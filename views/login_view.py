import streamlit as st
from modules import database

def show_login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/2048px-Spotify_logo_without_text.svg.png", width=100)
        st.title("Music Recommendation System")
        st.markdown("### Đăng nhập để trải nghiệm âm nhạc")
        
        tab1, tab2 = st.tabs(["Đăng Nhập", "Đăng Ký"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type='password', key="login_pass")
            if st.button("Login"):
                if database.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['view'] = 'home'
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu")
                    
        with tab2:
            new_user = st.text_input("Username Mới", key="reg_user")
            new_pass = st.text_input("Password Mới", type='password', key="reg_pass")
            if st.button("Register"):
                if database.add_user(new_user, new_pass):
                    st.success("Tạo tài khoản thành công! Mời đăng nhập.")
                else:
                    st.error("Username đã tồn tại.")