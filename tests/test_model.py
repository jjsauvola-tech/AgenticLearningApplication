import json
import threading
import unittest
import urllib.error
from http.server import ThreadingHTTPServer
from tests import test_core as core
from tools.verify_course import Fixture


class ModelTests(unittest.TestCase):
    request=core.HttpTests.request
    def setUp(self):
        core.HttpTests.setUp(self)
        self.fixture=ThreadingHTTPServer(('127.0.0.1',0),Fixture)
        self.worker=threading.Thread(target=self.fixture.serve_forever,daemon=True)
        self.worker.start()
        self.server.store.settings({'model':'ala-test-fixture','ollamaUrl':'http://127.0.0.1:'+str(self.fixture.server_port)})
    def tearDown(self):
        self.fixture.shutdown();self.fixture.server_close();self.worker.join()
        core.HttpTests.tearDown(self)
    def test_discovery_and_answer_with_thinking_disabled(self):
        with self.request('/api/model-test',{}) as response:
            self.assertEqual(['ala-test-fixture'],json.load(response)['models'])
        with self.request('/api/chat',{'text':'Explain'}) as response:
            self.assertTrue(json.load(response)['answer'])
        self.assertIs(False,Fixture.requests[-1]['think'])
    def test_empty_answer_is_not_saved_as_success(self):
        from unittest.mock import patch
        original=Fixture.reply
        def empty(handler,value):
            return original(handler,{'message':{'content':''}})
        with patch.object(Fixture,'reply',empty):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.request('/api/chat',{'text':'Explain'})
            self.assertEqual(502,error.exception.code)
            self.assertEqual('model_empty_response',json.load(error.exception)['error'])
        rows=self.server.store.rows(self.server.store.config['active'],'messages')
        self.assertFalse(any(r['role']=='assistant' for r in rows))

    def test_gpt_oss_uses_supported_reasoning_level(self):
        self.server.store.settings({'model':'gpt-oss:20b'})
        with self.request('/api/chat',{'text':'Explain'}) as response:self.assertTrue(json.load(response)['answer'])
        self.assertEqual('low',Fixture.requests[-1]['think'])
        self.assertGreater(Fixture.requests[-1]['options']['num_predict'],1500)

    def test_expert_role_is_bound_to_valid_source(self):
        store=self.server.store;vid=store.config['active']
        did=store.add_document(vid,'source.docx',core.docx_bytes(),'Module')['id']
        with self.request('/api/chat',{'text':'Explain','expert':True,'document_id':did,'page':2}) as response:
            self.assertEqual(2,json.load(response)['sources'][0]['page'])
        self.assertIn('subject-specific tutor',Fixture.requests[-1]['messages'][0]['content'])
        with self.request('/api/topics') as response:
            topics=json.load(response)
        self.assertTrue(any(p['document_id']==did and p['page']==2 for p in topics))

    def test_answer_sources_survive_restart_and_backup(self):
        from ala.storage import Store
        store=self.server.store
        vid=store.config['active']
        did=store.add_document(vid,'source.docx',core.docx_bytes(),'Test')['id']
        with self.request('/api/chat',{'text':'Explain','document_id':did,'page':1}) as response:
            answer=json.load(response)
        self.assertEqual(did,answer['sources'][0]['document_id'])
        restarted=Store(self.tmp.name)
        self.assertEqual(answer['sources'],restarted.rows(vid,'messages')[0]['sources'])
        restored=restarted.restore(restarted.export(None),'Restored sources')
        self.assertEqual(answer['sources'],restarted.rows(restored,'messages')[0]['sources'])

    def test_practice_uses_stable_source_without_chat_history(self):
        store=self.server.store;vid=store.config['active']
        did=store.add_document(vid,'source.docx',core.docx_bytes(),'Test')['id']
        for task in ('chat','question','feedback'):
            with self.request('/api/chat',{'text':'Explain photosynthesis','document_id':did,'page':2,'task':task}) as response:
                answer=json.load(response)
            if task!='chat':
                self.assertEqual(1,len(answer['sources']))
                self.assertEqual(2,answer['sources'][0]['page'])
                self.assertEqual(['system','user'],[m['role'] for m in Fixture.requests[-1]['messages']])

    def test_invalid_question_retried_then_rejected_without_saving_answer(self):
        from unittest.mock import patch
        store=self.server.store;vid=store.config['active']
        did=store.add_document(vid,'source.docx',core.docx_bytes(),'Test')['id']
        original=Fixture.reply
        before=len(Fixture.requests)
        def invalid(handler,value):
            return original(handler,{'message':{'content':'Question? Answer: leaked.'}})
        with patch.object(Fixture,'reply',invalid):
            with self.assertRaises(urllib.error.HTTPError) as error:
                self.request('/api/chat',{'text':'Ask a question','document_id':did,'page':2,'task':'question'})
            self.assertEqual(502,error.exception.code)
            self.assertEqual('model_invalid_practice',json.load(error.exception)['error'])
        self.assertEqual(2,len(Fixture.requests)-before)
        self.assertFalse(any(r['role']=='assistant' for r in store.rows(vid,'messages')))

    def test_heading_only_source_rejected_before_model_request(self):
        store=self.server.store;vid=store.config['active']
        did=store.add_document(vid,'source.docx',core.docx_bytes(),'Test')['id']
        before=len(Fixture.requests)
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request('/api/chat',{'text':'Ask a question','document_id':did,'page':1,'task':'question'})
        self.assertEqual('source_insufficient',json.load(error.exception)['error'])
        self.assertEqual(before,len(Fixture.requests))

    def test_invalid_question_can_be_repaired_once(self):
        from unittest.mock import patch
        store=self.server.store;vid=store.config['active']
        did=store.add_document(vid,'source.docx',core.docx_bytes(),'Test')['id']
        original=Fixture.reply
        calls=[]
        def first_invalid(handler,value):
            calls.append(value)
            if len(calls)==1:
                value={'message':{'content':'Question? Answer: do not show this.'}}
            return original(handler,value)
        with patch.object(Fixture,'reply',first_invalid):
            with self.request('/api/chat',{'text':'Ask a question','document_id':did,'page':2,'task':'question'}) as response:
                answer=json.load(response)['answer']
        self.assertEqual('What does the selected source explain?',answer)
        self.assertEqual(2,len(calls))
        assistants=[r for r in store.rows(vid,'messages') if r['role']=='assistant']
        self.assertEqual([answer],[r['body'] for r in assistants])


if __name__=='__main__':unittest.main()
