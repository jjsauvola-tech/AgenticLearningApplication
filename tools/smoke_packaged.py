"""Verify the packaged executable using synthetic, course-independent material."""
import argparse
import io
import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tests.test_core import docx_bytes,pptx_bytes,pdf_bytes

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('executable')
    parser.add_argument('--scratch')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='ALA test ä ',dir=args.scratch) as tmp:
        root=Path(tmp);runtime=root/'runtime.json';data=root/'Student data'
        process=subprocess.Popen([str(Path(args.executable).resolve()),'--no-browser','--data-dir',str(data),'--runtime-file',str(runtime)],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:
            for _ in range(100):
                if runtime.exists():break
                if process.poll() is not None:raise RuntimeError('Packaged process exited during startup')
                time.sleep(.1)
            config=json.loads(runtime.read_text(encoding='utf-8'))
            base=config['url'].split('/#')[0];token=config['url'].split('#')[1]
            def request(path,body=None,headers=None,raw=False):
                head={'X-ALA-Token':token,**(headers or {})}
                payload=body if raw else json.dumps(body).encode() if body is not None else None
                if body is not None and not raw:head['Content-Type']='application/json'
                with urllib.request.urlopen(urllib.request.Request(base+path,data=payload,headers=head),timeout=30) as r:
                    return r.read()
            state=json.loads(request('/api/state'));vid=state['active'];head={'X-ALA-Vault':vid}
            ids={}
            for ext,content in [('docx',docx_bytes()),('pptx',pptx_bytes()),('pdf',pdf_bytes())]:
                result=json.loads(request('/api/import',content,{**head,'X-Filename':'biology.'+ext,'X-Course':'Biology'},True));ids[ext]=result['id']
            request('/api/notes',{'document_id':ids['docx'],'page':1,'title':'Observation','body':'Persistent note'},head)
            request('/api/settings',{'language':'en','theme':'dark','fontSize':20,'showAssistant':False})
            goal=json.loads(request('/api/goals',{'course':'Biology','title':'Explain energy conversion','document_id':ids['docx'],'page':1},head))
            request('/api/quiz/questions',{'course':'Biology','question':'Which input supplies energy?',
                'choices':['Light','Darkness','Sound','Silence'],'correct':0,'explanation':'Light is the source input.',
                'document_id':ids['docx'],'page':1},head)
            quiz=json.loads(request('/api/quiz/start',{'course':'Biology','count':5},head))
            assert 'correct' not in quiz['questions'][0]
            graded=json.loads(request('/api/quiz/submit',{'id':quiz['id'],'answers':[0]},head))
            assert graded['score']==1
            card=json.loads(request('/api/cards',{'front':'Energy?','back':'Light'},head))
            request('/api/cards',{'id':card['id'],'front':'Input energy?','back':'Light energy'},head)
            png=request('/api/preview/'+ids['pdf']+'/1',headers=head)
            assert png.startswith(b'\x89PNG'), 'PDF rendering failed'
            backup=request('/api/backup',headers=head)
            assert backup.startswith(b'PK'), 'Backup failed'
            request('/api/shutdown',{})
            process.wait(timeout=10)
            runtime.unlink()
            process=subprocess.Popen([str(Path(args.executable).resolve()),'--no-browser','--data-dir',str(data),'--runtime-file',str(runtime)],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            for _ in range(100):
                if runtime.exists():break
                time.sleep(.1)
            config=json.loads(runtime.read_text(encoding='utf-8'));base=config['url'].split('/#')[0];token=config['url'].split('#')[1]
            state=json.loads(request('/api/state'))
            assert state['settings']['language']=='en' and state['settings']['fontSize']==20
            assert len(json.loads(request('/api/documents',headers=head)))==3
            assert json.loads(request('/api/notes',headers=head))[0]['body']=='Persistent note'
            assert json.loads(request('/api/goals',headers=head))[0]['id']==goal['id']
            assert json.loads(request('/api/quiz/history',headers=head))[0]['score']==1
            assert json.loads(request('/api/cards',headers=head))[0]['front']=='Input energy?'
            request('/api/shutdown',{});process.wait(timeout=10)
            print('PASS: executable, three imports, PDF, settings, notes, goals, quiz scoring, card editing, backup, restart, Unicode path')
        finally:
            if process.poll() is None:process.terminate();process.wait(timeout=10)

if __name__=='__main__':main()
