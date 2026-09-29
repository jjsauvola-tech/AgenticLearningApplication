import hashlib
import json
import os
import re
import sqlite3
import threading
import uuid
import zipfile
import tempfile
import shutil
from contextlib import contextmanager, closing
from datetime import datetime, timezone
from pathlib import Path
from .importers import extract

def now():
    return datetime.now(timezone.utc).isoformat()

DEFAULTS = {'language':'fi', 'theme':'light', 'fontSize':16, 'density':'comfortable',
            'showFlow':True, 'showAssistant':True, 'flowWidth':250, 'assistantWidth':330,
            'showNotes':False, 'reduceMotion':False, 'model':'', 'ollamaUrl':'http://127.0.0.1:11434'}

SCHEMA = '''
CREATE TABLE IF NOT EXISTS documents(
 id TEXT PRIMARY KEY,name TEXT NOT NULL,format TEXT NOT NULL,sha256 TEXT UNIQUE NOT NULL,
 course TEXT NOT NULL,created TEXT NOT NULL,pages TEXT NOT NULL,warnings TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS notes(
 id TEXT PRIMARY KEY,document_id TEXT,page INTEGER,title TEXT NOT NULL,body TEXT NOT NULL,updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS progress(document_id TEXT,page INTEGER,status TEXT,PRIMARY KEY(document_id,page));
CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,document_id TEXT,page INTEGER,role TEXT,body TEXT,created TEXT);
CREATE TABLE IF NOT EXISTS cards(id TEXT PRIMARY KEY,document_id TEXT,page INTEGER,front TEXT,back TEXT,created TEXT);
CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY,document_id TEXT,page INTEGER,question TEXT,answer TEXT,feedback TEXT,created TEXT);
PRAGMA user_version=1;
'''

GOAL_SCHEMA = '''
CREATE TABLE IF NOT EXISTS goals(
 id TEXT PRIMARY KEY,title TEXT NOT NULL,description TEXT NOT NULL,
 document_id TEXT,page INTEGER,status TEXT NOT NULL,updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS goal_dependencies(
 goal_id TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
 prerequisite_id TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
 PRIMARY KEY(goal_id,prerequisite_id));
PRAGMA user_version=2;
'''

MESSAGE_SOURCE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS message_sources(
 message_id TEXT PRIMARY KEY REFERENCES messages(id) ON DELETE CASCADE,
 sources TEXT NOT NULL);
