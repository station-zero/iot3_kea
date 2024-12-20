
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, render_template, make_response
import sqlite3
import hashlib
from datetime import datetime
import re

app = Flask(__name__)

hashed_pw = "fisk123"

sensors_in_total = 10

class User():

    def __init__(self):
        self.pw_hash = ""
        self.id = 9999
        self.username = ""
        self.session = ""
user = User()

def sani(s):
    s = str(s)
    s = s[:24].replace(" ", "").replace("=", "")
    return s


def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

def add_session_key(id):
    get_time = datetime.today()
    new_session_key = str(id) + "||" +  str(get_time.strftime("%Y%m%d%H%M"))

    dbcon = sqlite3.connect('database.db')
    cursor = dbcon.cursor()
    sql = "UPDATE users SET session = ? WHERE id = ?"

    cursor.execute(sql,(new_session_key,id))
    dbcon.commit()


    cursor.close()
    dbcon.close()

    return new_session_key

def check_cookie():
    cookie = request.cookies.get('sess')
    cookie_valid = False

    if cookie:
        today = datetime.today()
        now = int(today.strftime("%Y%m%d%H%M"))

        split_cookie = cookie.split("||")
        cookie_date = int(split_cookie[1])
        id = int(split_cookie[0])

        dbcon = sqlite3.connect('database.db')
        cursor = dbcon.cursor()
        sql = "SELECT session FROM users WHERE id = ?"
        cursor.execute(sql,(id,))
        rows = cursor.fetchall()

        if rows[0][0] == cookie:
            if (cookie_date + 60) > now:
                cookie_valid = True
                user.id = id

        cursor.close()
        dbcon.close()

    if cookie_valid == True:
        return True
    else:
        return False


@app.route('/login_form', methods=['post'])
def do_login():
    try:
        dbcon = sqlite3.connect('database.db')

        cursor = dbcon.cursor()

        username = request.form['username']
        password = request.form['password']

        username = sani(username)
        password = sani(password)

        sql = "SELECT * FROM users WHERE username = ?"
        cursor.execute(sql,(username,))

        login_status = False

        row_count = 0
        rows = cursor.fetchall()
        for row in rows:
            row_count = row_count + 1

        if row_count != 0:
            user.pw_hash = rows[0][2]
            user.id = rows[0][0]
            if user.pw_hash == encrypt_string(password):
                login_status = True
    except:
        return render_template('login.html',error="Server fejl")

    finally:

        if dbcon:
            dbcon.close()
        if login_status == True:
            session_key = add_session_key(user.id)
            resp = make_response( render_template('success.html'))
            resp.set_cookie('sess',session_key)

            return resp
        else:
            return render_template('login.html',error="error")



@app.route('/login')
def login_form():
    return render_template('login.html')


@app.route('/')
def index():

    return render_template('index.html', sensor_data="",path_data="", routes="")


@app.route('/map')
def load_it():

    if check_cookie() == True:
        sensors_res = []
        sensors = []
        path_x_y = []
        tracks = []

        track = request.args.get('t')
        track = sani(track)

        try:
            dbcon = sqlite3.connect('database.db')

            cursor = dbcon.cursor()

            sql = "SELECT * FROM data;"
            cursor.execute(sql)

            rows = cursor.fetchall()

            for row in rows:
                sensors_res.append(row)

            sql = "SELECT * FROM tracks WHERE user_id = ?;"
            cursor.execute(sql,(user.id,))

            rows = cursor.fetchall()

            for row in rows:
                tracks.append([row[0], row[3]])

                if str(row[0]) == str(track):
                    path_x_y = row[1]

            cursor.close()

        except sqlite3.Error as error:
            print("Failed to load sqlite table", error)

        finally:
            if dbcon:
                dbcon.close()

            for i in range(sensors_in_total):
                temp_arr = []

                for data in sensors_res:
                    if i == data[0]:
                        temp_list = []
                        temp_list.append(data[4])
                        temp_list.append(data)
                        temp_arr.append(temp_list)

                temp_arr.sort(reverse=True)

                if len(temp_arr) != 0:
                    sensors.append(temp_arr[0][1])


        return render_template('map.html', sensor_data=sensors, path_data=path_x_y, t_option=tracks)

    else:
        return render_template('login.html')


@app.route('/upload')
def upload():

    new_track = request.args.get('t')
    title = request.args.get('r')
    user = request.args.get('u')

    user = sani(user)
    title = sani(title)

    return render_template('upload.html',track=new_track,u=user,r=title)

@app.route('/new', methods=['post'])
def do_some_voodoo():
    dbcon = sqlite3.connect('database.db')
    cursor = dbcon.cursor()

    route_title = request.form['route']

    username = request.form['username']
    password = request.form['password']
    track = request.form['track']

    username = sani(username)
    password = sani(password)


    sql = "SELECT * FROM users WHERE username = ?"
    cursor.execute(sql,(username,))
    login_status = False

    row_count = 0
    rows = cursor.fetchall()
    for row in rows:
        row_count = row_count + 1

    if row_count != 0:
        user.pw_hash = rows[0][2]
        user.id = rows[0][0]
        if user.pw_hash == encrypt_string(password):
            login_status = True

    if login_status == True:
        sql = "INSERT INTO tracks(track,user_id,title)VALUES(?,?,?)"
        cursor.execute(sql,(track,user.id,route_title))
        dbcon.commit()
        cursor.close()

    return render_template('success.html')


@app.route('/data', methods=['post'])
def get_data():
    data = request.get_json()

    id = sani(data['id'])
    polution = sani(data['polution'])
    pressure = sani(data['pressure'])
    temp = sani(data['temp'])
    x_pos = sani("55.691570")
    y_pos = sani("12.554730")
    password = sani(data['pw'])
    time = sani(data['time'])
    battery = sani(data['battery'])


    if (password == hashed_pw):

        try:
            dbcon = sqlite3.connect('database.db')

            cursor = dbcon.cursor()
            sql = "INSERT INTO data(id,polution,pressure,temp,time,x_pos,y_pos,battery)VALUES(?,?,?,?,?,?,?,?)"

            cursor.execute(sql,(id,polution,pressure,temp,time,x_pos,y_pos,battery))
            dbcon.commit()

            cursor.close()

        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)

        finally:
            if dbcon:
                dbcon.close()
                print("The SQLite connection is closed")

        return "done"
