"""Course-independent learning goals and immutable formative quiz attempts."""
import json
import secrets
import uuid
from datetime import datetime, timezone

SCHEMA = '''
CREATE TABLE IF NOT EXISTS goals(id TEXT PRIMARY KEY, course TEXT NOT NULL,
 module TEXT NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL,
 document_id TEXT, page INTEGER, status TEXT NOT NULL, prerequisites TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS quiz_questions(id TEXT PRIMARY KEY, course TEXT NOT NULL,
 document_id TEXT, page INTEGER, question TEXT NOT NULL, choices TEXT NOT NULL,
 correct INTEGER NOT NULL, explanation TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS quiz_sessions(id TEXT PRIMARY KEY, questions TEXT NOT NULL,
 answers TEXT, score INTEGER, total INTEGER NOT NULL, created TEXT NOT NULL, submitted TEXT);
PRAGMA user_version=2;
'''

def timestamp():
    return datetime.now(timezone.utc).isoformat()

def required(value, limit):
    value = str(value or '').strip()
    if not value or len(value) > limit:
        raise ValueError('invalid_learning_item')
    return value

class LearningFeatures:
    def goals(self, vid):
        with self.db(vid) as db:
            rows = [dict(r) for r in db.execute('SELECT * FROM goals ORDER BY course,module,updated,id')]
        statuses = {r['id']: r['status'] for r in rows}
        for row in rows:
            row['prerequisites'] = json.loads(row['prerequisites'])
            row['ready'] = all(statuses.get(p) == 'complete' for p in row['prerequisites'])
        return rows

    def save_goal(self, vid, item):
        gid = item.get('id') or uuid.uuid4().hex
        course = required(item.get('course'), 160)
        title = required(item.get('title'), 200)
        module = str(item.get('module', '')).strip()[:160]
        description = str(item.get('description', ''))[:10000]
        status = item.get('status', 'waiting')
        if status not in ('waiting', 'ongoing', 'complete', 'failed'):
            raise ValueError('invalid_learning_item')
        deps = item.get('prerequisites', [])
        if not isinstance(deps, list) or len(deps) > 100 or any(not isinstance(x, str) for x in deps):
            raise ValueError('invalid_prerequisite')
        deps = list(dict.fromkeys(deps))
        did, page = item.get('document_id'), item.get('page')
        self.anchor(vid, did, page)
        if did and self.document(vid, did)['course'] != course:
            raise ValueError('source_course_mismatch')
        with self.lock:
            goals = {r['id']: r for r in self.goals(vid)}
            if item.get('id') and gid not in goals:
                raise ValueError('not_found')
            if any(d == gid or d not in goals or goals[d]['course'] != course for d in deps):
                raise ValueError('invalid_prerequisite')
            if any(gid in g['prerequisites'] and g['course'] != course for g in goals.values()):
                raise ValueError('invalid_prerequisite')
            goals[gid] = {'prerequisites': deps, 'course': course}
            visiting, visited = set(), set()
            def visit(node):
                if node in visiting:
                    raise ValueError('goal_cycle')
                if node in visited:
                    return
                visiting.add(node)
                for parent in goals[node]['prerequisites']:
                    visit(parent)
                visiting.remove(node)
                visited.add(node)
            for node in goals:
                visit(node)
            with self.db(vid) as db:
                db.execute('''INSERT INTO goals VALUES(?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET course=excluded.course,module=excluded.module,
                    title=excluded.title,description=excluded.description,document_id=excluded.document_id,
                    page=excluded.page,status=excluded.status,prerequisites=excluded.prerequisites,updated=excluded.updated''',
                    (gid, course, module, title, description, did, page if did else None, status, json.dumps(deps), timestamp()))
        return gid

    def quiz_questions(self, vid):
        with self.db(vid) as db:
            rows = [dict(r) for r in db.execute('SELECT * FROM quiz_questions ORDER BY updated DESC,id')]
        for row in rows:
            row['choices'] = json.loads(row['choices'])
        return rows

    def save_question(self, vid, item):
        qid = item.get('id') or uuid.uuid4().hex
        course = required(item.get('course'), 160)
        question = required(item.get('question'), 4000)
        choices = item.get('choices')
        correct = item.get('correct')
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError('invalid_choices')
        choices = [required(x, 2000) for x in choices]
        if len(set(x.casefold() for x in choices)) != 4 or type(correct) is not int or not 0 <= correct < 4:
            raise ValueError('invalid_choices')
        explanation = required(item.get('explanation'), 8000)
        did, page = item.get('document_id'), item.get('page')
        self.anchor(vid, did, page)
        if did and self.document(vid, did)['course'] != course:
            raise ValueError('source_course_mismatch')
        with self.db(vid) as db:
            if item.get('id') and not db.execute('SELECT 1 FROM quiz_questions WHERE id=?', (qid,)).fetchone():
                raise ValueError('not_found')
            db.execute('''INSERT INTO quiz_questions VALUES(?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET course=excluded.course,document_id=excluded.document_id,page=excluded.page,
                question=excluded.question,choices=excluded.choices,correct=excluded.correct,
                explanation=excluded.explanation,updated=excluded.updated''',
                (qid, course, did, page if did else None, question, json.dumps(choices, ensure_ascii=False), correct, explanation, timestamp()))
        return qid

    def start_quiz(self, vid, course='', count=5):
        bank = [q for q in self.quiz_questions(vid) if not course or q['course'] == course]
        if not bank:
            raise ValueError('empty_question_bank')
        if type(count) is not int or not 1 <= count <= 50:
            raise ValueError('invalid_learning_item')
        secrets.SystemRandom().shuffle(bank)
        chosen = bank[:count]
        sid = uuid.uuid4().hex
        with self.db(vid) as db:
            db.execute('INSERT INTO quiz_sessions VALUES(?,?,NULL,NULL,?,?,NULL)',
                       (sid, json.dumps(chosen, ensure_ascii=False), len(chosen), timestamp()))
        return {'id': sid, 'questions': [{k: v for k, v in q.items() if k not in ('correct','explanation')} for q in chosen]}

    def submit_quiz(self, vid, sid, answers):
        with self.lock, self.db(vid) as db:
            row = db.execute('SELECT * FROM quiz_sessions WHERE id=?', (sid,)).fetchone()
            if row is None:
                raise ValueError('not_found')
            if row['submitted']:
                return self.quiz_result(dict(row))
            questions = json.loads(row['questions'])
            if not isinstance(answers, list) or len(answers) != len(questions) or any(type(x) is not int or not 0 <= x < 4 for x in answers):
                raise ValueError('answer_all_questions')
            score = sum(a == q['correct'] for a, q in zip(answers, questions))
            submitted = timestamp()
            db.execute('UPDATE quiz_sessions SET answers=?,score=?,submitted=? WHERE id=?',
                       (json.dumps(answers), score, submitted, sid))
            return self.quiz_result({**dict(row), 'answers': json.dumps(answers), 'score': score, 'submitted': submitted})

    @staticmethod
    def quiz_result(row):
        return {**row, 'questions': json.loads(row['questions']), 'answers': json.loads(row['answers'])}

    def quiz_history(self, vid):
        with self.db(vid) as db:
            return [self.quiz_result(dict(r)) for r in db.execute('SELECT * FROM quiz_sessions WHERE submitted IS NOT NULL ORDER BY submitted DESC')]

    def save_card(self, vid, item):
        cid = item.get('id') or uuid.uuid4().hex
        did, page = item.get('document_id'), item.get('page')
        self.anchor(vid, did, page)
        front, back = required(item.get('front'), 4000), required(item.get('back'), 12000)
        with self.db(vid) as db:
            if item.get('id') and not db.execute('SELECT 1 FROM cards WHERE id=?', (cid,)).fetchone():
                raise ValueError('not_found')
            db.execute('''INSERT INTO cards VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                document_id=excluded.document_id,page=excluded.page,front=excluded.front,back=excluded.back''',
                (cid, did, page if did else None, front, back, timestamp()))
        return cid
