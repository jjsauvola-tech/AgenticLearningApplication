"""ALA Windows launcher. The executable includes Python and document readers."""
import argparse
import json
import os
import subprocess
import sys
import webbrowser
import threading
import time
from pathlib import Path
from ala.server import AppServer

def launch_browser(url):
    if os.name=='nt':
        candidates=[Path(os.environ.get(k,''))/'Microsoft/Edge/Application/msedge.exe' for k in ('PROGRAMFILES(X86)','PROGRAMFILES','LOCALAPPDATA')]
        for p in candidates:
            if p.is_file():
                subprocess.Popen([str(p),'--app='+url],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                return
    webbrowser.open(url)

def main():
    args=argparse.ArgumentParser()
    args.add_argument('--data-dir')
    args.add_argument('--no-browser',action='store_true')
    args.add_argument('--port',type=int,default=0)
    args.add_argument('--runtime-file')
    opt=args.parse_args()
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).parent))
    data=Path(opt.data_dir or os.environ.get('ALA_DATA_DIR') or (Path(os.environ.get('LOCALAPPDATA',Path.home()))/'ALA'))
    from ala.lifecycle import AlreadyRunning, atomic_json
    import urllib.request
    data.mkdir(parents=True, exist_ok=True)
    instance_file = data/'instance.json'
    try:
        server=AppServer(data,root/'web',opt.port)
    except AlreadyRunning:
        # Another launcher may still be starting; never create a second writer.
        for attempt in range(50):
            try:
                runtime=json.loads(instance_file.read_text(encoding='utf-8'))
                base,token=runtime['url'].split('#',1)
                request=urllib.request.Request(base+'api/ping',headers={'X-ALA-Token':token})
                with urllib.request.urlopen(request,timeout=1) as response:
                    if response.status!=200: raise RuntimeError('not_ready')
                if opt.runtime_file: atomic_json(opt.runtime_file,runtime)
                if not opt.no_browser: launch_browser(runtime['url'])
                return
            except (OSError,ValueError,KeyError,RuntimeError):
                # The owner may be shutting down. Acquire only after its OS lock
                # is released; never trust a stale runtime file as ownership.
                try:
                    server=AppServer(data,root/'web',opt.port)
                    break
                except AlreadyRunning:
                    time.sleep(.1)
        else:
            raise RuntimeError('ALA is already running but unavailable. Existing data was not opened by a second process.')
    url='http://127.0.0.1:'+str(server.server_port)+'/#'+server.token
    runtime={'url':url,'port':server.server_port,'pid':os.getpid()}
    atomic_json(instance_file,runtime)
    if opt.runtime_file: atomic_json(opt.runtime_file,runtime)
    if not opt.no_browser: launch_browser(url)
    # Browser timers are throttled in background tabs and during sleep.
    # Only explicit shutdown ends the local service.
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()
