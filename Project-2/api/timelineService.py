import sqlite3
import os
import flask
from flask import request, jsonify,g,Response
import werkzeug
from werkzeug import security

app = flask.Flask(__name__)
app.config["DEBUG"] = True

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

#       check if use is authentic
def authenticate(user,password):
    query = "SELECT * FROM activeUsers WHERE userName = ?"
    query_parameters =[user]
    fetchPasswords = query_db(query,query_parameters)
    if fetchPasswords:
        currentUserPassword =fetchPasswords[0].get('password')
        isValidPassword = werkzeug.security.check_password_hash (currentUserPassword, password)
        if isValidPassword:
            return True
        else:
            return False

@app.route('/', methods=['GET'])
def home():
    return jsonify("Welcome to Timeline service"),200

#   user posts new post.
#   @userName
#   @postText
#   postedAt : system date
#   201: valid request
#   400: invalid request
@app.route('/tweet',methods =['POST'])
def post_tweet():
    try:
        userName = request.form['userName']
        postText = request.form['postText']
        password = request.form['password']
        if authenticate(userName,password):
            get_db().execute("PRAGMA foreign_keys = ON")
            query = "INSERT INTO userTimeline(userName,postText) values(?,?)"
            query_parameters = [userName,postText]
            query_db(query,query_parameters)
            return jsonify((userName)+" successfully tweeted"),201
        else:
            return jsonify(" authentication failed for the user"+(userName)),400
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify("Missing fields"),400
    except sqlite3.IntegrityError:
        return jsonify("Check "+ (userName)+" is a valid user"),400

#   show recent 25 posts
#   @userName
#   200: valid request
#   400: invalid request
@app.route('/recent-timeline',methods =['GET'])
def userTimeline():
    try:
        userName = request.form['userName']
        query = "SELECT * FROM userTimeline WHERE userTimeline.userName = ? ORDER BY postedAt DESC LIMIT 25"
        result = query_db(query,[userName])
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify("Missing fields"),400
    return jsonify(result),200

#   returns all the public post
#   all public posts across platform,even if user's are not following to each other
#   No parameters
#   200: valid request
#   400: invalid request
@app.route('/public-timeline',methods =['GET'])
def publicTimeline():
    try:
        query = "SELECT * FROM userTimeline ORDER BY postedAt DESC LIMIT 25"
        result = query_db(query,[])
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify("Missing fields"),400
    return jsonify(result),200

#   returns all the post from user's that particular user follows
#
@app.route('/my-timeline',methods =['GET'])
def homeTimeline():
    try:
        password = request.form['password']
        userName = request.form['userName']
        if authenticate(userName,password):
            get_db().execute("PRAGMA foreign_keys = ON")
            query = "SELECT * FROM userTimeline WHERE userName IN (SELECT followedUser FROM followers where followerUser = ?)"
            query_parameters = [userName]
            result = query_db(query,query_parameters)
            return jsonify(result),200
        else:
            return jsonify("authentication failed to view the posts for the user  "+userName),400
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify("Missing fields"),400


if __name__ == "__main__" :
    app.run()
