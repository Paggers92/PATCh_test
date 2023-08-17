import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib
from pyodide.http import open_url

data = open_url('https://raw.githubusercontent.com/Paggers92/PATCh_test/main/ofsted_benchmarking_app/Local%20authorities%20and%20regions.csv')
regions = pd.read_csv(data)
ofsted_ratings = pd.read_csv(data)

st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/007_ofsted_market_analysis/app.py)")

# Title and description
st.title('Ofsted Benchmarking Analysis')
st.write('(in development)')
st.write('This tool analyses a list of social care settings providers as provided by Ofsted.')
st.write('The user can filter on one or multiple regions.')

# Takes "Ofsted Social care providers list for LAs"
uploaded_files = st.file_uploader('Upload Ofsted social care providers list:', accept_multiple_files=True)


if uploaded_files:

    loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}

    files_dict = {}

    for name,file in loaded_files.items():
        file.dropna(axis=1, how="all", inplace=True) # Drop any fields with only nan
        file.dropna(axis=0, how="all", inplace=True) # Drop any rows with only nan
        year = name[-8:-4] # Find year of dataset from file name
        file["year"] = year # Place year into new field
        #st.write(year)

        # Find month of dataset from file name
        if "april" in name.lower():
            month = "april"
            month_num = 0.4
            # st.write(month)
        if "may" in name.lower():
            month = "may"
            month_num = 0.5
        if "june" in name.lower():
            month = "june"
            month_num = 0.6
        if "july" in name.lower():
            month = "july"
            month_num = 0.7
        file["month"] = month  # Populate new field with month name
        file["month_order"] = float(year) + month_num  # Populate new field with month number

        # Find CH, Non-CH or all from file name
        if " non" in name.lower():
            homestype = "non-ch"
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
        
        #st.dataframe(file)

        # Put name of datasets and datasets themselves into a dictionary
        files_dict[name] = file
        
      
    #files_dict

    # Append all datasets together to check which columns line up
    df = pd.concat(list(files_dict.values()), axis=0).reset_index()

    # Match local authority to region
    df = df.merge(regions,how="left",on="Local authority")

    # Select only necessary columns
    df = df[['year',
             'month',
             'month_order',
             'homestype',
             'Local authority',
             'Region_y',
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

    df = df.rename(columns = {'Region_y':'Region'})
    df['Month-Year'] = df['month'] + ' ' + df['year'].astype(str)

    # Widgit to select geography level
    with st.sidebar:
        geography_level = st.sidebar.radio('Select geography level',
             ('England', 'Region', 'Local authority')
             )
    
    # Widgits to select geographic area
    england = 'England'
    regions = pd.DataFrame(df['Region'].unique())
    regions = regions.sort_values([0])
    local_authorities = pd.DataFrame(df['Local authority'].unique())
    local_authorities = local_authorities.sort_values([0])
    #st.dataframe(local_authorities)

    if geography_level == 'Local authority':
        with st.sidebar:
            la_option = st.sidebar.selectbox(
                'Select local authority',
                (local_authorities),
                key = 1
            )
        df = df[df['Local authority'] == la_option]
        geographic_area = la_option
    elif geography_level == 'Region':
        with st.sidebar:
            region_option = st.sidebar.selectbox(
                'Select region',
                (regions),
                key = 1
            )
        df = df[df['Region'] == region_option]
        geographic_area = region_option
    else:
        df = df
        geographic_area = 'England'

    # Widgit to select provider type(s)
    #provider_types = df['Provider type'].unique()
    provider_types = pd.DataFrame(df['Provider type'].unique())
    provider_types = provider_types.sort_values([0])
    #st.dataframe(provider_types)
    with st.sidebar:
        provider_type_select = st.sidebar.multiselect( # something wrong here
            'Select provider type',
            (provider_types),
            default = (["Children's Home"])
        )
    df = df[df['Provider type'].isin(provider_type_select)]
    
    # Display dataframe
    st.dataframe(df)


    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Setting & Beds',
                                            'Overall Effectiveness', 
                                            'CYP Safety', 
                                            'Leadership & Management',
                                            'Conditions Supported'])

    with tab1:
        # Group and plot number of settings per year by sector
        count_settings = df.groupby(['Month-Year', 'month_order', 'Sector']).count().reset_index()
        count_settings = count_settings.sort_values(['month_order'])
        #st.dataframe(count_settings)
        fig_settings = px.bar(count_settings,
                    x = 'Month-Year',
                    y = 'URN',
                    color = 'Sector',
                    title = f'Number of settings in {geographic_area}<br>by sector<br>{provider_type_select}',
                    barmode='group'
        )
        st.plotly_chart(fig_settings)

        # Group and plot average number of places per year by sector
        average_places = df.groupby(['Month-Year', 'month_order', 'Sector']).mean('Number of registered places').reset_index()
        average_places = average_places.rename(columns = {'Number of registered places':'Average registered places per provision'})
        average_places = average_places.sort_values(['month_order'])
        #st.dataframe(average_places)
        fig_places = px.bar(average_places,
                    x = 'Month-Year',
                    y = 'Average registered places per provision',
                    color = 'Sector',
                    title = f'Average number of registered places for provisions in {geographic_area}<br>by sector<br>{provider_type_select}',
                    barmode='group'
        )
        st.plotly_chart(fig_places)

    with tab2:
        # Group and plot number of settings per year by Overall Effectiveness grade
        count_settings = df.groupby(['Month-Year', 'month_order', 'Overall effectiveness']).count().reset_index()
        count_settings = count_settings.sort_values(['Overall effectiveness'])
        count_settings = count_settings.sort_values(['month_order'])
        #st.dataframe(count_settings)
        fig_oe = px.bar(count_settings,
                    x = 'Month-Year',
                    y = 'URN',
                    color = 'Overall effectiveness',
                    title = f'Number of settings in {geographic_area}<br>by overall effectiveness grade<br>{provider_type_select}',
                    barmode='group',
                    color_discrete_map = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'}
        )
        st.plotly_chart(fig_oe)

    with tab3:
        # Group and plot number of settings per year by CYP Safety grade
        count_settings = df.groupby(['Month-Year', 'month_order', 'CYP safety']).count().reset_index()
        count_settings = count_settings.sort_values(['CYP safety'])
        count_settings = count_settings.sort_values(['month_order'])
        #st.dataframe(count_settings)
        fig_oe = px.bar(count_settings,
                    x = 'Month-Year',
                    y = 'URN',
                    color = 'CYP safety',
                    title = f'Number of settings in {geographic_area}<br>by CYP safety grade<br>{provider_type_select}',
                    barmode='group'
                    color_discrete_map = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'}
        )
        st.plotly_chart(fig_oe)

    pass