# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 03:21:24 2022

@author: hp
"""

import pandas as pd
from pandas_profiling import ProfileReport
import streamlit as st
from streamlit_pandas_profiling import st_profile_report

df=pd.read_csv('training_data.csv')
profile =ProfileReport(df,title="Training Data",
        dataset={
        "description": "This profiling report was generated for Amon Melly's Blog",
        "copyright_holder": "Amon Melly",
        "copyright_year": "2022",
    },)

st.subheader("Exploratory Data Analysis on Sentinel Satellite Imagery")
st_profile_report(profile)