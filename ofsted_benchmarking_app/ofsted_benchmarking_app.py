import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib
from pyodide.http import open_url

data = open_url('')
regions = pd.read_csv(data)

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/007_ofsted_market_analysis/app.py)")

# Title and description
st.title('Ofsted Benchmarking Analysis')
st.write('(in development)')
st.write('This tool analyses a list of social care settings providers as provided by Ofsted.')
# st.write('The user can filter on one or multiple regions, as well as a maximum threshold of settings per owner, to view a list of socal care settings that fit these criteria.')

# Takes "Ofsted Social care providers list for LAs"
uploaded_files = st.file_uploader('Upload Ofsted social care providers list:', accept_multiple_files=True)


if uploaded_files:

    loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}

    files_dict = {}

    for name,file in loaded_files.items():
        file.dropna(axis=1, how="all", inplace=True) # Drop any fields with only nan
        year = name[-8:-4] # Find year of dataset from file name
        file["year"] = year # Place year into new field
        # st.write(year)

        # Find month of dataset from file name
        if "april" in name.lower():
            month = "april"
            # st.write(month)
        if "may" in name.lower():
            month = "may"
        if "june" in name.lower():
            month = "june"
        if "july" in name.lower():
            month = "july"
        file["month"] = month  # Place month into new field

        # Find CH, Non-CH or all from file name
        if " non" in name.lower():
            homestype = "non-CH"
        elif " ch" in name.lower():
            homestype = "ch"
        else:
            homestype = "all"
        file["homestype"] = homestype # Place homes type into new field

        name = f"{month}{year}{homestype}"

        # Rename columns to standard names 
        file.rename(columns = {'Local Authority':'Local authority'}, inplace = True)
        file.rename(columns = {'Provider Type':'Provider type'}, inplace = True)
        file.rename(columns = {'Provision type':'Provider type'}, inplace = True)
        file.rename(columns = {'Provider Subtype':'Provider subtype'}, inplace = True)
        file.rename(columns = {'Setting Name':'Setting name'}, inplace = True)
        file.rename(columns = {'Provider Status':'Registration status'}, inplace = True)
        file.rename(columns = {'Owner Name':'Owner name'}, inplace = True)
        file.rename(columns = {'Organisation name':'Owner name'}, inplace = True)
        file.rename(columns = {'Latest overall Effectiveness grade from last full inspection':'Overall effectiveness'}, inplace = True)
        file.rename(columns = {'Overall Effectiveness':'Overall effectiveness'}, inplace = True)
        file.rename(columns = {'CYP Safety':'CYP safety'}, inplace = True)
        file.rename(columns = {'Leadership and Management':'Leadership and management'}, inplace = True)
        file.rename(columns = {'Max Users':'Number of registered places'}, inplace = True)
        file.rename(columns = {'Emotional and Behavioural Difficulties':'Emotional and behavioural difficulties'}, inplace = True)
        file.rename(columns = {'Mental Disorders':'Mental disorders'}, inplace = True)
        file.rename(columns = {'Sensory Impairment':'Sensory impairment'}, inplace = True)
        file.rename(columns = {'Present impairment':'Present alcohol problems'}, inplace = True)
        file.rename(columns = {'Present Alcohol Problems':'Present alcohol problems'}, inplace = True)
        file.rename(columns = {'Present Drug Problems':'Present drug problems'}, inplace = True)
        file.rename(columns = {'Learning Difficulty':'Learning difficulty'}, inplace = True)
        file.rename(columns = {'Physical Disabilities':'Physical disabilities'}, inplace = True)
        
        st.dataframe(file)

        # Put name of datasets and datasets themselves into a dictionary
        files_dict[name] = file
        
      
    # files_dict

    # Append all datasets together to check which columns line up
    df = pd.concat(list(files_dict.values()), axis=0).reset_index()

    # Remove unecessary columns
    df = df[['year',
             'month',
             'homestype',
             'Local authority',
             'Region',
             'URN',
             'Provider type',
             'Provider subtype',
             'Sector',
             'Setting name',
             'Registration status',
             'Owner ID',
             'Owner name',
             'Overall effectiveness',
             'CYP safety',
             'Leadership and management',
             'Number of registered places',
             'Emotional and behavioural difficulties',
             'Mental disorders',
             'Sensory impairment',
             'Present alcohol problems',
             'Present drug problems',
             'Learning difficulty',
             'Physical disabilities']]
    
    # Complete Region where there are blanks
    



    st.dataframe(df)

    
    
        





    pass