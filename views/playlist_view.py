import streamlit as st

def show_playlist_page(data_artifacts):
    playlist_name = st.session_state.get('playlist_name', 'Playlist')
    playlist_tracks = st.session_state.get('playlist_tracks')
    
    if st.button("⬅️ Home"):
        st.session_state['view'] = 'home'
        st.rerun()
        
    st.markdown(f"""
    <div style="background: linear-gradient(180deg, #535353 0%, #121212 100%); padding: 30px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 50px;">{playlist_name}</h1>
        <p>Playlist gợi ý riêng cho {st.session_state['username']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 4, 3, 1])
    col1.write("#")
    col2.write("TITLE")
    col3.write("ARTIST")
    col4.write("PLAY")
    st.divider()
    
    for idx, row in playlist_tracks.reset_index(drop=True).iterrows():
        with st.container():
            c1, c2, c3, c4 = st.columns([1, 4, 3, 1])
            c1.write(f"{idx + 1}")
            c2.write(f"**{row['track_name']}**")
            c3.write(row['artists'])
            if c4.button("▶️", key=f"pl_{row['track_id']}"):
                st.session_state['selected_track'] = row['track_id']
                st.session_state['view'] = 'detail'
                st.rerun()
        st.divider()