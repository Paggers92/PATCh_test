import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib
from pyodide.http import open_url

# Buttons for each page linking to code
st.markdown("[![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/contribute.png?raw=true)](https://www.datatoinsight.org/patch) \
             [![Foo](https://github.com/data-to-insight/patch/blob/main/docs/img/viewthecodeimage.png?raw=true)](https://github.com/data-to-insight/patch/blob/main/apps/007_ofsted_market_analysis/app.py)")

def needs_coder(row, field):
    if row[field] == 'Y':
        return 'Yes'
    elif (int(row[field])) > 0:
        return 'Yes'
    else:
        return 'No'

def plot_chart(data_frame, var_x, var_y, var_color, var_title, var_barmode, var_labels=None, var_cdm=None, var_cat_orders=None):
    fig = px.bar(data_frame,
        x = var_x,
        y = var_y,
        color = var_color,
        title = var_title,
        barmode=var_barmode,
        labels=var_labels,
        color_discrete_map=var_cdm,
        category_orders=var_cat_orders)
    st.plotly_chart(fig)

def line_chart(data_frame, var_x, var_y, var_color, var_title):
    fig = px.line(data_frame,
        x = var_x,
        y = var_y,
        color = var_color,
        title = var_title)
    st.plotly_chart(fig)

data1 = open_url('https://raw.githubusercontent.com/data-to-insight/patch/main/apps/007_ofsted_market_analysis/Local%20authorities%20and%20regions.csv')
regions = pd.read_csv(data1)

# Title and description
st.title('Ofsted Market Analysis')
st.markdown('* This tool analyses a list of social care settings providers as provided by Ofsted.')
st.markdown('* Use the sidebar selectors to filter by geography and provider type.')
st.markdown('* Click on the tabs below the table to view different breakdowns for the selected filters.')

# Takes "Ofsted Social care providers list for LAs"
uploaded_files = st.file_uploader('Upload Ofsted social care providers list:', accept_multiple_files=True)


