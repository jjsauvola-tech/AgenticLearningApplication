import json
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import uuid
from contextlib import closing
from pathlib import Path
from ala.storage import Store
from ala.inquiry import InquiryConflict
from ala.server import AppServer
from tests.test_core import docx_bytes

class InquiryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store(self.tmp.name);self.vid=self.store.config['active']
        self.did=self.store.add_document(self.vid,'biology.docx',docx_bytes(),'Biology')['id']
    def tearDown(self):self.tmp.cleanup()
    def start(self):
        body={'request_id':uuid.uuid4().hex,'document_id':self.did,'page':2}
        return self.store.start_inquiry(self.vid,body),body
    def turn(self,a,action='answer',text='My own research question'):
        body={'request_id':uuid.uuid4().hex,'attempt_id':a['id'],'expected_revision':a['revision'],'action':action,'text':text}
        return self.store.inquiry_turn(self.vid,body),body
    def test_complete_path_retains_original_and_support(self):
        a,_=self.start();a,_=self.turn(a,text='Original question')
        a,_=self.turn(a,'hint');a,_=self.turn(a,text='Evidence needed')
        a,_=self.turn(a,text='Revised question')
        with self.assertRaisesRegex(ValueError,'inquiry_help_unavailable'):self.turn(a,'hint')
        a,_=self.turn(a,text='New situation');a,_=self.turn(a,text='Reflection')
        self.assertEqual('complete',a['state']['phase'])
        self.assertEqual('Original question',a['state']['original'])
        self.assertEqual('Revised question',a['state']['revised'])
        self.assertEqual(1,len(a['state']['hints']))
        self.assertEqual(6,len(a['state']['events']))
        with self.assertRaisesRegex(ValueError,'inquiry_complete'):self.turn(a)
    def test_duplicate_start_and_turn_are_idempotent(self):
        a,body=self.start();self.assertEqual(a,self.store.start_inquiry(self.vid,body))
        updated,turn=self.turn(a);self.assertEqual(updated,self.store.inquiry_turn(self.vid,turn))
        self.assertEqual(1,len(self.store.inquiries(self.vid)))
        self.assertEqual(1,len(self.store.inquiry(self.vid,a['id'])['state']['events']))
        with self.assertRaisesRegex(InquiryConflict,'inquiry_request_conflict'):
            self.store.inquiry_turn(self.vid,{**turn,'text':'Different payload'})
    def test_concurrent_revision_and_vault_isolation(self):
        a,_=self.start();self.turn(a)
        with self.assertRaisesRegex(InquiryConflict,'inquiry_revision_conflict'):self.turn(a)
        other=self.store.create_vault('Separate')
        with self.assertRaisesRegex(ValueError,'inquiry_not_found'):self.store.inquiry(other,a['id'])
        with self.assertRaisesRegex(ValueError,'inquiry_not_found'):
            self.store.inquiry_turn(other,{'request_id':'other','attempt_id':a['id'],'expected_revision':1,'action':'hint'})
    def test_simultaneous_identical_writes_have_one_effect(self):
        a,_=self.start();body={'request_id':'same-request','attempt_id':a['id'],'expected_revision':0,'action':'answer','text':'Question'}
        values=[];errors=[]
        def call():
            try:values.append(self.store.inquiry_turn(self.vid,body))
            except Exception as e:errors.append(e)
        threads=[threading.Thread(target=call) for _ in range(4)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertEqual([],errors);self.assertEqual(4,len(values))
        self.assertTrue(all(r['revision']==1 for r in values))
    def test_resume_backup_and_migration_snapshot(self):
        a,_=self.start();a,_=self.turn(a)
        restarted=Store(self.tmp.name);self.assertEqual(a,restarted.inquiry(self.vid,a['id']))
        restored=restarted.restore(restarted.export(self.vid),'Restored')
        self.assertEqual(a,restarted.inquiry(restored,a['id']))
        path=self.store.vault_path(self.vid)/'learning.sqlite'
        with self.store.db(self.vid) as db:
            db.executescript('DROP TABLE inquiry_requests; DROP TABLE inquiry_attempts; PRAGMA user_version=2;')
        migrated=Store(self.tmp.name)
        self.assertEqual([],migrated.inquiries(self.vid))
        with closing(sqlite3.connect(str(path)+'.before-v3.bak')) as backup:
            self.assertEqual(2,backup.execute('PRAGMA user_version').fetchone()[0])
        self.assertEqual(1,len(migrated.documents(self.vid)))
    def test_support_bounds_and_return_to_practice(self):
        a,_=self.start()
        with self.assertRaisesRegex(ValueError,'inquiry_help_unavailable'):self.turn(a,'hint')
        a,_=self.turn(a)
        for _ in range(3):a,_=self.turn(a,'hint')
        with self.assertRaisesRegex(ValueError,'inquiry_hints_used'):self.turn(a,'hint')
        a,_=self.turn(a);a,_=self.turn(a)
        a,_=self.turn(a,'practice');self.assertEqual('revise',a['state']['phase'])
        self.assertEqual('My own research question',a['state']['original'])
    def test_invalid_source_and_empty_answer_do_not_advance(self):
        with self.assertRaisesRegex(ValueError,'source_insufficient'):
            self.store.start_inquiry(self.vid,{'request_id':'short','document_id':self.did,'page':1})
        a,_=self.start()
        with self.assertRaisesRegex(ValueError,'inquiry_answer_required'):self.turn(a,text=' ')
        self.assertEqual(0,self.store.inquiry(self.vid,a['id'])['revision'])

class InquiryHttpTests(unittest.TestCase):
    def test_token_required_and_conflict_is_409(self):
        with tempfile.TemporaryDirectory() as root:
            server=AppServer(root,Path(__file__).resolve().parents[1]/'web')
            thread=threading.Thread(target=server.serve_forever);thread.start()
            try:
                vid=server.store.config['active'];did=server.store.add_document(vid,'biology.docx',docx_bytes(),'Biology')['id']
                base='http://127.0.0.1:'+str(server.server_port)
                def post(path,body,token=True):
                    headers={'Content-Type':'application/json','X-ALA-Vault':vid}
                    if token:headers['X-ALA-Token']=server.token
                    with urllib.request.urlopen(urllib.request.Request(base+path,json.dumps(body).encode(),headers)) as r:return json.load(r)
                body={'request_id':'start','document_id':did,'page':2}
                with self.assertRaises(urllib.error.HTTPError) as denied:post('/api/inquiry/start',body,False)
                self.assertEqual(403,denied.exception.code)
                a=post('/api/inquiry/start',body)
                turn={'request_id':'step1','attempt_id':a['id'],'expected_revision':0,'action':'answer','text':'My own idea'}
                post('/api/tutor/turn',turn)
                with self.assertRaises(urllib.error.HTTPError) as conflict:post('/api/tutor/turn',{**turn,'request_id':'step2'})
                self.assertEqual(409,conflict.exception.code)
            finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
