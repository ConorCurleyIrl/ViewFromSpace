# Starting a new Project to view Satellite dats
# App 1 - a way of exploring satilite data to create interesting comparions & Timelapse data
# App 2 - using Satilite data with ML for public good usecases. Usecase 1 Bush fires
# App 3 - Expand use of different data sources for public good usecases - Road quality assessments.


######################
# about sentinal 2
#https://dataspace.copernicus.eu/explore-data/data-collections/sentinel-data/sentinel-2
"""
Sentinel-2

The Copernicus Sentinel-2 mission consists of two polar-orbiting satellites that are positioned in the same sun-synchronous orbit, with a phase difference of 180°.
It aims to monitor changes in land surface conditions. 
The satellites have a wide swath width (290 km) and a high revisit time. 
This capability will support monitoring of changes on the Earth's surface.

Sentinel-2 provides high-resolution images in the visible and infrared wavelengths, to monitor vegetation, soil and water cover, inland waterways and coastal areas.

Spatial resolution: 10m, 20m, and 60m, depending on the wavelength (that is, only details bigger than 10m, 20m, and 60m can be seen). More info here.

Revisit time: maximum 5 days to revisit the same area, using both satellites.

Data availability: Since June 2015. Full global coverage since March 2017.

Common usage: Land-cover maps, land-change detection maps, vegetation monitoring, monitoring of burnt areas.

We are simulating this browser:
https://browser.dataspace.copernicus.eu/?zoom=9&lat=45.5043&lng=12.73178&themeId=DEFAULT-THEME&visualizationUrl=U2FsdGVkX1%2F3kOhMYoehYgUVTmu7xsVepx4gF1AcbbVdSiLd6iKE1WZZPunwNzIjQZhEBA%2Bt8w26agy7GYFVVcO8AmxC3VnX%2B0z27o%2FSb7S6AzCOzmyD1JQa0HBXdSUm&datasetId=S2_L2A_CDAS&fromTime=2023-02-07T00%3A00%3A00.000Z&toTime=2023-02-07T23%3A59%3A59.999Z&layerId=1_TRUE_COLOR&demSource3D=%22MAPZEN%22&cloudCoverage=10&dateMode=SINGLE

"""



#############################################################################
#imports
#############################################################################
#stanadard libraries

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import hmac

#More specialised libraries

#https://pypi.org/project/st-files-connection/
#pip install st-files-connection
#from st_files_connection import FilesConnection

#https://pystac.readthedocs.io/en/stable/
#conda install -c conda-forge  pystac-client
from pystac_client import Client 

#https://odc-stac.readthedocs.io/en/latest/intro.html
#conda install -c conda-forge odc-stac
from odc.stac import  load

#############################################################################


#Main Streamlit  app starts here
st.header('Wecome to my satelitte imagry app')

#Add theme to create a standard view for normal & Dark mode

#################################################################################
# Map portal - Front End
#################################################################################
 
st.title('Satellite Map Portal')

#Initatise session state  fpr date labels and user_date
if 'data_labels' not in st.session_state:
    st.session_state.data_labels = []

if 'data' not in st.session_state:
    st.session_state.data = None

if 'user_date' not in st.session_state:
    st.session_state.user_date = None

if 'user_date_index' not in st.session_state:
    st.session_state.user_date_index =0 

#Source of data 
#this can be a drop down with renaming of sources
collections = ["sentinel-2-l2a"]

# I dont exactly understand why these are in columns - where is this submitted? I wonder if it is standard for other sources?
columns = ['collections', 'start_date', 'end_date', 'min_cloud_cover' ]

# This is a new componet - I wonder how much customization is possible 
# Would be nice to have a maps and a pin drop interface for selecting the spot
# Why is there '*' at the end of each label - does this bold it?
with st.form(key='test'):
    collections =st.selectbox("collections*", options= collections, index=None)
    start_date  = st.date_input(label="start_date*")
    end_date  = st.date_input(label="end_date*")
    max_cloud_cover = st.number_input(label= "max_cloud_cover*", value=10)
    longitude= st.number_input(label="longitude*", format="%.4f", value=119.7513)
    latitude= st.number_input(label="latitude*", format="%.4f", value=37.250921)
    buffer = st.number_input(label="buffer (0.01 = 1 KM)*", format="%.2f, value = 0.01")

    #add a note what is needed
    st.markdown("***required*")

    submit_button_run = st.form_submit_button(label="Run")
    submit_button_list= st.form_submit_button(label="List Available Images")
    submit_button_viz= st.form_submit_button(label="Visualize")

