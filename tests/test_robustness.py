import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch
from ala.lifecycle import AlreadyRunning
from ala.server import AppServer
from ala.storage import Store
from ala.workers import extract_isolated,run_worker
from tests import test_core as core
from tests.test_core import docx_bytes,pdf_bytes

ROOT=Path(__file__).resolve().parents[1]

class RobustHttpTests(core.HttpTests):
    def test_new_tab_recovers_write_token_from_authenticated_cookie(self):
        with self.request('/api/bootstrap') as response:
            cookie=response.headers['Set-Cookie'].split(';')[0]
        for old_token in ('','expired-tab-token'):
            request=urllib.request.Request(self.base+'/api/bootstrap',headers={'Cookie':cookie,'X-ALA-Token':old_token})
            with urllib.request.urlopen(request) as response:token=json.load(response)['sessionToken']
            self.assertEqual(self.server.token,token)
            request=urllib.request.Request(self.base+'/api/notes',data=b'{"title":"New tab","body":"saved"}',headers={'X-ALA-Token':token,'Content-Type':'application/json'})
            with urllib.request.urlopen(request) as response:self.assertEqual(200,response.status)

    def test_session_recovery_does_not_allow_unauthenticated_or_cross_origin_access(self):
        cookie=self.server.cookie_name+'='+self.server.token
        for headers in ({},{'Cookie':self.server.cookie_name+'=expired'},{'Cookie':cookie,'Origin':'https://malicious.example'},{'Cookie':cookie,'Host':'malicious.example'}):
            request=urllib.request.Request(self.base+'/api/bootstrap',headers=headers)
            with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(request)
            self.assertEqual(403,error.exception.code)
        request=urllib.request.Request(self.base+'/api/notes',data=b'{}',headers={'Cookie':cookie,'Content-Type':'application/json'})
        with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(request)
        self.assertEqual(403,error.exception.code)

    def test_second_writer_rejected_and_lock_released(self):
        with self.assertRaises(AlreadyRunning): AppServer(self.tmp.name,ROOT/'web')

    def test_other_port_cookie_cannot_replace_session(self):
        with self.request('/api/bootstrap') as response:
            cookie=response.headers['Set-Cookie'].split(';')[0]
        request=urllib.request.Request(self.base+'/api/state',headers={'Cookie':cookie+'; ala_session_1=wrong; ala_session=wrong'})
        with urllib.request.urlopen(request) as response:self.assertEqual(200,response.status)

    def test_busy_worker_does_not_block_ping_or_notes(self):
        self.server.heavy_slots.acquire();self.server.heavy_slots.acquire()
        try:
            with self.assertRaises(urllib.error.HTTPError) as error:self.request('/api/chat',{'text':'hello'})
            self.assertEqual(503,error.exception.code)
            with self.request('/api/ping') as response:self.assertEqual(200,response.status)
            with self.request('/api/notes',{'title':'while busy','body':'retained'}) as response:self.assertIn('id',json.load(response))
        finally:self.server.heavy_slots.release();self.server.heavy_slots.release()

    def test_failure_logged_without_private_exception_text(self):
        with patch.object(self.server.store,'documents',side_effect=RuntimeError('PRIVATE TEST CONTENT')):
            with self.assertRaises(urllib.error.HTTPError) as error:self.request('/api/documents')
        payload=json.load(error.exception)
        log=(Path(self.tmp.name)/'diagnostics.log').read_text()
        self.assertIn(payload['event_id'],log)
        self.assertIn('RuntimeError',log)
        self.assertNotIn('PRIVATE TEST CONTENT',log)
        with self.request('/api/ping') as response:self.assertEqual(200,response.status)

    def test_ui_asset_snapshot_is_complete(self):
        for name in ('app.js','goals.js','imports.js','chat.js','recovery.js','agents.js','agents.css'):
            with self.request('/'+name) as response:self.assertTrue(response.read())
        self.assertIn('recovery.js',self.server.assets['index.html'].decode())

    def test_agent_images_are_served_without_exposing_project_files(self):
        with self.request('/assets/svla-faces/base.png') as response:
            self.assertEqual('image/png',response.headers['Content-Type'])
            self.assertTrue(response.read().startswith(b'\x89PNG'))
        for path in ('/../ala/server.py','/docs/SVLA_ASSET_PROVENANCE.json','/assets/missing.png'):
            with self.assertRaises(urllib.error.HTTPError) as error:self.request(path)
            self.assertIn(error.exception.code,(403,404))

    def test_default_vault_is_captured_before_another_tab_switches(self):
        store=self.server.store
        initial=store.state()['active']
        other=store.create_vault('Another tab')
        store.switch(initial)
        save=store.save_note
        def concurrent_switch(vault,body):
            store.switch(other)
            return save(vault,body)
        with patch.object(store,'save_note',side_effect=concurrent_switch):
            with self.request('/api/notes',{'title':'Anchored request','body':'Keep in original vault'}) as response:
                self.assertEqual(200,response.status)
        self.assertEqual(1,len(store.rows(initial,'notes')))
        self.assertEqual(0,len(store.rows(other,'notes')))

