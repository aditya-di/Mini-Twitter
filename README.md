# Mini-Twitter
This repository contains a set of projects covered for [CPSC-449 Web-Backend development](https://sites.google.com/view/cpsc-449/fall-2020?authuser=0) under the guidance of Prof. Kenytt Avery at CSU, Fullerton.

## Team members
- Aditya Dingare
- Aritra Sengupta

##  Built with
- [Python](https://www.python.org/downloads/) - API implementation
- [Flask](https://flask.palletsprojects.com/en/2.0.x/) - Web framework written in Python
- [SQLite3](https://www.sqlite.org/index.html) - Database to store data
- [httpie](https://httpie.io/) - API testing client
- [Foreman](https://github.com/ddollar/foreman) - Used Procfile to manage web-application
- [Tuffix](https://github.com/kevinwortman/tuffix/blob/master/install.md) or Mac OS - Operating System
- [Atom](https://atom.io/) - IDE

## Getting started
### Installations / Prerequisites
- Install Python3 and SQLite3 on your Mac/Linux
- Install Flask
```
    pip3 install Flask
```
- httpie on Mac
```
  brew install httpie
```
- Ruby Gem is required to install foreman. Use following command to install foreman:
```
  gem install foreman
```
- Use queries in database/ to up the db
- Double click on the procfile to start the two services *userService* and *timelineService*

## About project
### Project - 2
- Created a RESTful API *userService* to register user,bauthenticate, start following the other user,and stop following the other user
- *timelineService* a RESTful API to post a message, view recent 25 posts, view posts from the other user's to whom user is following, and public posts

### Project - 4
- Project-4 uses the two services created in above project - *userService and timelineService* and a **gateway** is implemented that works as a *[reverse proxy](https://www.cloudflare.com/learning/cdn/glossary/reverse-proxy/)* 
  that listens to the client requests and send it to the appropriate webserver of the service.
- All the requests are authenticated and a round robin policy is used for **load balancing** the requests. 
- Run following command to start the project: 
```
    foreman start userService=3,timelineService=3,gateway=1
```
