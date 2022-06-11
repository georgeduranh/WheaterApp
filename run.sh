#!/bin/bash


source venv/bin/activate
#pip install -r requirements.txt 


export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_ENV=development

#flask test
flask run