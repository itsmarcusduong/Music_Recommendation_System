import streamlit as st
import pandas as pd
from modules import database, recommender
from views import login_view, home_view, detail_view, playlist_view, library_view

pd.set_option('future.no_silent_downcasting', True)

st.set_page_config(page_title="Music Recommendation System", page_icon="🎵", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

if 'db_initialized' not in st.session_state:
    database.init_db()
    st.session_state['db_initialized'] = True

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'view' not in st.session_state: st.session_state['view'] = 'login'

data_artifacts = recommender.load_data_and_models()

if not st.session_state['logged_in']:
    login_view.show_login_page()
else:
    if st.session_state['view'] == 'home':
        home_view.show_home_page(data_artifacts)
    elif st.session_state['view'] == 'playlist':
        playlist_view.show_playlist_page(data_artifacts)
    elif st.session_state['view'] == 'detail':
        detail_view.show_detail_page(data_artifacts)
    # 🔥 Thêm Routing Library
    elif st.session_state['view'] == 'library':
        library_view.show_library_page(data_artifacts)