from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response, session
import json
from datetime import datetime #for saving the date of user note import



# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose InfoSys database
db = client['DigitalNotes']

students = db['Students']
notes = db['Notes']

#Initiate database and collection only for the first time
#document = {"email": "admin@admin.com", "fullname": "Admin", "password":"admin", "username": "Admin", "role": "admin"}
#students.insert_one(document)

#Initiate second collection only for the first time
#document2 = {"title": "Random Title 2", "text": "Text of note 2",  "keywords":["Keyword 1 new", "Keyword 2 new", "SOS  new Keyword"], "date_of_text":datetime.now()}
#notes.insert_one(document2)

# Initiate Flask App
app = Flask(__name__)
app.secret_key = "super secret key"



@app.route('/getallstudents', methods=['GET'])
def get_all_students():
    iterable = students.find({})
    output = []
    for student in iterable:
        student['_id'] = None 
        output.append(student)
    return jsonify(output)

@app.route('/getallnotes', methods=['GET'])
def get_all_notes():
    iterable = notes.find({})
    output = []
    for note in iterable:
        note['_id'] = None 
        output.append(note)
    return jsonify(output)



# Register Student
# Create Operation
@app.route('/register_user', methods=['POST'])
def register_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "username" in data or not "fullname" in data or not "password" in data:
        return Response("Information incompleted",status=500,mimetype="application/json")
    
    if students.count_documents(({"email":data["email"]})) != 0 :
        return Response("An account with this email already exists",status=200,mimetype='application/json')
    elif students.count_documents(({"username":data["username"]})):
        return Response("An account with this username already exists",status=200,mimetype='application/json')
    else:
        student = {"email": data['email'], "username": data['username'],  "fullname":data['fullname'], "password": data['password'], "role":"user"}
        # Add student to the 'Students' collection
        students.insert_one(student)
        session['email'] = data['email']
        session['usename'] = data['username']

        print(session['email'])
        return Response("User was added to the MongoDB",status=200,mimetype='application/json') 


# Sign in user
@app.route('/sign_in_user', methods=['GET'])
def get_student_by_email():
    email = request.args.get('email')
    password = request.args.get('password')
    if email == None:
        return Response("Bad request", status=500, mimetype='application/json')
    student = students.find_one({"email":email})
    if student !=None:
        if student["password"]==password: 
            session['email']=email
            print("Email:", session['email'])
            return Response("Successful sign in! You are signed in as: " +session['email'],status=200,mimetype='application/json')
        else:
            return Response("Unsuccessful sign in. Check your password",status=200,mimetype='application/json')
    else:
        return Response('No student found',status=500,mimetype='application/json')







# Insert Student
# Create Operation
@app.route('/insert_note', methods=['POST'])
def insert_note():
    if 'email' in session:
        # Request JSON data
        data = None 
        try:
            data = json.loads(request.data)
        except Exception as e:
            return Response("bad json content",status=500,mimetype='application/json')
        if data == None:
            return Response("bad request",status=500,mimetype='application/json')
        if not "title" in data or not "text" in data or not "keywords" in data:
            return Response("Information incompleted",status=500,mimetype="application/json")
        
        note = {"title": data['title'], "text": data['text'],  "keywords": data['keywords'], "date_of_text":datetime.now()}
        # Add note to the 'notes' collection
        notes.insert_one(note)
        return Response("Note was added to the MongoDB",status=200,mimetype='application/json') 
    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')



# Find note by title
@app.route('/get_note/<string:title>', methods=['GET'])
def get_note_by_title(title):
    if 'email' in session:
        if title == None:
            return Response("Bad request", status=500, mimetype='application/json')
        note = notes.find_one({"title":title})
        if note !=None:
            note = {'title':note["title"],'text':note["text"], 'keywords':note["keywords"], 'date_of_text':note["date_of_text"]}
            return jsonify(note)
        return Response('no note found',status=500,mimetype='application/json')
    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')



#Find notes from keywords
@app.route('/get_notes_by_keyword/<string:keywords>', methods=['GET'])
def get_note_by_keyword(keywords):
    if 'email' in session:
        if keywords == None:
            return Response("Bad request", status=500, mimetype='application/json')

        iterable = notes.find({"keywords":keywords})
        output = []
        if iterable==None:
            return Response('no note found',status=500,mimetype='application/json')
        for note in iterable:
            note['_id'] = None 
            output.append(note)
            return jsonify(output)

    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')

    




 #Find note by Title and update with PUT method
