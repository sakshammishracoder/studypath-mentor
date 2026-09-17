"""Versioned, allowlisted state codec. Never serializes tokens, chats or form secrets."""
from datetime import date, time
from dataclasses import asdict
import json
from hashlib import sha256
from mentor import Result, analyze
from roadmaps import CATALOG
from study_tools import CONCEPTS

TARGETS = {e['id'] for e in CATALOG}


def fingerprint(payload):
    return sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def encode_state(state):
    plan = state.get('lab_plan')
    if plan:
        plan = dict(plan)
        plan['start'] = plan['start'].isoformat()
        plan['clock'] = plan['clock'].isoformat()
        plan['exam_date'] = plan['exam_date'].isoformat()
    data = {'version': 1, 'results': [dict(topic=r.topic, marks=float(r.marks), total=float(r.total)) for r in state.get('results', [])],
            'diagnostic_history': state.get('diagnostic_history', []),
            'lab_plan': plan, 'task_completions': sorted(state.get('task_completions', set())),
            'target_exam': state.get('target_exam', '10'),
            'ui_language': state.get('ui_language', 'English'),
            'regular_plan': {k: v.isoformat() if isinstance(v, (date, time)) else v
                for k, v in dict(days=state.get('regular_days', 7), minutes=state.get('regular_minutes', 120),
                    start=state.get('regular_start', date.today()), clock=state.get('regular_export_time', time(18))).items()}}
    if len(json.dumps(data, ensure_ascii=False).encode()) > 950000:
        raise ValueError('Progress is too large to save. Export a report and shorten diagnostic history.')
    return data


def decode_state(data):
    """Fail closed on incompatible cloud data; don't replace it with blank progress."""
    if not data:
        return {}
    if data.get('version') != 1:
        raise ValueError('This saved progress uses an unsupported format.')
    results = [Result(str(r['topic'])[:200], float(r['marks']), float(r['total'])) for r in data.get('results', [])]
    if results:
        results = analyze(results)
    if len(results) > 200:
        raise ValueError('Too many assessment topics.')
    exam = data.get('target_exam', '10')
    if exam not in TARGETS:
        raise ValueError('Unsupported study target.')
    history = data.get('diagnostic_history', [])
    if not isinstance(history, list) or len(history) > 5000:
        raise ValueError('Unsupported diagnostic history.')
    for row in history:
        if row.get('exam') not in TARGETS or row.get('topic') not in CONCEPTS or not 0 <= float(row.get('score', -1)) <= 100 or not isinstance(row.get('time'), str):
            raise ValueError('Invalid diagnostic record.')
    done = data.get('task_completions', [])
    if not isinstance(done, list) or len(done) > 10000 or not all(isinstance(k, str) and len(k) <= 100 for k in done):
        raise ValueError('Invalid completion list.')
    plan = data.get('lab_plan')
    if plan:
        plan = dict(plan)
        if plan.get('exam') not in TARGETS or not isinstance(plan.get('signature'), str) or not isinstance(plan.get('panic'), bool):
            raise ValueError('Invalid saved plan.')
        plan['start'] = date.fromisoformat(plan['start'])
        plan['clock'] = time.fromisoformat(plan['clock'])
        plan['exam_date'] = date.fromisoformat(plan['exam_date'])
        tasks = plan.get('tasks', [])
        if not tasks or len(tasks) > 2000:
            raise ValueError('Invalid plan size.')
        for r in tasks:
            if r.get('topic') not in {*CONCEPTS, 'break'} or not isinstance(r.get('day'), int) or not 0 <= r['day'] < 30 or not 0 <= r.get('start', -1) < 360 or not 0 < r.get('minutes', 0) <= 45:
                raise ValueError('Invalid plan task.')
            if not all(isinstance(r.get(k), str) and len(r[k]) <= 1500 for k in ['en', 'hi']):
                raise ValueError('Invalid task text.')
    prefs = data.get('regular_plan', {})
    days, minutes = prefs.get('days', 7), prefs.get('minutes', 120)
    if not isinstance(days, int) or not 1 <= days <= 30 or not isinstance(minutes, int) or not 30 <= minutes <= 360:
        raise ValueError('Invalid timetable preferences.')
    return {'results': results, 'diagnostic_history': history, 'lab_plan': plan,
            'task_completions': set(done), 'target_exam': exam,
            'ui_language': data.get('ui_language') if data.get('ui_language') in ('English', 'हिन्दी') else 'English',
            'regular_days': days, 'regular_minutes': minutes,
            'regular_start': date.fromisoformat(prefs.get('start', date.today().isoformat())),
            'regular_export_time': time.fromisoformat(prefs.get('clock', '18:00:00')),
            'chat_exam': exam, 'chat_topic': None, 'messages': []}
