import streamlit as st
import pandas as pd
from modules import database

def show_library_page(data_artifacts):
    df_tracks, _, _, _, _ = data_artifacts
    username = st.session_state['username']
    
    if st.button("⬅️ Về trang chủ"):
        st.session_state['view'] = 'home'
        st.rerun()
        
    st.markdown(f"""
    <div style="background: linear-gradient(180deg, #4A00E0 0%, #121212 100%); padding: 30px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 40px;">❤️ Thư viện của tôi</h1>
        <p>Danh sách bài hát yêu thích của {username}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Lấy danh sách ID đã thích
    liked_df = database.get_user_history_list(username)
    
    if liked_df.empty:
        st.info("Thư viện trống. Hãy 'Thả tim' vài bài hát nhé!")
        return

    # Join với thông tin bài hát đầy đủ
    # Chỉ lấy các cột cần thiết từ df_tracks
    library_full = pd.merge(liked_df, df_tracks[['track_id', 'track_name', 'artists', 'track_genre', 'duration_ms']], on='track_id', how='left')
    
    # Đảo ngược để bài mới thích lên đầu
    library_full = library_full.iloc[::-1]

    # --- HEADER ---
    col1, col2, col3, col4, col5 = st.columns([1, 4, 3, 1, 1])
    col1.write("#")
    col2.write("BÀI HÁT")
    col3.write("NGHỆ SĨ")
    col4.write("NGHE")
    col5.write("XÓA")
    st.divider()
    
    # --- LIST ---
    for idx, row in library_full.reset_index(drop=True).iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([1, 4, 3, 1, 1])
            c1.write(f"{idx + 1}")
            c2.write(f"**{row['track_name']}**")
            c3.write(row['artists'])
            
            # Nút Nghe
            if c4.button("▶️", key=f"lib_play_{row['track_id']}"):
                st.session_state['selected_track'] = row['track_id']
                st.session_state['view'] = 'detail'
                st.rerun()
            
            # Nút Xóa (Unlike)
            if c5.button("❌", key=f"lib_del_{row['track_id']}"):
                database.remove_rating(username, row['track_id'])
                st.toast(f"Đã xóa {row['track_name']}")
                st.rerun()
                
        st.divider()