import io
import json
import tempfile
import unittest
import urllib.error
import zipfile
from ala.storage import Store
from tests import test_core as core
from tests.test_core import docx_bytes


class GoalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(self.tmp.name)
        self.vid = self.store.config['active']

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, title, **values):
        return self.store.save_goal(self.vid, {'title': title, **values})

    def test_dependency_order_and_transitive_readiness(self):
        a = self.add('Foundation')
        b = self.add('Application', prerequisites=[a], status='complete')
        c = self.add('Synthesis', prerequisites=[b])
        goals = self.store.goals(self.vid)
        self.assertEqual([a,b,c], [g['id'] for g in goals])
        self.assertEqual([b], goals[2]['unmet'])
        self.add('Foundation revised', id=a, status='complete')
        self.assertEqual([], self.store.goals(self.vid)[2]['unmet'])
        self.add('Foundation revised', id=a, status='ongoing')
        self.assertEqual([b], self.store.goals(self.vid)[2]['unmet'])

    def test_cycle_rejected_without_partial_update(self):
        a = self.add('A')
        b = self.add('B', prerequisites=[a])
        c = self.add('C', prerequisites=[b])
        for prerequisites in ([a], [c]):
            with self.assertRaisesRegex(ValueError, 'goal_cycle'):
                self.add('Overwrite', id=a, prerequisites=prerequisites)
        self.assertEqual('A', self.store.goals(self.vid)[0]['title'])
        self.assertEqual([], self.store.goals(self.vid)[0]['prerequisites'])

    def test_isolation_and_missing_dependencies(self):
        a = self.add('A')
        other = self.store.create_vault('Other')
        self.assertEqual([], self.store.goals(other))
        with self.assertRaisesRegex(ValueError, 'goal_missing_prerequisite'):
            self.store.save_goal(other, {'title':'B', 'prerequisites':[a]})
        with self.assertRaisesRegex(ValueError, 'not_found'):
            self.store.save_goal(other, {'id':a, 'title':'Overwrite'})

    def test_delete_removes_links_only(self):
        a = self.add('A')
        b = self.add('B', prerequisites=[a])
        self.store.delete_goal(self.vid, a)
        goals = self.store.goals(self.vid)
        self.assertEqual([b], [g['id'] for g in goals])
        self.assertEqual([], goals[0]['prerequisites'])

    def test_source_restart_and_backup(self):
        doc = self.store.add_document(self.vid, 'biology.docx', docx_bytes(), 'Biology')
        a = self.add('Understand energy', document_id=doc['id'], page=1)
        self.add('Apply energy', prerequisites=[a])
        restarted = Store(self.tmp.name)
        self.assertEqual(doc['id'], restarted.goals(self.vid)[0]['document_id'])
        with tempfile.TemporaryDirectory() as folder:
            restored = Store(folder)
            vid = restored.restore(restarted.export(self.vid), 'Copy')
            self.assertEqual(restarted.goals(self.vid), restored.goals(vid))

    def test_migrate_existing_v1_and_restore_v1_backup(self):
        doc = self.store.add_document(self.vid, 'biology.docx', docx_bytes(), 'Biology')
        self.store.save_note(self.vid, {'document_id':doc['id'], 'page':1, 'body':'Keep me'})
        with self.store.db(self.vid) as db:
            db.executescript('DROP TABLE goal_dependencies; DROP TABLE goals; PRAGMA user_version=1;')
        # Construct an actual v1 archive before reopening the old database.
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w') as z:
            z.writestr('manifest.json', json.dumps({'schema':1,'name':'Old'}))
            z.write(self.store.vault_path(self.vid)/'learning.sqlite', 'learning.sqlite')
            original = self.store.original(self.vid, doc['id'])
            z.write(original, 'originals/'+original.name)
        restarted = Store(self.tmp.name)
        self.assertEqual([], restarted.goals(self.vid))
        self.assertEqual('Keep me', restarted.rows(self.vid, 'notes')[0]['body'])
        restored = restarted.restore(out.getvalue(), 'Old backup')
        self.assertEqual([], restarted.goals(restored))
        self.assertEqual('Keep me', restarted.rows(restored, 'notes')[0]['body'])
        restarted.save_goal(restored, {'title':'Works after migration'})
        with restarted.db(restored) as db:
            self.assertEqual(3, db.execute('PRAGMA user_version').fetchone()[0])

    def test_validation(self):
        for values in ({'title':''}, {'title':'x','prerequisites':'bad'},
                       {'title':'x','status':'certified'}, {'title':'x','page':1},
                       {'title':'x','document_id':'missing','page':1}):
            with self.assertRaises(ValueError):
                self.store.save_goal(self.vid, values)


class GoalHttpTests(unittest.TestCase):
    setUp = core.HttpTests.setUp
    tearDown = core.HttpTests.tearDown
    request = core.HttpTests.request
    def test_goal_api_lifecycle(self):
        with self.request('/api/goals', {'title':'Learn biology'}) as response:
            gid = json.load(response)['id']
        with self.request('/api/goals') as response:
            self.assertEqual(gid, json.load(response)[0]['id'])
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request('/api/goals', {'id':gid,'title':'Cycle','prerequisites':[gid]})
        self.assertEqual(400, error.exception.code)
        with self.request('/api/goals/delete', {'id':gid}):
            pass
        with self.request('/api/goals') as response:
            self.assertEqual([], json.load(response))

    def test_goal_api_authentication(self):
        for path, body in [('/api/goals',None),('/api/goals',{'title':'X'}),('/api/goals/delete',{'id':'x'})]:
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.request(path,body,auth=False)
            self.assertEqual(403,error.exception.code)


if __name__ == '__main__':
    unittest.main()