@app.route('/update_note/<string:title>', methods=['PUT'])
def update_note(title): # find note by title and update with PUT method
    if 'email' in session:
        if title == None:
            return Response({"Bad request"},status=500,mimetype="application/json")
        
        note = notes.find_one({"title":title})
        if note == None:
            return Response('No note found with that title "'+ title +'"',status=500,mimetype='application/json')

        else:
            data = None 
            try:
                data = json.loads(request.data)
            except Exception as e:
                return Response("bad json content",status=500,mimetype='application/json')
            if data == None:
                return Response("bad request",status=500,mimetype='application/json')
            if not "title" in data or not "text" in data or not "keywords" in data:
                return Response("Information incompleted",status=500,mimetype="application/json")
            
            new_note = {"$set": {"title": data['title'], "text": data['text'],  "keywords": data['keywords'], "date_of_text":datetime.now()} }
            # Add note to the 'notes' collection
            notes.update_one(note, new_note)
            return Response("Note was added to the MongoDB",status=200,mimetype='application/json')
    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')




#Delete note
@app.route('/delete_note/<string:title>', methods=['DELETE'])
def delete_note(title):
    if 'email' in session:
        if title == None:
            return Response("Bad request", status=500, mimetype='application/json')
            

        note = notes.find_one({"title":title})
        if note !=None:
            notes.delete_one({"title": title})
            return Response("Note deleted successfuly", status=200, mimetype='application/json')
        
        else:
            return Response('no note found',status=500,mimetype='application/json')
    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')



#Show all notes in chronological order -Ascending
@app.route('/get_notes_ascending', methods=['GET'])
def get_notes_ascending():
    #if session['email'] !=None:
    if 'email' in session:
        iterable = notes.find().sort("date_of_text", 1)
        output = []
        for note in iterable:
            note['_id'] = None 
            output.append(note)
        return jsonify(output)
    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')
        #print("bad session")




#Show all notes in chronological order -Descending

@app.route('/get_notes_descending', methods=['GET'])
def get_notes_descendings():
    if 'email' in session:
        iterable = notes.find().sort("date_of_text", -1)
        output = []
        for note in iterable:
            note['_id'] = None 
            output.append(note)
        return jsonify(output)
    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')






#User Delete himself

@app.route('/delete_student/<string:email>', methods=['DELETE'])
def delete_student(email):
    if 'email' in session:
        if email == None:
            return Response("Bad request", status=500, mimetype='application/json')
        if email==session['email']:
            students.delete_one({"email": email})
            return Response("Account deleted successfuly", status=200, mimetype='application/json')
        else:
            return Response("You can only delete your account!", status=500, mimetype='application/json')
    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')




#Admin endpoints



#Insert New Admin
@app.route('/add_new_admin', methods=['POST'])
def add_new_admin():
    if session['email']=="admin@admin.com":
        # Request JSON data
        data = None 
        try:
            data = json.loads(request.data)
        except Exception as e:
            return Response("bad json content",status=500,mimetype='application/json')
        if data == None:
            return Response("bad request",status=500,mimetype='application/json')
        if not "username" in data or not "email" in data or not "one_use_password" in data:
            return Response("Information incompleted",status=500,mimetype="application/json")
        
        note = {"username": data['username'], "email": data['email'], "one_use_password":data["one_use_password"], "role": data['role']}
        student = students.find_one({"email":data['email']})
        if student != None:
            # Add note to the 'notes' collection
            notes.insert_one(note)
            return Response("Note was added to the MongoDB",status=200,mimetype='application/json') 
    else:
        return Response("You are not signed in and can't access this endpoint. Please sign in.", status=500, mimetype='application/json')



#Admin Delete student
@app.route('/admin_delete_student/<string:email>', methods=['DELETE'])
def admin_delete_student(email):
    if session['email']=="admin@admin.com":
        if email == None:
            return Response("Bad request", status=500, mimetype='application/json')
        student = students.find_one({"email":email})
        if student != None:
            students.delete_one({"email": email})
            return Response("Student deleted successfuly", status=200, mimetype='application/json')
        else:
            return Response('no note found',status=500,mimetype='application/json')
    else:
        return Response("You are not an admin and can't have access to this ednpoint.", status=500, mimetype='application/json')


# Run Flask App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


