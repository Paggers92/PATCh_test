import streamlit as st
import pandas as pd
from thefuzz import process, fuzz

name_town = pd.DataFrame([
    {'restaurant':'McDonalds', 'town':'elgin'},
    {'restaurant':"Harry Ramsden's", 'town':'forres'},
    {'restaurant':'KFC', 'town':'aberlour'},
    {'restaurant':'Prezzo', 'town':'fortrose'},
    {'restaurant':'Ask', 'town':'nairn'},
    {'restaurant':'Burger King', 'town':'invergordon'},
])

name_cuisine = pd.DataFrame([
    {'restaurant':'McDoalds', 'cuisine':'fast_food'},
    {'restaurant':"Harry Ramsdens", 'cuisine':'fish_and_chips'},
    {'restaurant':'KFCs', 'cuisine':'chicken'},
    {'restaurant':'Prezzzo', 'cuisine':'italian'},
    {'restaurant':'Asking', 'cuisine':'italian'},
    {'restaurant':'BurgerMonarch', 'cuisine':'fast_food'},
])

#st.table(name_town)
#st.table(name_cuisine)

names_1 = name_town['restaurant'].to_list()
names_2 = name_cuisine['restaurant'].to_list()

m1 = []
m2 = []
p = []

# Use the Levenshtein ratio to find the restaurant in names 2 that is most similar to each restaurant in names 1
for i in names_1:
    m1.append(process.extractOne(i, names_2, scorer=fuzz.ratio))
st.write(m1)

# If the ratio is greater than greater than or equal to our threshold, match it
for j in m1:
    if j[1] >= 60:
        p.append(j[0])
    m2.append(",".join(p)) #add an empty value if p does not meet the threshold
    p = []

st.write(m2)
name_town['matches'] = m2

# Create joined table and drop columns we don't want
all_restaurants = pd.merge(name_town, name_cuisine, how='left',
                           left_on='matches', right_on='restaurant')
all_restaurants.drop(['matches', 'restaurant_y'], axis=1, inplace=True)


st.table(all_restaurants)

