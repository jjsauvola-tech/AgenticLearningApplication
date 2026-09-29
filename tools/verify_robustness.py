"""Exercise real release imports and mixed HTTP load in an isolated vault."""
import argparse,concurrent.futures,hashlib,json,sys,tempfile,threading,time,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ala.server import AppServer


def main():
    args=argparse.ArgumentParser();args.add_argument('release',type=Path);args.add_argument('--seconds',type=int,default=60);args.add_argument('--report',type=Path,required=True);opt=args.parse_args()
    files=sorted(p for p in opt.release.rglob('*') if p.suffix.lower() in ('.docx','.pptx','.pdf'))
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with tempfile.TemporaryDirectory() as folder:
        server=AppServer(folder,Path(__file__).resolve().parents[1]/'web');thread=threading.Thread(target=server.serve_forever);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        headers={'X-ALA-Token':server.token}
        def request(path,data=None,extra=None):
            req=urllib.request.Request(base+path,data=data,headers={**headers,**(extra or {})})
            with urllib.request.urlopen(req,timeout=120) as response:return response.read()
        try:
            from urllib.parse import quote
            for index,p in enumerate(files):
                request('/api/import',p.read_bytes(),{'X-Filename':quote(p.name),'X-Course':'NFR'})
                print(f'Imported {index+1}/{len(files)}',flush=True)
            docs=json.loads(request('/api/documents'));assert len(docs)==len(files)
            deadline=time.monotonic()+opt.seconds
            def exercise(worker):
                times=[];count=0
                while time.monotonic()<deadline:
                    start=time.monotonic()
                    if count%5==0:
                        data=json.dumps({'title':f'Load test {worker}/{count}','body':'Retained under concurrent load'}).encode()
                        request('/api/notes',data,{'Content-Type':'application/json'})
                    else:request('/api/document/'+docs[count%len(docs)]['id'])
                    times.append(time.monotonic()-start);count+=1
                    time.sleep(.02)
                return times
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                samples=sum(list(pool.map(exercise,range(4))),[])
            samples.sort()
            notes=json.loads(request('/api/notes'))
            backup=request('/api/backup')
            restored=server.store.restore(backup,'NFR restored')
            assert len(server.store.documents(restored))==len(docs)
            assert len(server.store.rows(restored,'notes'))==len(notes)
            assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest for p,digest in hashes.items())
            report={'documents':len(docs),'seconds':opt.seconds,'requests':len(samples),'p95_ms':round(samples[int(.95*(len(samples)-1))]*1000,2),'max_ms':round(max(samples)*1000,2),'notes_restored':len(notes),'source_hashes_unchanged':True,'backup_restore':'passed'}
            opt.report.parent.mkdir(parents=True,exist_ok=True);opt.report.write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
        finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':main()
