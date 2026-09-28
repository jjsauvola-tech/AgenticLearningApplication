"""Opt-in ordered integration check using an external course, never committed data.

Run: python tools/verify_course.py PATH_TO_RELEASE --report data/course-check.json
All study mutations use a temporary, isolated vault. The Ollama fixture validates
protocol and source context only; it does not evaluate a real model's quality.
"""
import argparse
import hashlib
import json
import sys
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ala.server import AppServer
from tests.test_core import pdf_bytes
from pptx import Presentation


class Fixture(BaseHTTPRequestHandler):
    requests = []
    def log_message(self, *args): pass
    def do_GET(self):
        self.reply({'models':[{'name':'ala-test-fixture'}]})
    def do_POST(self):
        payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.requests.append(payload)
        self.reply({'message':{'content':'TEST FIXTURE ONLY: source-linked response [1].'}})
    def reply(self, value):
        payload=json.dumps(value).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(payload)))
        self.end_headers(); self.wfile.write(payload)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('course', type=Path)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--live-model',help='Optional installed local Ollama model; sends course context only to localhost')
    args=parser.parse_args()
    files=sorted(p for p in args.course.rglob('*') if p.is_file() and p.suffix.lower() in ('.docx','.pptx','.pdf') and not p.name.startswith('~$'))
    assert files, 'No supported course materials'
    report={'checks':[], 'formats':dict(Counter(p.suffix for p in files)), 'model_quality':'not evaluated; deterministic fixture only'}
    def record(name, **details):
        report['checks'].append({'check':name,'result':'PASS',**details})
        print('PASS: '+name,flush=True)
    with tempfile.TemporaryDirectory(prefix='ALA course verification ') as folder:
        server=None; thread=None; fixture=None; fixture_thread=None
        def start():
            nonlocal server,thread
            server=AppServer(folder,Path(__file__).resolve().parents[1]/'web')
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        def stop():
            server.shutdown();server.server_close();thread.join()
        def request(path,body=None,vid=None,raw=False,headers=None):
            head={'X-ALA-Token':server.token,**(headers or {})}
            if vid: head['X-ALA-Vault']=vid
            if body is not None and not raw: head['Content-Type']='application/json'
            data=body if raw else None if body is None else json.dumps(body).encode()
            req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=data,headers=head)
            with urllib.request.urlopen(req,timeout=150) as resp:
                payload=resp.read()
                return json.loads(payload) if 'application/json' in resp.headers['Content-Type'] else payload
        def reject(path,body,code):
            try: request(path,body,vid)
            except urllib.error.HTTPError as exc:
                assert exc.code==code,(path,exc.code)
                return json.load(exc)
            raise AssertionError('Expected failure: '+path)
        try:
            start()
            state=request('/api/bootstrap');vid=state['active']
            for path in ('/','/app.js','/goals.js','/imports.js','/style.css'):
                assert request(path)
            record('01 Startup, session and all UI assets')
            imported=[]
            for path in files:
                course='External course / '+path.parent.relative_to(args.course).as_posix()
                head={'X-Filename':urllib.parse.quote(path.name),'X-Course':urllib.parse.quote(course)}
                result=request('/api/import',path.read_bytes(),vid,True,head)
                assert not result['duplicate'],path.name
                imported.append((path,result['id'],head))
            assert len(request('/api/documents',vid=vid))==len(files)
            record('02 Recursive course import',documents=len(files))
            slides=0; sections=0; notes=0
            for path,did,head in imported:
                doc=request('/api/document/'+did,vid=vid)
                assert doc['pages']
                assert hashlib.sha256(request('/api/original/'+did,vid=vid)).hexdigest()==hashlib.sha256(path.read_bytes()).hexdigest()
                sections+=len(doc['pages'])
                if path.suffix.lower()=='.pptx':
                    deck=Presentation(path)
                    assert len(doc['pages'])==len(deck.slides)
                    slides+=len(deck.slides)
                    for page,slide in zip(doc['pages'],deck.slides):
                        expected=slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ''
                        assert page['notes']==expected
                        notes+=bool(expected)
            record('03 All material sections, PPTX slide counts, speaker notes and original hashes',sections=sections,slides=slides,slides_with_notes=notes)
            for path,did,head in imported:
                again=request('/api/import',path.read_bytes(),vid,True,head)
                assert again['duplicate'] and again['id']==did
            assert len(request('/api/documents',vid=vid))==len(files)
            record('04 Full repeat import without duplicates',duplicates=len(files))
            path,did,head=next((x for x in imported if x[0].suffix.lower()=='.pptx'),imported[0])
            doc=request('/api/document/'+did,vid=vid)
            import re
            term=next(w for w in re.findall(r'\w+',doc['pages'][0]['text']) if len(w)>4)
            hits=request('/api/search?q='+urllib.parse.quote(term),vid=vid)
            assert hits
            for hit in hits:
                target=request('/api/document/'+hit['document_id'],vid=vid)
                assert 1<=hit['page']<=len(target['pages'])
            record('05 Search and source anchors',hits=len(hits))
            anchor={'document_id':did,'page':1}
            nid=request('/api/notes',{**anchor,'title':'QA note','body':'First revision'},vid)['id']
            request('/api/notes',{**anchor,'id':nid,'title':'QA note edited','body':'Second revision'},vid)
            assert request('/api/notes',vid=vid)[0]['body']=='Second revision'
            for status in ('complete','ongoing','waiting','complete'):
                request('/api/progress',{**anchor,'status':status},vid)
                assert request('/api/document/'+did,vid=vid)['progress']['1']==status
            request('/api/cards',{**anchor,'front':'QA: What counts as evidence?','back':'Observed behaviour checked against requirements.'},vid)
            request('/api/attempts',{**anchor,'question':'QA: Explain acceptance.','answer':'Observed behaviour supports acceptance.','feedback':'Test self-review.'},vid)
            request('/api/external',{**anchor,'text':'QA external answer, deliberately unverified.'},vid)
            for table in ('cards','attempts','messages'): assert len(request('/api/'+table,vid=vid))==1
            assert request('/api/messages',vid=vid)[0]['role']=='external'
            record('06 Note editing, study states, cards, practice and external answer')
            a=request('/api/goals',{**anchor,'title':'Foundation'},vid)['id']
            b=request('/api/goals',{'title':'Application','prerequisites':[a]},vid)['id']
            assert request('/api/goals',vid=vid)[1]['unmet']==[a]
            request('/api/goals',{**anchor,'id':a,'title':'Foundation','status':'complete'},vid)
            assert request('/api/goals',vid=vid)[1]['unmet']==[]
            assert reject('/api/goals',{'id':a,'title':'Cycle','prerequisites':[b]},400)['error']=='goal_cycle'
            request('/api/goals/delete',{'id':b},vid)
            assert len(request('/api/goals',vid=vid))==1
            record('07 Goal prerequisites, cycle rejection and deletion')
            original_settings=request('/api/state')['settings']
            changed={**original_settings,'language':'en','theme':'dark','fontSize':20,'density':'compact','showFlow':False,'showAssistant':False,'showNotes':True,'reduceMotion':True,'flowWidth':300,'assistantWidth':400}
            assert request('/api/settings',changed)==changed
            stop();start()
            assert request('/api/state')['settings']==changed
            assert request('/api/notes',vid=vid)[0]['body']=='Second revision'
            assert request('/api/document/'+did,vid=vid)['progress']['1']=='complete'
            record('08 All appearance settings and restart persistence')
            backup=request('/api/backup',vid=vid)
            restored=request('/api/restore',backup,raw=True,headers={'X-Vault-Name':'QA-restored'})['id']
            assert len(request('/api/documents',vid=restored))==len(files)
            for table in ('notes','cards','attempts','messages','goals'):
                assert request('/api/'+table,vid=restored)==request('/api/'+table,vid=vid)
            for path,original_id,_ in imported:
                assert hashlib.sha256(request('/api/original/'+original_id,vid=restored)).hexdigest()==hashlib.sha256(path.read_bytes()).hexdigest()
            other=request('/api/vaults',{'name':'Empty isolation check'})['id']
            for table in ('documents','notes','cards','attempts','messages','goals'): assert request('/api/'+table,vid=other)==[]
            request('/api/switch',{'id':vid})
            assert request('/api/state')['active']==vid
            record('09 Backup, restore of all originals and records, empty vault isolation and switching',backup_bytes=len(backup))
            assert reject('/api/chat',{**anchor,'text':'Explain the source.'},400)['error']=='model_not_configured'
            fixture=ThreadingHTTPServer(('127.0.0.1',0),Fixture)
            fixture_thread=threading.Thread(target=fixture.serve_forever,daemon=True);fixture_thread.start()
            request('/api/settings',{'model':'ala-test-fixture','ollamaUrl':'http://127.0.0.1:'+str(fixture.server_port)})
            assert request('/api/model-test',{})['models']==['ala-test-fixture']
            for prompt,scope in [('Explain the source.',anchor),('Create one practice question.',anchor),('Give formative feedback.',anchor),('Explain '+term,{'document_id':None,'page':None})]:
                answer=request('/api/chat',{**scope,'text':prompt},vid)
                assert answer['sources'] and answer['answer'].startswith('TEST FIXTURE')
                assert 'SOURCE MATERIAL' in Fixture.requests[-1]['messages'][0]['content']
            fixture.shutdown();fixture.server_close();fixture_thread.join();fixture=None
            assert reject('/api/chat',{**anchor,'text':'Explain'},503)['error']=='model_unavailable'
            request('/api/settings',original_settings)
            record('10 Missing model, model discovery, contextual chat, question/feedback requests, whole-vault retrieval and unavailable service',adapter='deterministic local fixture; not real AI')
            pdf=request('/api/import',pdf_bytes(),vid,True,{'X-Filename':'synthetic-check.pdf'})
            assert request('/api/preview/'+pdf['id']+'/1',vid=vid).startswith(b'\x89PNG')
            record('11 Supplemental synthetic PDF import and rendering',reason='Release folder contains no PDFs')
            if args.live_model:
                request('/api/settings',{'model':args.live_model,'ollamaUrl':'http://127.0.0.1:11434','language':'fi'})
                available=request('/api/model-test',{})['models']
                assert args.live_model in available
                report['live_model']={'model':args.live_model,'samples':[]}
                for sample_index,prompt in enumerate(('Selitä aineiston tärkein oppimistavoite suomeksi. Viittaa lähteeseen [1].',
                               'Laadi yksi harjoituskysymys tästä aineistokohdasta. Älä anna vastausta.',
                               'Anna oppimista tukeva palaute. Kysymys: Miten ohjelmiston hyväksyntä perustellaan? Vastaus: Se perustellaan havaittavalla toiminnalla ja riippumattomalla vaatimusten tarkistuksella.')):
                    answer=request('/api/chat',{**anchor,'text':prompt,'task':('chat','question','feedback')[sample_index]},vid)
                    assert answer['answer'].strip() and answer['sources']
                    report['live_model']['samples'].append({'prompt':prompt,**answer})
                    print('PASS: live model sample '+str(len(report['live_model']['samples'])),flush=True)
                report['model_quality']='Three live local responses collected for manual inspection; not comprehensive validation'
                request('/api/settings',original_settings)
                record('12 Live local model: explanation, practice question and formative feedback',model=args.live_model)
            request('/api/shutdown',{})
            thread.join(timeout=5);assert not thread.is_alive();server.server_close();server=None
            record('13 Clean application shutdown')
        finally:
            if server: stop()
            if fixture: fixture.shutdown();fixture.server_close();fixture_thread.join()
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2),encoding='utf-8')


if __name__=='__main__': main()
