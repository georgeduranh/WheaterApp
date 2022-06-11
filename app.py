import requests

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import os

app = Flask(__name__)

#App config 
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET')

appid = os.environ.get('ACCESS_KEY')

#DB config
db = SQLAlchemy(app)

#City model
class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)

#Fuction to get API response of Wheater
def get_weather_data(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&APPID={ appid }'
    r = requests.get(url).json()
    return r


# Get Index route, we can see the results on this path
@app.route('/')
def index_get():
    
    #Limiting the results to 5 cities, order by id (most recent to the old one)
    cities = City.query.order_by(desc(City.id)).limit(5).all()    
    weather_data = []

    #Loop to storte the cities to show in the template
    for city in cities:
        r = get_weather_data(city.name)
        print(r)

        weather = {
            'city': city.name ,
            'temperature': r['main']['temp'] ,
            'description' : r['weather'][0]['description'] ,
            'icon' :  r['weather'][0]['icon']
        }
        #print(weather)
        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)


# Post on Index route, we can request data from an specific city and add it to the main  view
@app.route('/', methods = ['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')

    #Validation of the city, if this doesn't exist in the DB and we got 200ok from the API we add it. 
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'City does not exists in the world'
        else:
            err_msg = 'City already exists in de database!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added sucessfully')
    
    return redirect(url_for('index_get'))


#Route to delete an city of the list 
@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f'Sucessfuly deleted {city.name}', 'success')
    return redirect(url_for('index_get'))