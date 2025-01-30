from flask import Flask, send_file, request, jsonify, session, render_template, redirect
import sqlite3
from hashlib import sha256


db = sqlite3.connect("myDatabase.db", check_same_thread=False)
cur = db.cursor()

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'


@app.route('/login', methods=["GET"])
def login_page():
    return send_file('login.html')
     
@app.route('/login', methods=["POST"])
def login_action():
    username = request.form["email"]
    pwd = request.form["password"]
    result = cur.execute("SELECT id FROM users WHERE email = ? AND password = ?", (username, sha256(pwd.encode()).hexdigest(),)).fetchone()
    if result != None:
        session['id'] = result[0]
        return redirect("/home")
    else:
        return send_file('login.html')

@app.route('/signup', methods=["GET"])
def signup_page():
    return send_file('signup.html')

@app.route('/signup', methods=["POST"])
def signup_action():
    email = request.form["email"]
    username = request.form["username"]
    pwd = request.form["password"]
    print(cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email=?)", (email,)).fetchone())
    if cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email=?)", (email,)).fetchone() == (0,) and cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username=?)", (username,)).fetchone() == (0,):
        cur.execute("INSERT INTO users (email, password, username) VALUES (?, ?, ?)", (email, sha256(pwd.encode()).hexdigest(), username,))
        db.commit()
        return send_file('login.html')
    else:
        return send_file('signup.html')

@app.route("/home", methods=["GET"])
def PersonnalPage():
    if Authenticate():
        return render_template('HomePage.html', name=GetInfos("username"), Tasks=GetTasks())
    else:
        return send_file("login.html")

@app.route("/createTask", methods=["POST"])
def AddTask():
    if(Authenticate()):
        name = request.form["name"]
        description= request.form["description"]
        cur.execute("INSERT INTO tasks (user_id, description, name, done) VALUES (?,?,?,?)", (session["id"], description, name, False,))
        db.commit()
    return redirect("/home")

@app.route("/checkTask", methods=["GET"])
def CheckTask():
    TaskIDToCheck = request.args.get('id')
    if(Authenticate()):
        CheckVar = cur.execute("SELECT user_id FROM tasks WHERE id=?", (TaskIDToCheck,)).fetchone()
        
        if CheckVar and CheckVar[0] == session["id"]:
            cur.execute("UPDATE tasks SET done = ? WHERE id=?", (request.args.get('state'), TaskIDToCheck,))
            db.commit()
    return redirect("/home")


@app.route("/createTask", methods=["GET"])
def RerouteToHome():
    return redirect("/home")

@app.route("/deleteTask", methods=["GET"])
def DeleteTask():
    TaskIDToDelete = request.args.get('id')
    if Authenticate():
        CheckVar = cur.execute("SELECT user_id FROM tasks WHERE id=?", (TaskIDToDelete,)).fetchone()
        if CheckVar and CheckVar[0] == session["id"]:
            cur.execute("DELETE FROM tasks WHERE id=?", (TaskIDToDelete,))
            db.commit()
    return redirect("/home")


def Authenticate():
    if "id" in session and cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE id=?)", (session["id"],)).fetchall():
        return True
    else:
        return False
def GetInfos(info): #Always call after authenticate
    return cur.execute(f"SELECT {info} FROM users WHERE id = ?", (session["id"],)).fetchone()[0]


def GetTasks():
    return cur.execute("SELECT name, description, id, done FROM tasks WHERE user_id = ?", (session["id"],)).fetchall()

@app.route('/')
def home():
    return send_file('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
