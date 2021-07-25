from flask import Flask,request, url_for, redirect, render_template
import pickle
import numpy as np
import requests
import os
from datetime import datetime
user_api=os.environ["current_weather_data"]
import folium


app = Flask(__name__)

model=pickle.load(open('model.pkl','rb'))


@app.route('/home')
def home():
    return render_template("forest.html")

@app.route('/test')
def test():
    return render_template("test.html")

@app.route('/predict',methods=['POST','GET'])
def predict():
    features=[x for x in request.form.values()]
    location=features[0]
    location=location.lower()
    #past from wesite: api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}
    complete_link="https://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(location,user_api)
    api_link=requests.get(complete_link)
    api_data = api_link.json()
    if api_data['cod']=='404':
        return render_template('forest.html',pred="Invalid location {}  please check your location name it !".format(location.upper()),bhai="kuch karna hain iska ab?")
    else:
        m=[]
        lon=api_data["coord"]['lon']
        lat=api_data["coord"]['lat']
        x = folium.Map(location=[lat, lon], zoom_start=5)
        folium.Marker([lat, lon], popup=location).add_to(x)
        x.add_child(folium.ClickForMarker(popup="Waypoint"))
        x.save("templates/test.html")

        temp=int(api_data['main']['temp']-273.15)
        m.append(temp)
        speed=int(api_data["wind"]["speed"]*10)
        m.append(speed)
        humidity=int(api_data["main"]['humidity'])
        m.append(humidity)
        int_features=[int(x) for x in m]
        final=[np.array(int_features)]
        print(int_features)
        print(final)
        prediction=model.predict_proba(final)
        output='{0:.{1}f}'.format(prediction[0][1], 2)

        if output>str(0.5):
            return render_template('forest.html',temp=temp,oxygen=speed,humidity="{}".format(humidity),pred="Your {} Wild is in Danger.\nProbability of fire occuring is {}".format(location,output),bhai="kuch karna hain iska ab?")
        else:
            return render_template('forest.html',temp=temp,oxygen=speed,humidity="{}".format(humidity),pred= "Your {} Wild is safe.\n Probability of fire occuring is {}".format(location,output),bhai="Your Forest is Safe for now")


if __name__ == '__main__':
    app.run(debug=True)