'''

def migrate_goals(path):
    with closing(sqlite3.connect(path)) as db:
        version = db.execute('PRAGMA user_version').fetchone()[0]
        if version not in (1, 2):
            raise ValueError('unsupported_database')
        if version == 1:
            db.executescript('BEGIN IMMEDIATE;\n' + GOAL_SCHEMA + '\nCOMMIT;')
        # Additive metadata: older schema-2 backups simply have no source links.
        db.executescript(MESSAGE_SOURCE_SCHEMA)

class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.config_path = self.root/'settings.json'
        if self.config_path.exists():
            self.config = json.loads(self.config_path.read_text(encoding='utf-8'))
        else:
            self.config = {'settings':dict(DEFAULTS), 'vaults':[], 'active':None}
        self.config['settings'] = {**DEFAULTS, **self.config['settings']}
        if not self.config['vaults']:
            self.create_vault('Oma oppiminen')
        for vault in self.config['vaults']:
            migrate_goals(self.vault_path(vault['id'])/'learning.sqlite')

    def save_config(self):
        from .lifecycle import atomic_json
        atomic_json(self.config_path,self.config)

    def vault_path(self, vid=None):
        vid = vid or self.config['active']
        if vid not in [v['id'] for v in self.config['vaults']]:
            raise ValueError('unknown_vault')
        return self.root/'vaults'/vid

    @contextmanager
    def db(self, vid=None):
        con = sqlite3.connect(self.vault_path(vid)/'learning.sqlite', timeout=30)
        con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON')
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def create_vault(self, name):
        name = str(name).strip()[:100]
        if not name:
            raise ValueError('name_required')
        with self.lock:
            vid = uuid.uuid4().hex
            path = self.root/'vaults'/vid
            (path/'originals').mkdir(parents=True)
            con = sqlite3.connect(path/'learning.sqlite')
            con.executescript(SCHEMA + GOAL_SCHEMA + MESSAGE_SOURCE_SCHEMA)
            con.close()
            previous = json.loads(json.dumps(self.config))
            self.config['vaults'].append({'id':vid,'name':name,'created':now()})
            self.config['active'] = vid
            try: self.save_config()
            except BaseException:
                self.config = previous
                raise
            return vid

    def switch(self, vid):
        with self.lock:
            self.vault_path(vid)
            previous = self.config['active']
            self.config['active'] = vid
            try: self.save_config()
            except BaseException:
                self.config['active'] = previous
                raise

    def settings(self, values):
        with self.lock:
            new = {**self.config['settings'], **{k:v for k,v in values.items() if k in DEFAULTS}}
            if new['language'] not in ('fi','en') or new['theme'] not in ('light','dark','system'):
                raise ValueError('invalid_settings')
            if new['density'] not in ('comfortable','compact'):
                raise ValueError('invalid_settings')
            for key, lo, hi in [('fontSize',14,24),('flowWidth',190,380),('assistantWidth',260,480)]:
                new[key] = max(lo,min(hi,int(new[key])))
            for key in ('showFlow','showAssistant','showNotes','reduceMotion'):
                if not isinstance(new[key],bool): raise ValueError('invalid_settings')
            from urllib.parse import urlparse
            url = urlparse(new['ollamaUrl'])
            if url.scheme != 'http' or url.hostname not in ('localhost','127.0.0.1','::1') or url.username or url.password or url.query or url.fragment:
                raise ValueError('local_endpoint_required')
            new['ollamaUrl'] = new['ollamaUrl'].rstrip('/')
            new['model'] = str(new['model'])[:200]
            previous = self.config['settings']
            self.config['settings'] = new
            try: self.save_config()
            except BaseException:
                self.config['settings'] = previous
                raise
            return new

    def state(self):
        with self.lock:
            return json.loads(json.dumps(self.config))

    def documents(self, vid):
        with self.db(vid) as db:
            rows = db.execute('SELECT * FROM documents ORDER BY course,name').fetchall()
            progress = db.execute('SELECT * FROM progress').fetchall()
        return [{**{k:r[k] for k in ['id','name','format','course','created']},'count':len(json.loads(r['pages'])),
                 'warnings':json.loads(r['warnings']),
                 'completed':sum(p['document_id']==r['id'] and p['status']=='complete' for p in progress)} for r in rows]

    def document(self, vid, did):
        with self.db(vid) as db:
            r = db.execute('SELECT * FROM documents WHERE id=?',(did,)).fetchone()
            if r is None: raise ValueError('not_found')
            progress = {str(p['page']):p['status'] for p in db.execute('SELECT * FROM progress WHERE document_id=?',(did,))}
        result = dict(r)
        result['pages'] = json.loads(r['pages'])
        result['warnings'] = json.loads(r['warnings'])
        result['progress'] = progress
        return result

    def original(self, vid, did):
        doc = self.document(vid, did)
        return self.vault_path(vid)/'originals'/(doc['sha256']+'.'+doc['format'])

    def add_document(self, vid, name, data, course, parser=extract):
        self.vault_path(vid)
        name = Path(name.replace('\\','/')).name[:200]
        digest = hashlib.sha256(data).hexdigest()
        with self.db(vid) as db:
            existing = db.execute('SELECT id FROM documents WHERE sha256=?',(digest,)).fetchone()
        if existing: return {'id':existing['id'],'duplicate':True}
        parsed = parser(name, data)
        did = uuid.uuid4().hex
        with self.lock:
            with self.db(vid) as db:
                existing = db.execute('SELECT id FROM documents WHERE sha256=?',(digest,)).fetchone()
                if existing: return {'id':existing['id'],'duplicate':True}
                path = self.vault_path(vid)/'originals'/(digest+'.'+parsed['format'])
                tmp = path.with_suffix('.tmp')
                tmp.write_bytes(data)
                os.replace(tmp, path)
                db.execute('INSERT INTO documents VALUES (?,?,?,?,?,?,?,?)',
                    (did,name,parsed['format'],digest,str(course).strip()[:160] or 'Omat materiaalit',now(),
                     json.dumps(parsed['pages'],ensure_ascii=False),json.dumps(parsed['warnings'])))
        return {'id':did,'duplicate':False,'count':len(parsed['pages']),'warnings':parsed['warnings']}

    def anchor(self, vid, did, page):
        if not did: return
        doc = self.document(vid,did)
        if not isinstance(page,int) or not 1 <= page <= len(doc['pages']): raise ValueError('invalid_page')

    def save_note(self, vid, values):
        did, page = values.get('document_id'), values.get('page')
        self.anchor(vid,did,page)
        nid = values.get('id') or uuid.uuid4().hex
        body = str(values.get('body',''))[:200000]
        title = str(values.get('title','')).strip()[:200] or 'Note'
        with self.db(vid) as db:
            db.execute('INSERT INTO notes VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,body=excluded.body,updated=excluded.updated',
                       (nid,did,page,title,body,now()))
        return nid

    def rows(self, vid, table):
        if table not in ('notes','messages','cards','attempts'): raise ValueError('invalid_table')
        with self.db(vid) as db:
            if table == 'messages':
                return [{**dict(r),'sources':json.loads(r['sources'] or '[]')} for r in db.execute(
                    'SELECT m.*, s.sources FROM messages m LEFT JOIN message_sources s ON m.id=s.message_id ORDER BY m.rowid DESC')]
            return [dict(r) for r in db.execute('SELECT * FROM '+table+' ORDER BY rowid DESC')]

    def goals(self, vid):
        with self.db(vid) as db:
            goals = [dict(r) for r in db.execute('SELECT * FROM goals ORDER BY rowid')]
            edges = db.execute('SELECT * FROM goal_dependencies').fetchall()
        by_id = {g['id']: g for g in goals}
        for goal in goals:
            goal['prerequisites'] = [e['prerequisite_id'] for e in edges if e['goal_id'] == goal['id']]
        ordered, pending, done = [], list(goals), set()
        while pending:
            batch = [g for g in pending if set(g['prerequisites']) <= done]
            if not batch:
                raise ValueError('goal_cycle')
            for goal in batch:
                goal['unmet'] = [p for p in goal['prerequisites']
                                 if by_id[p]['status'] != 'complete' or by_id[p]['unmet']]
                ordered.append(goal)
                done.add(goal['id'])
                pending.remove(goal)
        return ordered

    def save_goal(self, vid, values):
        title, description = values.get('title', ''), values.get('description', '')
        prerequisites, status = values.get('prerequisites', []), values.get('status', 'waiting')
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ValueError('goal_title_required')
        if not isinstance(description, str) or len(description) > 12000:
            raise ValueError('invalid_goal')
        if status not in ('waiting', 'ongoing', 'complete'):
            raise ValueError('invalid_goal')
        if not isinstance(prerequisites, list) or any(not isinstance(p, str) for p in prerequisites):
            raise ValueError('invalid_goal')
        gid = values.get('id') or uuid.uuid4().hex
        if not isinstance(gid, str):
            raise ValueError('invalid_goal')
        did, page = values.get('document_id'), values.get('page')
        if (did is None) != (page is None) or (did is not None and (not isinstance(did, str) or not did)):
            raise ValueError('invalid_goal')
        self.anchor(vid, did, page)
        with self.lock, self.db(vid) as db:
            graph = {r['id']: set() for r in db.execute('SELECT id FROM goals')}
            if values.get('id') and gid not in graph:
                raise ValueError('not_found')
            if any(p not in graph for p in prerequisites):
                raise ValueError('goal_missing_prerequisite')
            for edge in db.execute('SELECT * FROM goal_dependencies'):
                graph[edge['goal_id']].add(edge['prerequisite_id'])
            graph[gid] = set(prerequisites)
            pending, seen = list(prerequisites), set()
            while pending:
                current = pending.pop()
                if current == gid:
                    raise ValueError('goal_cycle')
                if current not in seen:
                    seen.add(current)
                    pending.extend(graph[current])
            db.execute('INSERT INTO goals VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
                       'title=excluded.title,description=excluded.description,document_id=excluded.document_id,'
                       'page=excluded.page,status=excluded.status,updated=excluded.updated',
                       (gid, title.strip(), description, did, page, status, now()))
            db.execute('DELETE FROM goal_dependencies WHERE goal_id=?', (gid,))
            db.executemany('INSERT INTO goal_dependencies VALUES(?,?)', [(gid, p) for p in set(prerequisites)])
        return gid

    def delete_goal(self, vid, gid):
        with self.lock, self.db(vid) as db:
            if not db.execute('DELETE FROM goals WHERE id=?', (gid,)).rowcount:
                raise ValueError('not_found')

    def search(self, vid, query, did=None):
        terms = re.findall(r'\w+', query.lower())[:12]
        if not terms: return []
        hits = []
        for d in self.documents(vid):
            if did and d['id'] != did: continue
            doc = self.document(vid,d['id'])
            for p in doc['pages']:
                text = p['text'].lower()
                score = sum(text.count(t) for t in terms)
                if score:
                    pos = min((text.find(t) for t in terms if t in text),default=0)
                    hits.append({'document_id':d['id'],'name':d['name'],'page':p['number'],
                                 'title':p['title'],'score':score,'excerpt':p['text'][max(0,pos-100):pos+380]})
        return sorted(hits,key=lambda h:-h['score'])[:30]

    def export(self, vid):
        vid = vid or self.config['active']
        path = self.vault_path(vid)
        with tempfile.TemporaryDirectory(dir=self.root) as tmp:
            dbfile = Path(tmp)/'learning.sqlite'
            with self.db(vid) as src:
                dst = sqlite3.connect(dbfile)
                src.backup(dst)
                dst.close()
            out = Path(tmp)/'backup.zip'
            with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
                z.writestr('manifest.json',json.dumps({'schema':2,'created':now(),'name':next(v['name'] for v in self.config['vaults'] if v['id']==vid)}))
                z.write(dbfile,'learning.sqlite')
                for p in (path/'originals').glob('*'):
                    if p.is_file() and p.suffix != '.tmp': z.write(p,'originals/'+p.name)
            return out.read_bytes()

    def restore(self, data, name):
        import io
        from .importers import MAX_EXPANDED
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            infos=z.infolist()
            if len(infos)>20000 or sum(i.file_size for i in infos)>MAX_EXPANDED*4: raise ValueError('archive_limit')
            names={i.filename for i in infos}
            if not {'manifest.json','learning.sqlite'} <= names: raise ValueError('invalid_backup')
            manifest=json.loads(z.read('manifest.json'))
            if manifest.get('schema') not in (1,2): raise ValueError('invalid_backup')
            for item in infos:
                if item.filename in ('manifest.json','learning.sqlite'): continue
                if not re.fullmatch(r'originals/[a-f0-9]{64}\.(pdf|docx|pptx)',item.filename): raise ValueError('invalid_backup')
            with tempfile.TemporaryDirectory(dir=self.root) as tmp:
                stage=Path(tmp)
                z.extractall(stage)
                con=sqlite3.connect('file:'+str(stage/'learning.sqlite')+'?mode=ro',uri=True)
                try:
                    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise ValueError('invalid_backup')
                    required={'documents','notes','progress','messages','cards','attempts'}
                    tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    version=con.execute('PRAGMA user_version').fetchone()[0]
                    if version==2: required |= {'goals','goal_dependencies'}
                    if not required <= tables or version!=manifest['schema']: raise ValueError('invalid_backup')
                    if con.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0]: raise ValueError('invalid_backup')
                    for sha,fmt,pages in con.execute('SELECT sha256,format,pages FROM documents'):
                        if not re.fullmatch(r'[a-f0-9]{64}',sha) or fmt not in ('pdf','docx','pptx'): raise ValueError('invalid_backup')
                        p=stage/'originals'/(sha+'.'+fmt)
                        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha: raise ValueError('invalid_backup')
                        if not isinstance(json.loads(pages),list): raise ValueError('invalid_backup')
                finally: con.close()
                migrate_goals(stage/'learning.sqlite')
                # Complete all file work before exposing a restored vault in the registry.
                with self.lock:
                    vid=uuid.uuid4().hex
                    target=self.root/'vaults'/vid
                    prepared=stage/'ready'
                    prepared.mkdir()
                    shutil.copyfile(stage/'learning.sqlite',prepared/'learning.sqlite')
                    if (stage/'originals').exists(): shutil.copytree(stage/'originals',prepared/'originals')
                    else: (prepared/'originals').mkdir()
                    os.replace(prepared,target)
                    previous = json.loads(json.dumps(self.config))
                    self.config['vaults'].append({'id':vid,'name':str(name or manifest.get('name','Restored')).strip()[:100] or 'Restored','created':now()})
                    self.config['active']=vid
                    try: self.save_config()
                    except BaseException:
                        self.config = previous
                        raise
                    return vid
