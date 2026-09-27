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
    server=AppServer(data,root/'web',opt.port)
    url='http://127.0.0.1:'+str(server.server_port)+'/#'+server.token
    if opt.runtime_file:
        Path(opt.runtime_file).write_text(json.dumps({'url':url,'port':server.server_port,'pid':os.getpid()}),encoding='utf-8')
    if not opt.no_browser: launch_browser(url)
    if not opt.no_browser:
        def idle_shutdown():
            while True:
                time.sleep(20)
                if time.monotonic()-server.last_activity>180:
                    server.shutdown()
                    return
        threading.Thread(target=idle_shutdown,daemon=True).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__':
    main()
