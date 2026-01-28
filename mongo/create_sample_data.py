import pymongo
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from faker import Faker
import datetime
import random

MONGO_URI = "mongodb://admin:admin@localhost:27017/"
DB_NAME = "company_db"
fake = Faker('en_US')

def to_datetime(date_obj):
    if date_obj is None:
        return None
    if isinstance(date_obj, datetime.datetime):
        return date_obj
    if isinstance(date_obj, datetime.date):
        return datetime.datetime.combine(date_obj, datetime.time.min)
    return date_obj

VALIDATOR_DEPARTMENT = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "name", "address", "fk_head_employee"],
        "properties": {
            "_id": {"bsonType": "int"},
            "name": {"bsonType": "string"},
            "address": {"bsonType": ["string", "null"]},
            "fk_head_employee": {"bsonType": ["int", "null"]}
        }
    }
}

VALIDATOR_EMPLOYEE = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "login", "user_password", "permission_type", "name", "surname", "telephone", "fk_department", "absences", "competences", "project_assignments"],
        "properties": {
            "_id": {"bsonType": "int"},
            "login": {"bsonType": "string"},
            "user_password": {"bsonType": "string"},
            "permission_type": {"bsonType": "int"},
            "name": {"bsonType": "string"},
            "surname": {"bsonType": "string"},
            "telephone": {"bsonType": ["string", "null"]},
            "fk_department": {"bsonType": ["int", "null"]},
            "absences": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["_id", "date_from", "date_to", "absence_type", "paid"],
                    "properties": {
                        "_id": {"bsonType": "int"},
                        "date_from": {"bsonType": "date"},
                        "date_to": {"bsonType": ["date", "null"]},
                        "absence_type": {"bsonType": "string"},
                        "paid": {"bsonType": "bool"}
                    }
                }
            },
            "competences": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["_id", "skill_type", "level"],
                    "properties": {
                        "_id": {"bsonType": "int"},
                        "skill_type": {"bsonType": "string"},
                        "level": {"bsonType": "int"}
                    }
                }
            },
            "project_assignments": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["_id", "fk_project", "project_role", "date_start", "date_end", "work_schedules", "monthly_scores"],
                    "properties": {
                        "_id": {"bsonType": "int"},
                        "fk_project": {"bsonType": "int"},
                        "project_role": {"bsonType": ["string", "null"]},
                        "date_start": {"bsonType": "date"},
                        "date_end": {"bsonType": ["date", "null"]},
                        "work_schedules": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["weekday", "time_from", "time_to"],
                                "properties": {
                                    "weekday": {"bsonType": "int"},
                                    "time_from": {"bsonType": "string"},
                                    "time_to": {"bsonType": "string"}
                                }
                            }
                        },
                        "monthly_scores": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["_id", "score", "date_of"],
                                "properties": {
                                    "_id": {"bsonType": "int"},
                                    "score": {"bsonType": "int"},
                                    "date_of": {"bsonType": "date"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

VALIDATOR_LOCATION = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "name", "address", "terminals"],
        "properties": {
            "_id": {"bsonType": "int"},
            "name": {"bsonType": ["string", "null"]},
            "address": {"bsonType": "string"},
            "terminals": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["_id"],
                    "properties": {
                        "_id": {"bsonType": "int"}
                    }
                }
            }
        }
    }
}