#################################################################################
# Backend - Search Function
#################################################################################
 
sat_img_library= "sentinel-2-l2a"
sat_img_long = "-120.15,38.93"
sat_img_lat = "-119.88,-39.25"
sat_img_date = "2023-06-07/2023-06-30"


#Define the Search function
def search_satelitte_images(collection = sat_img_library,
                            bbox=[sat_img_long,sat_img_lat],
                            date=sat_img_date,
                            cloud_cover=(0,10)):
    # Define the search client
    client= Client.open("https://earth-search.aws.element84.com/v1")
    search = client.search(collections=[collection],
                            bbox=bbox,
                            datetime=date,
                            query=[f"eo:cloud_cover<{cloud_cover[1]}", f"eo:cloud_cover>{cloud_cover[0]}"])

    # Print the number of matched items
    print(f"Number of images found: {search.matched()}")

    data = load(search.items(), bbox=bbox, groupby="solar_day", chunks={})

    print(f"Number of days in data: {len(data.time)}")

    return data

def get_bbox_with_buffer(latitude=37.2502, longitude=-119.7513, buffer=0.01):
    
    min_lat = latitude - buffer
    max_lat = latitude + buffer
    min_lon = longitude - buffer
    max_lon = longitude + buffer
    
    bbox = [min_lon, min_lat, max_lon, max_lat]
    return bbox

#####################################################
# Backend - Run Button
#####################################################

# Create an empty DataFrame with these columns
df = pd.DataFrame(columns=columns)

if "mdf" not in st.session_state:
    st.session_state.mdf = pd.DataFrame(columns=df.columns)


# New Data
with st.form(key="test"):
    
    collection=st.selectbox("collection*",options=collections,index=None)
    start_date = st.date_input(label="start_date*")
    end_date = st.date_input(label="end_date*")
    max_cloud_cover  = st.number_input(label="max_cloud_cover*",value=10)
    longitude=st.number_input(label="longitude*", format="%.4f",value=-119.7513)
    latitude=st.number_input(label="latitude*", format="%.4f",value=37.2502)
    buffer=st.number_input(label="buffer (0.01 = 1 km)*", format="%.2f",value=0.01)

    # Mark Mandatory fields
    st.markdown("**required*")

    submit_button_run = st.form_submit_button(label="Run")
    submit_button_list = st.form_submit_button(label="List Available Images")
    submit_button_viz = st.form_submit_button(label="Visualize")

    if submit_button_run:
        new_df=pd.DataFrame(
            [
                {   
                    "collection": collection,
                    "start_date":start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "max_cloud_cover":max_cloud_cover,
                    "longitude": longitude,
                    "latitude": latitude,
                    "buffer": buffer,

                }

            ]
        )
        
        st.session_state.mdf = pd.concat([st.session_state.mdf, new_df], axis=0)
        st.dataframe(st.session_state.mdf)
        st.success("Your request successfully submitted!")

        data = search_satelitte_images(collection=collection,
                                       date=f"{start_date}/{end_date}",
                                       cloud_cover=(0, max_cloud_cover),
                                       bbox=get_bbox_with_buffer(latitude=latitude, longitude=longitude, buffer=buffer))
        st.session_state.data = data

        date_labels = []
        # Determine the number of time steps
        numb_days = len(data.time)
        # Iterate through each time step
        for t in range(numb_days):
            scl_image = data[["scl"]].isel(time=t).to_array()
            dt = pd.to_datetime(scl_image.time.values)
            year = dt.year
            month = dt.month
            day = dt.day
            date_string = f"{year}-{month:02d}-{day:02d}"
            date_labels.append(date_string)
        
        st.session_state.date_labels= date_labels