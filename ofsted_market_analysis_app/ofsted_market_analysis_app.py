import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib

# Takes "Ofsted Social care providers list for LAs"
uploaded_files = st.file_uploader('Upload Ofsted social care providers list', accept_multiple_files=False)

if uploaded_files:
    loaded_files = {uploaded_files.name: pd.read_csv(uploaded_files)}
    
    for file in loaded_files.items():
        st.write(file[0]) # Print the key from the dictionary for this file
        #st.dataframe(file[1]) # Print the dataframe from the dictionary for this file

    # Access the dataframe for the file
    df = list(loaded_files.values())[0]

    # Take only the first 48 columns and rows where URN is not null
    df = df.iloc[:, : 47]
    df = df.dropna(subset=['URN'])

    # Filter out Sectors "Local Authority" and "Health Authority"
    df = df[~df['Sector'].isin(['Local Authority', 'Health Authority'])]

    # Where owner fields are blank, replace with setting fields
    df['Owner ID'][df['Owner ID'].isna()] = df['URN']
    df['Owner name'][df['Owner name'].isna()] = df['Setting name']

    # Add column for number of settings per owner
    df['Number of settings with this owner'] = df.groupby('Owner ID')['Owner ID'].transform('count')
    #st.dataframe(df)

    # Widgits to filter the dataframe
    regions = df['Region'].unique()
    with st.sidebar:
        region_option = st.sidebar.selectbox(
            'Select region',
            (regions)
        )
    df = df[df['Region'] == region_option]

    with st.sidebar:
        upper_threshold = st.sidebar.number_input(
            'Enter upper threshold for portfolio of settings per owner',
            min_value = 1,
            max_value = 100,
            value = 5
        )
    df = df[df['Number of settings with this owner'] <= upper_threshold]
    

    # Select only certain columns in dataframe
    df = df[['URN',
             'Setting name',
             'Owner name',
             'Local authority',
             'Number of registered places',
             'Number of settings with this owner']]

    # Display dataframe
    st.dataframe(df)

    # Create a plot
    fig = px.histogram(df, x='Number of settings with this owner')
    st.plotly_chart(fig)

    pass