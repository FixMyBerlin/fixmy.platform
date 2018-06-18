# fixmy.platform

Python 3.6/Django 2.0 project: REST APIs with Django

Run locally: ```$ heroku local```, then access at [localhost:5000](http://localhost:5000)

Set up Heroku:
1. ```heroku git:remote -a fixmyplatform```
2. Work around Python buildpack missing JasPer by doing `heroku stack:set cedar-14` (which is a deprecated stack) or adding [JasPer via apt](https://github.com/heroku/heroku-buildpack-python/issues/398#issuecomment-379708542)

Deploy to Heroku: ```$ git push heroku HEAD:master```
