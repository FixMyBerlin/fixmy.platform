# fixmy.platform

[![Build Status](https://semaphoreci.com/api/v1/hekele/fixmy-platform/branches/master/badge.svg)](https://semaphoreci.com/hekele/fixmy-platform)

# Installation

You can run fixmy.platform for development on your local machine using the 
[Heroku command line helper](https://devcenter.heroku.com/articles/heroku-cli#download-and-install). Before
you can start the backend you need to

- Install and setup Python 3, Postgres, GDAL
- Install dependencies using `pip install -r requirements.txt`

If you are on MacOS and using brew to install dependencies you may need to set 
these flags to enable access to openssh libraries.

```
export LDFLAGS="-L/usr/local/opt/openssl@1.1/lib"
export CPPFLAGS="-I/usr/local/opt/openssl@1.1/include"
```

Now you can start the backend using `heroku local`.