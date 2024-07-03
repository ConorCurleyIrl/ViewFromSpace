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
st.header('Wecome to View from Space App :satellite:')
st.write('By Conor Curley :wave:')
st.image(width=150,image="https://media0.giphy.com/media/X6hiFJjvTDAAw/giphy.gif")

#Add theme to create a standard view for normal & Dark mode

#################################################################################
# Map portal - Front End
#################################################################################
 