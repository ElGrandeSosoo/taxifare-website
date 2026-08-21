import streamlit as st
import requests
import pandas as pd
from datetime import date, time
import numpy as np


'''
# TaxiFareModel front
'''

st.markdown('''
Remember that there are several ways to output content into your web page...

Either as with the title by just creating a string (or an f-string). Or as with this paragraph using the `st.` functions
''')

'''
## Here we would like to add some controllers in order to ask the user to select the parameters of the ride

1. Let's ask for:
- date and time
- pickup longitude
- pickup latitude
- dropoff longitude
- dropoff latitude
- passenger count
'''
st.markdown('''
Date
''')
import datetime

d = st.date_input(
    "Date",
    datetime.date(2019, 7, 6))

st.markdown('''
Time
''')

t = st.time_input('What hour do you want to be pick?', datetime.time(7, 00))

times = pd.Timestamp.combine(d, t)
st.write('OKay we will be there at', times)

st.markdown('''
Pickup Longitude
''')
pickup_longitude = st.number_input("Enter your longitude")


st.markdown('''
Pickup Latitude
''')
pickup_lattitude = st.number_input("Enter your lattitude")


st.markdown('''
Dropoff Longitude
''')
dropoff_longitude = st.number_input("Where do u want to go")

st.markdown('''
Dropoff Latitude
''')
dropoff_lattitude = st.number_input("Where do you want to go")

st.markdown('''
Passenger Count
''')
passenger_count = st.slider('Select a line count', 1, 10, 1)

st.markdown('''
MAP
''')
# def get_map_data():

#     return pd.DataFrame(48.71 + -74.00,columns=['lat', 'lon'])

# df = get_map_data()

# st.map(df, latitude=str(48.71), longitude=str(-74.00), zoom =10)

import streamlit as st
import datetime
import requests
import pandas as pd
import pydeck as pdk

'''
# Display of Our Taxifare Model
'''

"""
## Ride
### Date & Time
"""

d = st.date_input(
    "Which date do you want to select?",
    datetime.date(2019, 7, 6))

t = st.time_input('Select the time you would like for your ride', datetime.time(8, 45))

dt = datetime.datetime.combine(d, t)

st.write('Your ride is set for', dt)

"""
### Pickup & Dropoff
"""

def get_coordinates(address):
    try:
        r = requests.get(
            "https://photon.komoot.io/api/",
            params={"q": address, "limit": 1},
            headers={"User-Agent": "taxifare-streamlit-app"},
            timeout=10
        )
        data = r.json()
        if data.get("features"):
            lon, lat = data["features"][0]["geometry"]["coordinates"]
            return lat, lon
    except Exception:
        pass
    return None, None

pickup_address = st.text_input("Adresse de départ")
dropoff_address = st.text_input("Adresse d'arrivée")

pick_lat, pick_long = get_coordinates(pickup_address) if pickup_address else (None, None)
drop_lat, drop_long = get_coordinates(dropoff_address) if dropoff_address else (None, None)

if pickup_address and pick_lat is None:
    st.warning("Adresse de départ introuvable")
if dropoff_address and drop_lat is None:
    st.warning("Adresse d'arrivée introuvable")

"""
### Passenger Count
"""

option = st.slider('Select the number of passengers', 1, 6, 1)

st.write("Number of passengers: ", option)

url = 'https://taxifare.lewagon.ai/predict'

'''
# Price
'''

if pick_lat and pick_long and drop_lat and drop_long:

    params = {
        "pickup_datetime": dt,
        "pickup_longitude": pick_long,
        "pickup_latitude": pick_lat,
        "dropoff_longitude": drop_long,
        "dropoff_latitude": drop_lat,
        "passenger_count": option
    }

    response = requests.get(url, params=params)
    prediction = response.json()

    st.write("Your estimated price is", round(prediction["fare"], 2), "$")

    '''
    # Your itinerary
    '''

    def get_route(pick_lat, pick_long, drop_lat, drop_long):
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{pick_long},{pick_lat};{drop_long},{drop_lat}"
        osrm_params = {"overview": "full", "geometries": "geojson"}
        r = requests.get(osrm_url, params=osrm_params, timeout=10)
        return r.json()["routes"][0]["geometry"]["coordinates"]  # liste de [lon, lat]

    try:
        route_coords = get_route(pick_lat, pick_long, drop_lat, drop_long)

        path_layer = pdk.Layer(
            "PathLayer",
            data=[{"path": route_coords}],
            get_path="path",
            get_width=4,
            get_color=[230, 80, 60],
            width_min_pixels=3,
        )

        # Point de départ : rond simple, fixe
        pickup_layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame({"lat": [pick_lat], "lon": [pick_long]}),
            get_position=["lon", "lat"],
            get_color=[0, 100, 200],
            get_radius=80,
        )

        # Point d'arrivée : pin pointu
        pin_icon = {
            "url": "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png",
            "width": 128,
            "height": 128,
            "anchorY": 128,
        }

        dropoff_data = pd.DataFrame({
            "lat": [drop_lat],
            "lon": [drop_long],
            "icon_data": [pin_icon],
        })

        dropoff_layer = pdk.Layer(
            "IconLayer",
            data=dropoff_data,
            get_icon="icon_data",
            get_position=["lon", "lat"],
            get_size=4,
            size_scale=15,
            get_color=[230, 80, 60],
        )

        view_state = pdk.ViewState(
            latitude=(pick_lat + drop_lat) / 2,
            longitude=(pick_long + drop_long) / 2,
            zoom=12,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[path_layer, pickup_layer, dropoff_layer],
            initial_view_state=view_state,
            map_style="road"
        ))

    except Exception:
        st.warning("Impossible de calculer l'itinéraire routier pour le moment")

else:
    st.write("Merci de renseigner une adresse de départ et d'arrivée valides.")


url = 'https://taxifare.lewagon.ai/predict'

params= {
        'pickup_datetime': times,  # 2014-07-06 19:18:00
        'pickup_longitude': pickup_longitude,    # -73.950655
        'pickup_latitude': pickup_lattitude,     # 40.783282
        'dropoff_longitude': dropoff_longitude,   # -73.984365
        'dropoff_latitude': dropoff_lattitude,    # 40.769802
        'passenger_count': passenger_count
    }

response = requests.get(url, params=params)


prediction= response.json()

st.write(prediction)