class WorkerTests(unittest.TestCase):
    def test_isolated_import_and_corruption(self):
        self.assertEqual('docx',extract_isolated('lesson.docx',docx_bytes())['format'])
        with self.assertRaises(ValueError):extract_isolated('broken.docx',b'broken')

    def test_isolated_pdf_and_timeout_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'test.pdf';path.write_bytes(pdf_bytes())
            with self.assertRaisesRegex(ValueError,'worker_timeout'):run_worker('pdf',path,1,timeout=0)
            self.assertTrue(run_worker('pdf',path,1).startswith(b'\x89PNG'))

    def test_settings_write_failure_keeps_previous_state(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Store(folder);before=store.state()
            with patch.object(store,'save_config',side_effect=OSError('disk full')):
                with self.assertRaises(OSError):store.settings({'language':'en'})
            self.assertEqual(before,store.state())
            self.assertEqual(before,Store(folder).state())

class LauncherTests(unittest.TestCase):
    def test_concurrent_launch_and_crash_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);processes=[]
            try:
                for i in range(10):
                    processes.append(subprocess.Popen([sys.executable,str(ROOT/'main.py'),'--no-browser','--data-dir',str(folder),'--runtime-file',str(folder/f'launch-{i}.json')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE))
                deadline=time.monotonic()+30
                while time.monotonic()<deadline and len(list(folder.glob('launch-*.json')))<10:time.sleep(.1)
                runtimes=[json.loads(p.read_text()) for p in folder.glob('launch-*.json')]
                self.assertEqual(10,len(runtimes))
                self.assertEqual(1,len({r['pid'] for r in runtimes}))
                if sys.platform=='win32':
                    launcher=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
                        str(ROOT/'scripts/start.ps1'),'-NoBrowser','-DataDir',str(folder)],
                        capture_output=True,text=True,timeout=20,env=dict(os.environ))
                    self.assertEqual(0,launcher.returncode,launcher.stderr)
                    self.assertIn('is running',launcher.stdout)
                owner=next(p for p in processes if p.pid==runtimes[0]['pid'])
                owner.kill();owner.wait(5)
                successor=subprocess.Popen([sys.executable,str(ROOT/'main.py'),'--no-browser','--data-dir',str(folder),'--runtime-file',str(folder/'recovered.json')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
                processes.append(successor)
                deadline=time.monotonic()+15
                while time.monotonic()<deadline and not (folder/'recovered.json').exists():time.sleep(.1)
                recovered=json.loads((folder/'recovered.json').read_text())
                self.assertEqual(successor.pid,recovered['pid'])
                self.assertEqual(runtimes[0]['url'],recovered['url'])
                base,token=recovered['url'].split('#')
                with urllib.request.urlopen(urllib.request.Request(base+'api/ping',headers={'X-ALA-Token':token})) as response:self.assertEqual(200,response.status)
                with urllib.request.urlopen(urllib.request.Request(base+'api/shutdown',data=b'{}',headers={'X-ALA-Token':token})) as response:self.assertEqual(200,response.status)
                successor.wait(10)
            finally:
                for process in processes:
                    if process.poll() is None:process.kill()
                    process.wait(5)
                    if process.stderr:process.stderr.close()

if __name__=='__main__':unittest.main()