if uploaded_files:

    loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}

    files_dict = {}

    rename_dict = {'Local Authority':'Local authority',
                    'Provider Type':'Provider type',
                    'Provision type':'Provider type',
                    'Provider Subtype':'Provider subtype',
                    'Setting Name':'Setting name',
                    'Provider Status':'Registration status',
                    'Registration Status':'Registration status',
                    'Owner Name':'Owner name',
                    'Organisation name':'Owner name',
                    'Latest overall Effectiveness grade from last full inspection':'Overall effectiveness',
                    'Overall Effectiveness':'Overall effectiveness',
                    'CYP Safety':'CYP safety',
                    'Leadership and Management':'Leadership and management',
                    'Max Users':'Number of registered places',
                    'Emotional and Behavioural Difficulties':'Emotional and behavioural difficulties',
                    'Mental Disorders':'Mental disorders',
                    'Sensory Impairment':'Sensory impairment',
                    'Present impairment':'Present alcohol problems',
                    'Present Alcohol Problems':'Present alcohol problems',
                    'Present Drug Problems':'Present drug problems',
                    'Learning Difficulty':'Learning difficulty',
                    'Physical Disabilities':'Physical disabilities'}

    for name,file in loaded_files.items():
        file.dropna(axis=1, how="all", inplace=True) # Drop any fields with only nan
        file.dropna(axis=0, how="all", inplace=True) # Drop any rows with only nan
        year = name[-8:-4] # Find year of dataset from file name
        file["year"] = year # Place year into new field
        #st.write(year)

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
        if "august" in name.lower():
            month = "august"
        if "september" in name.lower():
            month = "september"
        if "october" in name.lower():
            month = "october"
        if "november" in name.lower():
            month = "november"
        if "december" in name.lower():
            month = "december"
        if "january" in name.lower():
            month = "january"
        if "february" in name.lower():
            month = "february"
        if "march" in name.lower():
            month = "march"
        file["month"] = month  # Populate new field with month name

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
        file.rename(columns = rename_dict, inplace = True)

        # Put name of datasets and datasets themselves into a dictionary
        files_dict[name] = file

    # Append all datasets together to check which columns line up
    df = pd.concat(list(files_dict.values()), axis=0).reset_index()

    # Match local authority to region
    df = df.merge(regions,how='left',on='Local authority')

    # Select only necessary columns
    df = df[['year',
             'month',
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

    # Select only settings with Registration Status = Active
    df = df[df['Registration status'] == 'Active']

    # Convert Month-Year to datetime format
    df['Month-Year'] = df['month'] + '/' + df['year'].astype(str)
    df["ofsted_date_order"] = pd.to_datetime(df['Month-Year'])
    df['Ofsted date'] = df['ofsted_date_order'].apply(lambda x: x.strftime('%B-%Y'))

    # Replace values
    df['Overall effectiveness'] = df['Overall effectiveness'].replace('Requires Improvement', 'Requires improvement to be good')
    df['CYP safety'] = df['CYP safety'].replace('Requires Improvement', 'Requires improvement to be good')
    df['Leadership and management'] = df['Leadership and management'].replace('Requires Improvement', 'Requires improvement to be good')

    # Create additional dataframe to code "needs provisions" fields into a Yes-No format
    needs_list = ['Emotional and behavioural difficulties',
             'Mental disorders',
             'Sensory impairment',
             'Present alcohol problems',
             'Present drug problems',
             'Learning difficulty',
             'Physical disabilities']

    for field in needs_list:
        df[field].fillna(0, inplace=True)
        df[field] = df.apply(lambda row: needs_coder(row, field), axis=1)
    #st.dataframe(df)

    # Create lists of regions and local authorites
    england = 'England'
    regions = pd.DataFrame(df['Region'].unique())
    regions = regions.sort_values([0])
    local_authorities = pd.DataFrame(df['Local authority'].unique())
    local_authorities = local_authorities.sort_values([0])
    #st.dataframe(local_authorities)

    # Create list of Ofsted dates
    ofsted_dates = pd.DataFrame(df['Ofsted date'].unique())

    # Create list of owners
    #unique_owner_ids = df.groupby('Owner ID')
    owner_list = pd.DataFrame(df['Owner name'].unique())
    owner_list.columns = ['Owner name']
    #owner_list = owner_list.str.lstrip()
    owner_list = owner_list.sort_values(['Owner name'])
    #st.dataframe(owner_list)

    # Create list of owners where they appear in each dataset
    owner_appearances = df[['Owner name', 'Ofsted date']]
    owner_appearances = owner_appearances.drop_duplicates()
    owner_appearances['Count'] = 1
    st.dataframe(owner_appearances)
    owner_appearances = owner_appearances.pivot(index='Owner name', columns='Ofsted date', values='Count')
    owner_appearances['First year appearing'] = '' #### ADD LAMBDA FUNCTION FOR CONDITIONAL COLUMN - AN IF ELSE FOR EACH OFSTED-DATE

    # Widgit to toggle between geography and owner-level analysis
    with st.sidebar:
        toggle = st.sidebar.radio('Analyse by geographic area or owner name',
            ('Geographic area', 'Owner name')
            )

    if toggle == 'Geographic area':
        # Widgit to select geography level
        with st.sidebar:
            geography_level = st.sidebar.radio('Select geography level',
                ('England', 'Region', 'Local authority')
                )
        
        # Widgits to select geographic area
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

    elif toggle == 'Owner name':
        # Widgit to select provider
        with st.sidebar:
            owner_selected = st.sidebar.selectbox(
                'Select owner name',
                (owner_list)
            )
        df = df[df['Owner name'] == owner_selected]
        #geographic_area = ""

    
    else:
        df = df

    with st.sidebar:
        floor2 = st.sidebar.selectbox(
            'Registered places - group boundary 1-2',
            (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
            index=0
        )

    with st.sidebar:
        floor3 = st.sidebar.selectbox(
            'Registered places - group boundary 2-3',
            (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
            index=3
        )

    with st.sidebar:
        floor4 = st.sidebar.selectbox(
            'Registered places - group boundary 3-4',
            (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
            index=8
        )
    
    ceiling1 = floor2 - 1
    ceiling2 = floor3 - 1
    ceiling3 = floor4 - 1

    # Add grouped column for number of registered places
    df['Registered places group'] = df['Number of registered places'].transform(lambda x: '1 to ' + str(ceiling1) if x < floor2
                                                                                else str(floor2) + ' to ' + str(ceiling2) if floor2 <= x < floor3
                                                                                else str(floor3) + ' to ' + str(ceiling3) if floor3 <= x < floor4
                                                                                else str(floor4) + '+')
    
    # Display dataframe, reset index and don't display index column
    df_display = df[['Ofsted date',
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
             'Registered places group',
             'Emotional and behavioural difficulties',
             'Mental disorders',
             'Sensory impairment',
             'Present alcohol problems',
             'Present drug problems',
             'Learning difficulty',
             'Physical disabilities']].reset_index()
    st.dataframe(df_display.iloc[:,1:])

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Setting & Beds',
                                            'Overall Effectiveness', 
                                            'CYP Safety', 
                                            'Leadership & Management',
                                            'Conditions Supported',
                                            'List of owners'])

    with tab1:
        if toggle == 'Geographic area':
            title_1 = f"Number of settings in {geographic_area} by sector<br>{', '.join(provider_type_select)}"
            title_2 = f"Total number of registered places for provisions in {geographic_area} by sector<br>{', '.join(provider_type_select)}"
            title_3 = f"Number of settings with grouped number of registered places in {geographic_area} by sector<br>{', '.join(provider_type_select)}"
        else:
            title_1 = f"Number of settings owned by {owner_selected}"
            title_2 = f"Total number of registered places for provisions owned by {owner_selected}"
            title_3 = f"Number of settings with grouped number of registered places owned by {owner_selected}"

        # Group and plot number of settings by sector
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Sector']).count().reset_index()
        #count_settings['Ofsted date'].dtypes
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Sector',
                   var_title = title_1,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"))

        # Group and plot total number of places by sector
        total_places = df.groupby(['ofsted_date_order', 'Ofsted date', 'Sector']).sum('Number of registered places').reset_index()
        total_places = total_places.rename(columns = {'Number of registered places':'Total registered places'})
        #total_places = total_places.sort_values(['ofsted_date_order'])
        #st.dataframe(total_places)
        plot_chart(data_frame=total_places,
                   var_x = 'Ofsted date',
                   var_y = 'Total registered places',
                   var_color = 'Sector',
                   var_title = title_2,
                   var_barmode = 'group')

        # Group and plot number of settings with grouped number of registered places
        grouped_places = df.groupby(['ofsted_date_order', 'Ofsted date', 'Registered places group']).count().reset_index()
        line_chart(data_frame=grouped_places,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Registered places group',
                   var_title = title_3)

    with tab2:
        if toggle == 'Geographic area':
            title_3 = f"Number of settings in {geographic_area} by overall effectiveness grade<br>{', '.join(provider_type_select)}"
            title_4 = f'Number of private sector settings in {geographic_area}<br>by overall effectiveness grade<br>{provider_type_select}'
            title_5 = f'Number of local authority sector settings in {geographic_area}<br>by overall effectiveness grade<br>{provider_type_select}'
        else:
            title_3 = f"Number of settings owned by {owner_selected} by overall effectiveness grade"
            title_4 = f'Number of private sector settings owned by {owner_selected}<br>by overall effectiveness grade'
            title_5 = f'Number of local authority sector settings owned by {owner_selected}<br>by overall effectiveness grade'

        # Group and plot number of settings by Overall Effectiveness grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Overall effectiveness']).count().reset_index()
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Overall effectiveness',
                   var_title = title_3,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Overall effectiveness':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})

        # Plot for private sector only
        count_settings_private = df[df['Sector'] == 'Private'].groupby(['ofsted_date_order', 'Ofsted date', 'Overall effectiveness']).count().reset_index()
        #count_settings_private = count_settings_private.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_private)
        plot_chart(data_frame=count_settings_private,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Overall effectiveness',
                   var_title = title_4,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Overall effectiveness':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for local authority sector only
        count_settings_la = df[df['Sector'] == 'Local Authority'].groupby(['ofsted_date_order', 'Ofsted date', 'Overall effectiveness']).count().reset_index()
        #count_settings_la = count_settings_la.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_la)
        plot_chart(data_frame=count_settings_la,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Overall effectiveness',
                   var_title = title_5,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Overall effectiveness':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})

        

    with tab3:
        if toggle == 'Geographic area':
            title_6 = f"Number of settings in {geographic_area} by CYP safety grade<br>{', '.join(provider_type_select)}"
            title_7 = f'Number of private sector settings in {geographic_area}<br>by CYP safety grade<br>{provider_type_select}'
            title_8 = f'Number of local authority sector settings in {geographic_area}<br>by CYP safety grade<br>{provider_type_select}'
        else:
            title_6 = f"Number of settings owned by {owner_selected} by CYP safety"
            title_7 = f'Number of private sector settings owned by {owner_selected}<br>by CYP safety grade'
            title_8 = f'Number of local authority sector settings owned by {owner_selected}<br>by CYP safety grade'

        # Group and plot number of settings by CYP Safety grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'CYP safety']).count().reset_index()
        count_settings = count_settings.sort_values(['CYP safety'])
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'CYP safety',
                   var_title = title_6,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'CYP safety':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for private sector only
        count_settings_private = df[df['Sector'] == 'Private'].groupby(['ofsted_date_order', 'Ofsted date', 'CYP safety']).count().reset_index()
        #count_settings_private = count_settings_private.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_private)
        plot_chart(data_frame=count_settings_private,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'CYP safety',
                   var_title = title_7,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'CYP safety':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for local authority sector only
        count_settings_la = df[df['Sector'] == 'Local Authority'].groupby(['ofsted_date_order', 'Ofsted date', 'CYP safety']).count().reset_index()
        #count_settings_la = count_settings_la.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_la)
        plot_chart(data_frame=count_settings_la,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'CYP safety',
                   var_title = title_8,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'CYP safety':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


    with tab4:
        if toggle == 'Geographic area':
            title_9 = f"Number of settings in {geographic_area} by Leadership & Management grade<br>{', '.join(provider_type_select)}"
            title_10 = f'Number of private sector settings in {geographic_area}<br>by Leadership & Management grade<br>{provider_type_select}'
            title_11 = f'Number of local authority sector settings in {geographic_area}<br>by Leadership & Management<br>{provider_type_select}'
        else:
            title_9 = f"Number of settings owned by {owner_selected} by CYP safety"
            title_10 = f'Number of private sector settings owned by {owner_selected}<br>by Leadership & Management'
            title_11 = f'Number of local authority sector settings owned by {owner_selected}<br>by Leadership & Management'

        # Group and plot number of settings by Leadership & Management grade
        count_settings = df.groupby(['ofsted_date_order', 'Ofsted date', 'Leadership and management']).count().reset_index()
        count_settings = count_settings.sort_values(['Leadership and management'])
        #count_settings = count_settings.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings)
        plot_chart(data_frame=count_settings,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Leadership and management',
                   var_title = title_9,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Leadership and management':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for private sector only
        count_settings_private = df[df['Sector'] == 'Private'].groupby(['ofsted_date_order', 'Ofsted date', 'Leadership and management']).count().reset_index()
        #count_settings_private = count_settings_private.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_private)
        plot_chart(data_frame=count_settings_private,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Leadership and management',
                   var_title = title_10,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Leadership and management':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


        # Plot for local authority sector only
        count_settings_la = df[df['Sector'] == 'Local Authority'].groupby(['ofsted_date_order', 'Ofsted date', 'Leadership and management']).count().reset_index()
        #count_settings_la = count_settings_la.sort_values(['ofsted_date_order'])
        #st.dataframe(count_settings_la)
        plot_chart(data_frame=count_settings_la,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Leadership and management',
                   var_title = title_11,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"),
                   var_cdm = {
                        'Outstanding' : 'blue',
                        'Good' : 'green',
                        'Adequate' : 'cornsilk',
                        'Requires improvement to be good' : 'orange',
                        'Inadequate' : 'red',
                        'Not yet inspected' : 'grey'},
                    var_cat_orders = {'Leadership and management':['Outstanding', 'Good', 'Adequate', 'Requires improvement to be good', 'Inadequate', 'Not yet inspected']})


    with tab5:
        if toggle == 'Geographic area':
            title_12 = f"Number of settings in {geographic_area}<br>providing care for categories of need<br>{', '.join(provider_type_select)}"

        else:
            title_12 = f"Number of settings owned by {owner_selected}<br>providing care for categories of need"

        # Group and plot number of settings per year that support each category of need
        count_needs = pd.DataFrame()

        for need in needs_list:
            df_yes = df.groupby(['ofsted_date_order', 'Ofsted date', need]).count().reset_index()
            df_yes = df_yes[df_yes[need] == 'Yes']
            df_yes.rename(columns = {need:'Category_of_need'}, inplace = True)
            df_yes['Category_of_need'] = df_yes['Category_of_need'].replace('Yes', need)
            df_yes = df_yes[['Ofsted date',
                            'ofsted_date_order',
                            'Category_of_need',
                            'URN']]
            count_needs = count_needs.append(df_yes)
            #st.dataframe(df_yes)
        
        #st.dataframe(count_needs)
        plot_chart(data_frame=count_needs,
                   var_x = 'Ofsted date',
                   var_y = 'URN',
                   var_color = 'Category_of_need',
                   var_title = title_12,
                   var_barmode = 'group',
                   var_labels = dict(URN = "Number of settings"))

    with tab6:
        st.dataframe(owner_appearances)

    pass