# quizApp
A real time quiz application built on Python websockets for web with fully functional RESTful API.

## Run
install Redis server on Ubuntu/openSUSE/Kali/Debian bash if you are on windows.
```
redis-server (only for Windows users)

sudo pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Features
* Real time quiz application
* Login with Google (No sign up required)
* Build for the web, supports every platform once deployed
* Records each response with the validity of answer
* Keeps track of score of every quiz attempted by a user

