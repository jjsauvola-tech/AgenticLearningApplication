import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from ala.storage import Store
from tests.test_core import docx_bytes

class LearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=Store(self.tmp.name);self.vid=self.store.config['active']
        self.did=self.store.add_document(self.vid,'biology.docx',docx_bytes(),'Biology')['id']
    def tearDown(self):self.tmp.cleanup()
    def goal(self,**changes):
        return {'course':'Biology','module':'Cells','title':'Explain photosynthesis','document_id':self.did,'page':1,**changes}
    def question(self,**changes):
        return {'course':'Biology','document_id':self.did,'page':1,'question':'What supplies energy?',
                'choices':['Light','Darkness','Sound','Silence'],'correct':0,'explanation':'The source identifies light as the input.',**changes}
    def test_dependencies_cycle_and_cross_course_rejected(self):
        first=self.store.save_goal(self.vid,self.goal())
        second=self.store.save_goal(self.vid,self.goal(title='Apply the concept',prerequisites=[first]))
        with self.assertRaisesRegex(ValueError,'goal_cycle'):
            self.store.save_goal(self.vid,self.goal(id=first,prerequisites=[second]))
        with self.assertRaisesRegex(ValueError,'invalid_prerequisite'):
            self.store.save_goal(self.vid,self.goal(course='History',document_id=None,prerequisites=[first]))
        self.assertFalse(next(g for g in self.store.goals(self.vid) if g['id']==second)['ready'])
        self.store.save_goal(self.vid,self.goal(id=first,status='complete'))
        self.assertTrue(next(g for g in self.store.goals(self.vid) if g['id']==second)['ready'])
    def test_invalid_source_and_vault_isolation(self):
        with self.assertRaisesRegex(ValueError,'source_course_mismatch'):
            self.store.save_goal(self.vid,self.goal(course='Chemistry'))
        with self.assertRaisesRegex(ValueError,'invalid_page'):
            self.store.save_goal(self.vid,self.goal(page=999))
        self.store.save_goal(self.vid,self.goal());self.store.save_question(self.vid,self.question())
        other=self.store.create_vault('Separate')
        self.assertEqual([],self.store.goals(other));self.assertEqual([],self.store.quiz_questions(other))
    def test_quiz_snapshot_and_idempotent_submission(self):
        qid=self.store.save_question(self.vid,self.question())
        session=self.store.start_quiz(self.vid,'Biology',5)
        self.assertNotIn('correct',session['questions'][0])
        self.assertNotIn('explanation',session['questions'][0])
        self.store.save_question(self.vid,self.question(id=qid,correct=1,explanation='Edited answer key'))
        result=self.store.submit_quiz(self.vid,session['id'],[0])
        self.assertEqual((1,1),(result['score'],result['total']))
        self.assertEqual(0,result['questions'][0]['correct'])
        self.assertEqual(1,self.store.submit_quiz(self.vid,session['id'],[1])['score'])
        second=self.store.start_quiz(self.vid,'Biology',1)
        self.assertEqual(0,self.store.submit_quiz(self.vid,second['id'],[0])['score'])
        self.assertEqual(2,len(self.store.quiz_history(self.vid)))
    def test_quiz_validation(self):
        with self.assertRaisesRegex(ValueError,'empty_question_bank'):self.store.start_quiz(self.vid)
        for changes in [{'choices':['same']*4},{'correct':True},{'correct':4},{'explanation':''}]:
            with self.assertRaises(ValueError):self.store.save_question(self.vid,self.question(**changes))
        self.store.save_question(self.vid,self.question())
        s=self.store.start_quiz(self.vid)
        with self.assertRaisesRegex(ValueError,'answer_all_questions'):self.store.submit_quiz(self.vid,s['id'],[])
        self.assertEqual([],self.store.quiz_history(self.vid))
    def test_card_edit_preserves_identity(self):
        card=self.store.save_card(self.vid,{'front':'Q','back':'A','document_id':self.did,'page':1})
        self.store.save_card(self.vid,{'id':card,'front':'Updated Q','back':'Updated A','document_id':self.did,'page':2})
        rows=self.store.rows(self.vid,'cards');self.assertEqual(1,len(rows))
        self.assertEqual(('Updated Q',2),(rows[0]['front'],rows[0]['page']))
    def test_backup_new_records_and_v1_migration(self):
        self.store.save_goal(self.vid,self.goal());self.store.save_question(self.vid,self.question())
        session=self.store.start_quiz(self.vid);self.store.submit_quiz(self.vid,session['id'],[0])
        restored=self.store.restore(self.store.export(self.vid),'Copy')
        self.assertEqual(1,len(self.store.goals(restored)))
        self.assertEqual(1,self.store.quiz_history(restored)[0]['score'])
        with self.store.db(self.vid) as db:
            for table in ('goals','quiz_questions','quiz_sessions'):db.execute('DROP TABLE '+table)
            db.execute('PRAGMA user_version=1')
        # Export an actual version-1 schema and verify restoration upgrades it.
        old_backup=self.store.export(self.vid)
        upgraded=self.store.restore(old_backup,'Version one')
        self.assertEqual(1,len(self.store.documents(upgraded)))
        self.assertEqual([],self.store.goals(upgraded))
        restarted=Store(self.tmp.name)
        self.assertEqual([],restarted.goals(self.vid))
        self.assertEqual(1,len(restarted.documents(self.vid)))

if __name__=='__main__':unittest.main()
