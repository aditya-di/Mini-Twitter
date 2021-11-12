#   Simple API gateway in Python
#   Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>
#   Reference for below code : https://flask-httpauth.readthedocs.io/en/latest/
#   gateway recieves all the request and routes the request to the appropriate
#   endpoint. All requests are authorized
import sys
import flask
import requests
from flask import request,jsonify
import itertools
from flask_httpauth import HTTPBasicAuth
import json
auth = HTTPBasicAuth()

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

#   api endpoints
userEndpoints = {'/users?':True,'/login?':True,'/users/follow?':True,'/users/unfollow?':True}
timelineEndpoints = {'/tweet?':True}

#   get instance values
userInstance = app.config['USER_SERVICE']
timelineInstance = app.config['TIMELINE_SERVICE']
failedInstance = []    # to store the failed instance

#   serve the request from the next instance
currentUserInstance = itertools.cycle(userInstance)
currentTimelineInstance = itertools.cycle(timelineInstance)

@app.errorhandler(404)
@auth.login_required
def route_page(err):
    try:
        currentRequest = flask.request.full_path
        #   request is either userService or timelineService api endpoint
        if  currentRequest in userEndpoints:
            upstream = next(currentUserInstance)
        elif  currentRequest in timelineEndpoints:
            upstream = next(currentTimelineInstance)

        #   if failed instance,skip it and assign the request to the next instance
        if upstream in failedInstance:
            upstream = next(currentUserInstance)

        #   hit the request to either userService or timelineService from gateway
        #   ex:  http://127.0.0.1:5100//users/follow
        response = requests.request(
            flask.request.method,
            upstream + flask.request.full_path,
            data = flask.request.get_data(),
            headers = flask.request.headers,
            cookies = flask.request.cookies,
            stream = True
        )
        responseMessgae = response.content.decode("utf-8")
        return flask.json.jsonify({
        'response': responseMessgae }),200

        #   If instance is failed, store it in failedInstance list
        #   and skip in the subsequent iteration
    except requests.exceptions.RequestException as e:
        app.log_exception(sys.exc_info())
        failedInstance.append(upstream)
        return flask.json.jsonify({
            'method': e.request.method,
            'url': e.request.url,
            'exception': type(e).__name__,
        }), 503
    headers = remove_item(
        response.headers,
        'Transfer-Encoding',
        'chunked'
    )

def remove_item(d, k, v):
    if k in d:
        if d[k].casefold() == v.casefold():
            del d[k]
    return dict(d)

@auth.verify_password
def verify_password(userName,password):
    #   endpoints /users and /login does not require authentication
    if (flask.request.full_path =="/users?") or (flask.request.full_path =="/login?"):
        return True
    if userName is None or password is None:
        return False
    userName = request.authorization.username
    password= request.authorization.password
    payload = {'userName':userName,'password':password}
    response = requests.post('http://127.0.0.1:5100/login',data = payload)
    if response.ok:
        return True
    else:
        return False
