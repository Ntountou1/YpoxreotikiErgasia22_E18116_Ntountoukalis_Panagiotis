import json, os, sys
from pymongo import MongoClient

mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose InfoSys database
db = client['DigitalNotes']
students = db['Students']
notes=db['Notes']

def insert(entry,database):
    try:
        database.insert_one(entry)
        return True 
    except Exception as e:
        print(e)
        return False 

def insert_all():
    file_students = open('./data/Students.json','r')
    file_notes = open('./data/Notes.json','r')
    insertion(file_students,students)
    insertion(file_notes,notes)
    print("Inserted succesfully.")

def insertion(file,database):
    lines = file.readlines()
    for line in lines:
        entry = None 
        try:
            entry = json.loads(line)
        except Exception as e:
            print(e)
            continue
        if entry != None:
            entry.pop("_id",None) 
            insert(entry,database)

insert_all()