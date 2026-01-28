import pymongo
from datetime import datetime
from pymongo import MongoClient

MONGO_URI = "mongodb://admin:admin@localhost:27017/"
DB_NAME = "company_db"

db = MongoClient(MONGO_URI)[DB_NAME]

# Ilość dni urlopu które pracownicy wybrali w danym roku
def employee_absences_in_given_year(year=2023):
    employees = db.get_collection("employees")

    start_date = datetime(year, 1, 1)
    end_date = datetime(year+1, 1, 1)

    return employees.aggregate([
        {
            "$project": {
                "_id": 1,
                "absenceCount": {
                    "$size": {
                        "$filter": {
                            "input": "$absences",
                            "as": "abs",
                            "cond": {
                                "$and": [
                                    {"$gte": ["$$abs.date_from", start_date]},
                                    {"$lt": ["$$abs.date_from", end_date]},
                                ]
                            }
                        }
                    }
                }
            }
        },
        {
            "$sort": {"absenceCount": -1},
        }
    ])


# Lista pracowników nadzorujących projekty i ile nadzorują
def number_of_overseed_projects():
    projects = db.get_collection("projects")

    return projects.aggregate([
        {
            "$group": {
                "_id": "$fk_overseer_employee",
                "overseedProjects": {"$sum": 1}
            },
        },
#        {
#            "$lookup": {
#                "from": "employees",
#                "localField": "_id",
#                "foreignField": "_id",
#                "as": "employee"
#            }
#        }
    ])

# Wypisanie wszystkich pracowników którzy w danym okresie byli w danej lokacji (Adam)
def employees_in_given_location_in_period():
    employee_ids = [res["_id"] for res in db.get_collection("employees").find({}, {"_id": 1})]

    result = set()

    for id in employee_ids:
        work_sessions = db.get_collection(f"work_sessions_{id}")

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 5)

        cnt = len(list(work_sessions.aggregate([
            {
                "$match": {
                    "$and": [
                        {"time_from": {"$gte": start_date}},
                        {"time_to": {"$lte": end_date}},
                    ],
                }
            },
            {
                "$lookup": {
                    "from": "locations",
                    "localField": "fk_start_terminal",
                    "foreignField": "terminals._id",
                    "as": "location"
                }
            },
            {
                "$unwind": "$location"
            },
            {
                "$match": {
                    "location.address": "65763 Craig Bridge",
                }
            }
        ])))
        
        if cnt:
            result.add(id)


    return result


if __name__ == "__main__":
    print("\n".join(map(str, employees_in_given_location_in_period())))