VALIDATOR_PROJECT = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "name", "fk_overseer_employee", "location", "vacancies"],
        "properties": {
            "_id": {"bsonType": "int"},
            "name": {"bsonType": "string"},
            "fk_overseer_employee": {"bsonType": ["int", "null"]},
            "location": {
                "bsonType": ["object", "null"],
                "required": ["_id", "name", "address"],
                "properties": {
                    "_id": {"bsonType": "int"},
                    "name": {"bsonType": ["string", "null"]},
                    "address": {"bsonType": "string"}
                }
            },
            "vacancies": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["_id", "fk_employee", "vacancy_skills"],
                    "properties": {
                        "_id": {"bsonType": "int"},
                        "fk_employee": {"bsonType": ["int", "null"]},
                        "vacancy_skills": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["skill_type", "level"],
                                "properties": {
                                    "skill_type": {"bsonType": "string"},
                                    "level": {"bsonType": "int"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

VALIDATOR_WORK_SESSION = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "time_from", "time_to", "fk_employee", "fk_start_terminal", "fk_end_terminal", "fk_project"],
        "properties": {
            "_id": {"bsonType": "int"},
            "time_from": {"bsonType": "date"},
            "time_to": {"bsonType": ["date", "null"]},
            "fk_employee": {"bsonType": "int"},
            "fk_start_terminal": {"bsonType": "int"},
            "fk_end_terminal": {"bsonType": ["int", "null"]},
            "fk_project": {"bsonType": "int"}
        }
    }
}

table_counts = {
    'employee': 1000,
    'department': 6,
    'location': 7,
    'terminal': 14,
    'project': 200,
    'project_assignment': 80,
    'competence': 5000,
}

class IdGenerator:
    def __init__(self):
        self.counters = {
            'terminal': 1,
            'competence': 1,
            'assignment': 1,
            'absence': 1,
            'score': 1,
            'session': 1,
            'vacancy': 1
        }

    def get_next(self, entity_type):
        val = self.counters[entity_type]
        self.counters[entity_type] += 1
        return val

SKILL_TYPES = {
    i: name for i, name in enumerate([
        'C++', 'Python', 'Java', 'Rust', 'C', 'JavaScript', 'React', 'Postgres',
        'English', 'Spanish', 'German', 'Kotlin', 'Swift', 'Swing',
        'Project management', 'Linux', 'Cloud computing', 'Machine Learning',
        'Data Engineering', 'Graphic Design'
    ], 1)
}

PROJECT_ROLES = {
    i: name for i, name in enumerate([
        'Project Manager', 'Technical Lead', 'Front-End Developer', 'Back-End Developer',
        'Full-Stack Developer', 'Mobile App Developer', 'DevOps Engineer', 'Cloud Engineer',
        'Software Architect', 'Database Developer', 'QA Engineer', 'Security Tester',
        'Performance Tester', 'UI Designer', 'Data Engineer', 'ML Engineer',
        'Network Engineer', 'System Administrator', 'Business Analyst', 'Data Analyst'
    ], 1)
}

ABSENCE_TYPES = {
    1: {'name': 'Vacation', 'paid': True},
    2: {'name': 'Sick Leave', 'paid': True},
    3: {'name': 'Personal Leave', 'paid': False},
    4: {'name': 'Parental Leave', 'paid': True},
    5: {'name': 'Absence', 'paid': False}
}

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def create_collection_safe(db, name, validator):
    if name in db.list_collection_names():
        db.drop_collection(name)

    try:
        db.create_collection(name, validator=validator)
    except CollectionInvalid:
        pass

def generate_work_sessions_mongo(id_gen, employee_id, project_id, schedule_weekday,
                               time_from, time_to, start_date, end_date, terminal_pool):
    sessions = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() == schedule_weekday:
            is_complete = random.random() < 0.95

            dt_from = pd.Timestamp.combine(current_date, time_from).to_pydatetime()
            dt_to = pd.Timestamp.combine(current_date, time_to).to_pydatetime()

            session = {
                '_id': id_gen.get_next('session'),
                'time_from': dt_from,
                'time_to': dt_to if is_complete else None,
                'fk_employee': int(employee_id),
                'fk_start_terminal': int(random.choice(terminal_pool)),
                'fk_end_terminal': int(random.choice(terminal_pool)) if is_complete else None,
                'fk_project': int(project_id)
            }
            sessions.append(session)

        current_date += datetime.timedelta(days=1)

    return sessions

def generate_monthly_scores_mongo(id_gen, start_date, end_date):
    scores = []
    current_date = start_date.replace(day=1)

    while current_date <= end_date:
        scores.append({
            '_id': id_gen.get_next('score'),
            'score': int(random.randint(0, 9)),
            'date_of': to_datetime(current_date)
        })

        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    return scores

def generate_schedules_mongo(num_days=None):
    if num_days is None:
        num_days = random.randint(3, 5)

    schedules = []
    selected_weekdays = random.sample(range(7), num_days)

    for weekday in selected_weekdays:
        hour_from = random.randint(7, 9)
        hour_to = random.randint(15, 18)

        time_from = datetime.time(hour=hour_from, minute=random.choice([0, 30]))
        time_to = datetime.time(hour=hour_to, minute=random.choice([0, 30]))

        schedules.append({
            'weekday': int(weekday),
            'time_from': time_from.strftime("%H:%M:%S"),
            'time_to': time_to.strftime("%H:%M:%S"),
            '_obj_time_from': time_from,
            '_obj_time_to': time_to
        })
    return schedules

def generate_absences_mongo(id_gen, employee_id, start_date, end_date):
    absences = []
    num_absences = random.choices([0, 1, 2, 3], weights=[0.4, 0.35, 0.2, 0.05])[0]

    for _ in range(num_absences):
        days_in_assignment = (end_date - start_date).days
        if days_in_assignment <= 0: continue

        absence_start_offset = random.randint(0, max(0, days_in_assignment - 1))
        absence_start = start_date + datetime.timedelta(days=absence_start_offset)

        type_id = random.choice(list(ABSENCE_TYPES.keys()))
        type_data = ABSENCE_TYPES[type_id]

        if type_id == 1: duration = random.randint(3, 14)
        elif type_id == 2: duration = random.randint(1, 7)
        elif type_id == 3: duration = random.randint(1, 3)
        elif type_id == 4: duration = random.randint(30, 180)
        else: duration = random.randint(1, 5)

        absence_end = absence_start + datetime.timedelta(days=duration)
        if absence_end > end_date: absence_end = end_date

        days_to_end = (end_date - absence_start).days
        if days_to_end < 30 and random.random() < 0.1:
            absence_end = None

        absences.append({
            '_id': id_gen.get_next('absence'),
            'date_from': to_datetime(absence_start),
            'date_to': to_datetime(absence_end) if absence_end else None,
            'absence_type': type_data['name'],
            'paid': type_data['paid']
        })

    return absences

def populate_mongo():
    db = get_db()
    id_gen = IdGenerator()

    db.client.drop_database(DB_NAME)

    create_collection_safe(db, 'locations', VALIDATOR_LOCATION)

    locations_data = []
    location_map = {}
    terminal_pool = []

    for loc_id in range(1, table_counts['location'] + 1):
        loc_terminals = []
        for _ in range(2):
            term_id = id_gen.get_next('terminal')
            terminal_pool.append(term_id)
            loc_terminals.append({'_id': term_id})

        loc_doc = {
            '_id': loc_id,
            'name': random.choice(['Headquarters', 'The Cheeser', 'The Second Dust', 'Bridge', 'Basement']) if random.random() > 0.3 else None,
            'address': fake.street_address(),
            'terminals': loc_terminals
        }
        locations_data.append(loc_doc)
        location_map[loc_id] = {'_id': loc_id, 'name': loc_doc['name'], 'address': loc_doc['address']}

    db.locations.insert_many(locations_data)

    create_collection_safe(db, 'employees', VALIDATOR_EMPLOYEE)

    employees_data = {}
    employee_ids = list(range(1, table_counts['employee'] + 1))

    for emp_id in employee_ids:
        employees_data[emp_id] = {
            '_id': emp_id,
            'login': fake.first_name() + str(random.randint(1, 100)),
            'user_password': fake.pystr(min_chars=40, max_chars=80),
            'permission_type': int(random.randint(0, 2)),
            'name': fake.first_name(),
            'surname': fake.last_name(),
            'telephone': fake.unique.bothify(text="#########") if random.random() > 0.05 else None,
            'fk_department': int(random.randint(1, table_counts['department'])),
            'absences': [],
            'competences': [],
            'project_assignments': []
        }

    for emp_id, emp_doc in employees_data.items():
        num_comps = random.randint(0, 5)
        skill_keys = random.sample(list(SKILL_TYPES.keys()), num_comps)
        for skill_id in skill_keys:
            emp_doc['competences'].append({
                '_id': id_gen.get_next('competence'),
                'skill_type': SKILL_TYPES[skill_id],
                'level': int(random.randint(1, 5))
            })

    create_collection_safe(db, 'projects', VALIDATOR_PROJECT)

    projects_data = []
    all_sessions = {eid: [] for eid in employee_ids}

    for proj_id in range(1, table_counts['project'] + 1):
        project_start = fake.date_between(start_date=datetime.date(2022, 11, 5), end_date=datetime.date(2023, 6, 1))
        project_end = fake.date_between(start_date=datetime.date(2023, 6, 2), end_date=datetime.date(2024, 11, 5))

        loc_id = random.choice(list(location_map.keys())) if random.random() > 0.05 else None
        loc_embed = location_map[loc_id] if loc_id else None

        vacancies = []
        num_vacancies = random.choices([0, 1, 2, 3], weights=[0.5, 0.3, 0.15, 0.05])[0]

        for _ in range(num_vacancies):
            is_filled = random.random() > 0.3

            target_emp_id = None
            req_skills = []

            if is_filled:
                target_emp_id = random.choice(employee_ids)
                target_emp = employees_data[target_emp_id]

                if target_emp['competences']:
                    comp = random.choice(target_emp['competences'])
                    req_skills.append({
                        "skill_type": comp['skill_type'],
                        "level": max(1, comp['level'] - 1)
                    })
                else:
                    target_emp_id = None

            if target_emp_id is None:
                skill_id = random.choice(list(SKILL_TYPES.keys()))
                req_skills.append({
                    "skill_type": SKILL_TYPES[skill_id],
                    "level": random.randint(1, 4)
                })

            vacancies.append({
                "_id": id_gen.get_next('vacancy'),
                "fk_employee": int(target_emp_id) if target_emp_id else None,
                "vacancy_skills": req_skills
            })

        proj_doc = {
            '_id': proj_id,
            'name': fake.catch_phrase(),
            'fk_overseer_employee': int(random.choice(employee_ids)) if random.random() > 0.05 else None,
            'location': loc_embed,
            'vacancies': vacancies
        }
        projects_data.append(proj_doc)

        for _ in range(table_counts['project_assignment']):
            emp_id = random.choice(employee_ids)
            emp_doc = employees_data[emp_id]

            assignment_start = project_start + datetime.timedelta(days=random.randint(0, (project_end - project_start).days // 2))

            has_end = random.random() > 0.15
            assignment_end = None
            if has_end:
                max_dur = (project_end - assignment_start).days
                min_dur = min(30, max_dur)
                if max_dur < 1: assignment_end = assignment_start + datetime.timedelta(days=1)
                else: assignment_end = assignment_start + datetime.timedelta(days=random.randint(min_dur, max_dur))

            schedules = generate_schedules_mongo()
            score_end = assignment_end if assignment_end else project_end
            monthly_scores = generate_monthly_scores_mongo(id_gen, assignment_start, score_end)
            session_end = assignment_end if assignment_end else min(project_end, datetime.date.today())

            for sched in schedules:
                new_sessions = generate_work_sessions_mongo(
                    id_gen, emp_id, proj_id, sched['weekday'],
                    sched['_obj_time_from'], sched['_obj_time_to'],
                    assignment_start, session_end, terminal_pool
                )
                all_sessions[emp_id].extend(new_sessions)

            mongo_schedules = []
            for s in schedules:
                mongo_schedules.append({
                    'weekday': s['weekday'],
                    'time_from': s['time_from'],
                    'time_to': s['time_to']
                })

            new_absences = generate_absences_mongo(id_gen, emp_id, assignment_start, session_end)
            emp_doc['absences'].extend(new_absences)

            role_id = random.choice(list(PROJECT_ROLES.keys()))
            assignment_doc = {
                '_id': id_gen.get_next('assignment'),
                'fk_project': proj_id,
                'project_role': PROJECT_ROLES.get(role_id) if random.random() > 0.08 else None,
                'date_start': to_datetime(assignment_start),
                'date_end': to_datetime(assignment_end) if assignment_end else None,
                'work_schedules': mongo_schedules,
                'monthly_scores': monthly_scores
            }
            emp_doc['project_assignments'].append(assignment_doc)

    db.projects.insert_many(projects_data)

    final_employee_list = list(employees_data.values())
    db.employees.insert_many(final_employee_list)

    create_collection_safe(db, 'departments', VALIDATOR_DEPARTMENT)
    dept_names = ['R&D', 'Cybersec', 'Assistance in Developing Systems', 'Frontend', 'Machine Learning', 'Database Management']
    dept_data = []
    for i in range(1, table_counts['department'] + 1):
        dept_data.append({
            '_id': i,
            'name': dept_names[i-1],
            'address': fake.street_address(),
            'fk_head_employee': int(random.choice(employee_ids)) if i < 4 else None
        })
    db.departments.insert_many(dept_data)


    created_session_colls = set()

    for emp_id, sessions in all_sessions.items():
        if sessions:
            coll_name = f"work_sessions_{emp_id}"

            if coll_name not in created_session_colls:
                create_collection_safe(db, coll_name, VALIDATOR_WORK_SESSION)
                created_session_colls.add(coll_name)

            db[coll_name].insert_many(sessions)


if __name__ == '__main__':
    populate_mongo()
