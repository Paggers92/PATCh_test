import streamlit as st
import pandas as pd

st.title('Random Forest model to predict if a child will become a CLA')

# Upload CIN Census files
uploaded_files = st.file_uploader('Upload CIN Census files:', accept_multiple_files=True)


if uploaded_files:
    loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}