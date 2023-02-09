
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://directionRealTimeDataBase/"
})

ref= db.reference('Students') #The referent where we include the information of students inside database

data={
    "321654":{
        "name": "Andres Guapi",
        "major": "Computer vision",
        "starting_year": 2020,
        "total_attendance":7,
        "starding": "G",
        "year": 2,
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    "852741":{
        "name": "Emma Stone",
        "major": "Actress",
        "starting_year": 2021,
        "total_attendance":7,
        "starding": "B",
        "year": 1,
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    "963852":{
        "name": "Elon Musk",
        "major": "Physics",
        "starting_year": 2020,
        "total_attendance":7,
        "starding": "G",
        "year": 2,
        "last_attendance_time": "2022-12-11 00:54:34"
    }
}

#send data
for key,value in data.items():
    ref.child(key).set(value)
