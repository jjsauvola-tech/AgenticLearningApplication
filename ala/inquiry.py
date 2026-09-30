"""Durable, source-linked inquiry practice. Prompts are scaffolds, not AI grading."""
import hashlib
import json
import uuid
from datetime import datetime, timezone

SCHEMA = '''
CREATE TABLE IF NOT EXISTS inquiry_attempts(
 id TEXT PRIMARY KEY, document_id TEXT NOT NULL, page INTEGER NOT NULL,
 source TEXT NOT NULL, revision INTEGER NOT NULL, state TEXT NOT NULL,
 created TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS inquiry_requests(
 request_id TEXT PRIMARY KEY, attempt_id TEXT NOT NULL, fingerprint TEXT NOT NULL, response TEXT NOT NULL);
PRAGMA user_version=3;
'''
PHASES = ('attempt','clarify','revise','transfer','reflect','complete')
FIELDS = {'attempt':'original','clarify':'clarification','revise':'revised','transfer':'transfer','reflect':'reflection'}

class InquiryConflict(ValueError):
    pass

def stamp():
    return datetime.now(timezone.utc).isoformat()

def request_key(body):
    value=body.get('request_id')
    if not isinstance(value,str) or not 1<=len(value)<=100 or not all(c.isalnum() or c in '-_' for c in value):
        raise ValueError('invalid_inquiry_request')
    fingerprint=hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return value,fingerprint

def unpack(row):
    result=dict(row)
    result['source']=json.loads(result['source'])
    result['state']=json.loads(result['state'])
    return result

def cached(db,key,fingerprint):
    row=db.execute('SELECT * FROM inquiry_requests WHERE request_id=?',(key,)).fetchone()
    if row:
        if row['fingerprint']!=fingerprint:raise InquiryConflict('inquiry_request_conflict')
        return json.loads(row['response'])

def remember(db,key,fingerprint,result):
    db.execute('INSERT INTO inquiry_requests VALUES(?,?,?,?)',
               (key,result['id'],fingerprint,json.dumps(result,ensure_ascii=False)))
    return result

class InquiryStore:
    def inquiries(self,vid):
        with self.db(vid) as db:
            return [unpack(r) for r in db.execute('SELECT * FROM inquiry_attempts ORDER BY updated DESC,id')]

    def inquiry(self,vid,aid):
        with self.db(vid) as db:
            row=db.execute('SELECT * FROM inquiry_attempts WHERE id=?',(aid,)).fetchone()
            if row is None:raise ValueError('inquiry_not_found')
            return unpack(row)

    def start_inquiry(self,vid,body):
        key,fingerprint=request_key(body)
        with self.db(vid) as db:
            db.execute('BEGIN IMMEDIATE')
            prior=cached(db,key,fingerprint)
            if prior:return prior
            did,page=body.get('document_id'),body.get('page')
            if not did:raise ValueError('source_required')
            self.anchor(vid,did,page)
            doc=self.document(vid,did);part=doc['pages'][page-1]
            if len(part['text'].strip())<40:raise ValueError('source_insufficient')
            source={'name':doc['name'],'title':part['title'],'sha256':doc['sha256'],
                    'course':doc['course'],'text':part['text'][:14000]}
            state={'phase':'attempt','original':'','clarification':'','revised':'','transfer':'',
                   'reflection':'','hints':[],'events':[]}
            now=stamp();aid=uuid.uuid4().hex
            db.execute('INSERT INTO inquiry_attempts VALUES(?,?,?,?,?,?,?,?)',
                       (aid,did,page,json.dumps(source,ensure_ascii=False),0,json.dumps(state),now,now))
            result=unpack(db.execute('SELECT * FROM inquiry_attempts WHERE id=?',(aid,)).fetchone())
            return remember(db,key,fingerprint,result)

    def inquiry_turn(self,vid,body):
        key,fingerprint=request_key(body)
        with self.db(vid) as db:
            db.execute('BEGIN IMMEDIATE')
            prior=cached(db,key,fingerprint)
            if prior:return prior
            row=db.execute('SELECT * FROM inquiry_attempts WHERE id=?',(body.get('attempt_id'),)).fetchone()
            if row is None:raise ValueError('inquiry_not_found')
            current=unpack(row)
            if type(body.get('expected_revision')) is not int or body['expected_revision']!=current['revision']:
                raise InquiryConflict('inquiry_revision_conflict')
            state=current['state'];phase=state['phase'];action=body.get('action')
            event={'phase':phase,'action':action,'created':stamp()}
            if action=='answer':
                text=body.get('text')
                if phase not in FIELDS:raise ValueError('inquiry_complete')
                if not isinstance(text,str) or not text.strip() or len(text)>20000:raise ValueError('inquiry_answer_required')
                state[FIELDS[phase]]=text.strip();event['text']=text.strip()
                state['phase']=PHASES[PHASES.index(phase)+1]
            elif action=='hint':
                if phase not in ('clarify','revise'):raise ValueError('inquiry_help_unavailable')
                level=1+sum(h['phase']==phase for h in state['hints'])
                if level>3:raise ValueError('inquiry_hints_used')
                hint={'phase':phase,'level':level,'created':stamp()}
                state['hints'].append(hint);event['level']=level
            elif action=='practice':
                if phase!='transfer':raise ValueError('invalid_inquiry_request')
                state['phase']='revise'
            else:raise ValueError('invalid_inquiry_request')
            state['events'].append(event)
            if len(state['events'])>200:raise ValueError('inquiry_limit')
            db.execute('UPDATE inquiry_attempts SET revision=revision+1,state=?,updated=? WHERE id=?',
                       (json.dumps(state,ensure_ascii=False),stamp(),current['id']))
            result=unpack(db.execute('SELECT * FROM inquiry_attempts WHERE id=?',(current['id'],)).fetchone())
            return remember(db,key,fingerprint,result)
