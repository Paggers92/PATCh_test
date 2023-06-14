import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib

# Takes "benchmarking_data_a1"
uploaded_files = st.file_uploader('Upload National Benchmarking Data', accept_multiple_files=False)

if uploaded_files:
    loaded_files = {uploaded_files.name: pd.read_csv(uploaded_files)}
    
    for file in loaded_files.items():
        st.write(file[0]) # Print the key from the dictionary for this file
        # st.dataframe(file[1]) # Print the dataframe from the dictionary for this file

    # Access the dataframe for the file
    df = list(loaded_files.values())[0]
    df['time_period'] = df['time_period'].astype('int')

    # Widgits to filter the dataframe
    cat_types = df['category'].unique()
    with st.sidebar:
        cat_option = st.sidebar.selectbox(
            'Select category',
            (cat_types)
        )
    df = df[df['category'] == cat_option]

    sub_cat_types = df['category_type'].unique()
    with st.sidebar:
        sub_cat_option = st.sidebar.selectbox(
            'Select subcategory',
            (sub_cat_types)
        )
    df = df[df['category_type'] == sub_cat_option]
    

    with st.sidebar:
        years = st.sidebar.slider(
            'Year select',
            min_value=2013,
            max_value=2022,
            value=[2013,2022]
        )
    df = df[(df['time_period'] >= years[0]) & (df['time_period'] <= years[1])]

    st.dataframe(df)

    with st.sidebar:
        chart_title = st.sidebar.text_input(
            'Title your chart',
            value = '(please label your chart)'
        )

    # Create a plot
    fig = px.line(df, x='time_period', y='number', title=chart_title)
    st.plotly_chart(fig)

    pass

# # For multiple files
# # Create a dictionary to contain the names of each uploaded file, and embed each file to their respective name
# if uploaded_files:
#     loaded_files = {file.name: pd.read_csv(file) for file in uploaded_files}
#     st.write(loaded_files[0])
#     st.write('File uploaded!')
#     pass