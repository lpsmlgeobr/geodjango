from unittest import load_tests
from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
from geopy.distance import geodesic
import folium

# Create your views here.
def calculate_distance_view(request):
    distance = None
    destination = None

    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurements')
    ip_ = get_ip_address(request)
    print(ip_)
    ip = '101.33.22.255'
    country, city, lat, lon = get_geo(ip)
    location = geolocator.geocode(city)
 
    # location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)

    # initial folium map
    m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon),
    zoom_start=8)
    #location marker 
    folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city["city"],
    icon=folium.Icon(color='purple')).add_to(m)


    if form.is_valid():
        instace = form.save(commit=False)
        destination_ = form.cleaned_data.get("destination")
        destination = geolocator.geocode(destination_)
        d_lat = destination.latitude
        d_long =destination.longitude

        # destination coordinates
        pointB = (d_lat, d_long)

        # distance calculation
        distance = round(geodesic(pointA,pointB).km,2)

        # folium map modification
        m = folium.Map(width=800, height=500, 
        location=get_center_coordinates(l_lat,l_lon,d_lat,d_long),
        zoom_start=get_zoom(distance))
         #location marker 
        folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city["city"],
        icon=folium.Icon(color='purple')).add_to(m)
        folium.Marker([d_lat, d_long], tooltip='click here for more', popup=destination,
        icon=folium.Icon(color='red',icon="cloud")).add_to(m)
       
        #draw the line between location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=5, color="blue")
        m.add_child(line)
        
        instace.location = location
        instace.distance = distance
        instace.save()
    
    m = m._repr_html_()

    context = {
        'distance': distance,
        'destination': destination,
        'form': form,
        'map': m,
    }

    return render(request, "measurements/main.html", context)
