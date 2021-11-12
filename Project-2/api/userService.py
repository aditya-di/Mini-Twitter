#   * Simplified the db calls using:
#       https://flask.palletsprojects.com/en/1.0.x/patterns/sqlite3/
#
import sqlite3
import os
import flask
from flask import request, jsonify,Response,json,render_template,g
import werkzeug
from werkzeug import security
import sys

app = flask.Flask(__name__)
#   app.config["DEBUG"] = True
app.config['JSON_SORT_KEYS'] = False

# TODO: Make DB path dynamic
# TODO: Refactor http status code https://github.com/ansrivas/angular2-flask/blob/master/backend/flask_app/http_codes.py
database = "/Users/adityadingre/Desktop/workplace/Mini-Twitter/Project-2/database/user.db"

def make_dicts(cursor,row):
    return dict((cursor.description[idx][0],value) for idx,value in enumerate(row))

def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(database)
        db.row_factory = make_dicts
    return db

def query_db(query,args=(),one=False):
    cur = get_db().execute(query,args)
    rv = cur.fetchall()
    get_db().commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()

# welcome endpoint
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

#   create new user
#   Parameters:
#        @userName @emailID @password
#   201: valid request/user created
#   400: bad request
@app.route('/users',methods =['POST'])
def createUser():
    try:
        userName = request.form['userName']
        emailID = request.form['emailID']
        password = werkzeug.security.generate_password_hash(request.form['password'],method='pbkdf2:sha256', salt_length=8)
        query = "INSERT INTO activeUsers(userName,emailID,password) values(?,?,?)"
        query_parameters =[userName,emailID,password]
        query_db(query,query_parameters)
    except sqlite3.IntegrityError:
        return jsonify("User "+ (userName) +" already exists"),409
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify("Missing field "),400
    return jsonify("User "+ (userName) +" successfully created"),201

#   login to user account
#   @userName @password
#   200: userName and password valid
#   400: userName or password invalid/ bad request
@app.route('/login', methods =['POST'])
def authenticateUser():
    userName = request.form['userName']
    password = request.form['password']
    query = "SELECT * FROM activeUsers WHERE userName = ?"
    query_parameters =[userName]
    fetchPasswords = query_db(query,query_parameters)
    if fetchPasswords:
        currentUserPassword =fetchPasswords[0].get('password')
        isValidPassword = werkzeug.security.check_password_hash (currentUserPassword, password)
        if isValidPassword:
            return jsonify('welcome to the user page'), 200
        else:
            return jsonify('Username or Password not recognised'), 400
    conn.close()

#   user starts following to other user.
#   @followerUser @followedUser
#   200: followerUser starts following followedUser
#   400: bad request
@app.route('/users/follow',methods=['POST'])
def startFollowing():
    try:
        followerUser = request.form['followerUser']
        followedUser = request.form['followedUser']
        get_db().execute("PRAGMA foreign_keys = ON")
        query = "INSERT INTO followers(followerUser,followedUser) values(?,?)"
        query_parameters = [followerUser,followedUser]
        query_db(query,query_parameters)
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify("Missing fields"),400
    except sqlite3.IntegrityError:
        return jsonify("Check "+ (followerUser)+" and "+(followedUser)+" are valid users"),400
    return jsonify(" "+ (followerUser)+" started following "+(followedUser)),201

#   user stops following other user
#   @followerUser @followedUser
#   200: followerUser stops following followedUser
#   400: bad request
@app.route('/users/unfollow',methods=['DELETE'])
def stopFollowing():
    try:
        followerUser = request.form['followerUser']
        followedUser = request.form['followedUser']
        query = "DELETE FROM followers WHERE followerUser = ? AND followedUser=?"
        query_parameters =[followerUser,followedUser]
        query_db(query,query_parameters)
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify("Missing fields"),400
    return jsonify(""+(followerUser)+" unfollowing "+(followedUser)),200

if __name__ == "__main__" :
    app.run()
