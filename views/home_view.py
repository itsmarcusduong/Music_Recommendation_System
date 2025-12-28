import streamlit as st
import pandas as pd
from modules import database, recommender

def show_home_page(data_artifacts):
    df_tracks, _, _, _, _ = data_artifacts
    
    # --- CSS CHO PHẦN GỢI Ý BÀI HÁT ---
    st.markdown("""
    <style>
    /* Style cho ảnh bài hát */
    .cover-img {
        border-radius: 8px;
        width: 100%;
        object-fit: cover;
    }
    /* Cắt bớt tên bài hát nếu quá dài */
    .truncate-text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-weight: bold;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # --- SIDEBAR (GIỮ NGUYÊN) ---
    with st.sidebar:
        st.markdown(f"<div class='user-box'>👤 {st.session_state['username']}</div>", unsafe_allow_html=True)
        
        if st.button("❤️ Thư viện của tôi"):
            st.session_state['view'] = 'library'
            st.rerun()

        if st.button("Đăng Xuất"):
            st.session_state['logged_in'] = False
            st.rerun()
        
        st.divider()
        st.write("### Nghe gần đây")
        history = database.get_user_history_list(st.session_state['username'])
        if not history.empty:
            hist_display = pd.merge(history, df_tracks[['track_id', 'track_name']], on='track_id', how='left')
            for _, row in hist_display.tail(5).iterrows():
                if st.button(f"🎵 {row['track_name']}", key=f"hist_{row['track_id']}"):
                    st.session_state['selected_track'] = row['track_id']
                    st.session_state['view'] = 'detail'
                    database.log_interaction(st.session_state['username'], row['track_id'], action_type='play')
                    st.rerun()
        else:
            st.caption("Chưa có bài hát nào.")

    # --- MAIN CONTENT ---
    st.title("Home 🏠")
    
    # 1. TÌM KIẾM
    st.write("### 🔍 Tìm kiếm")
    all_songs = [""] + list(df_tracks['track_name'].unique())
    selected_song = st.selectbox("Chọn bài hát...", all_songs, index=0, label_visibility="collapsed")
    
    if selected_song and selected_song != "":
        try:
            tid = df_tracks[df_tracks['track_name'] == selected_song].iloc[0]['track_id']
            st.session_state['selected_track'] = tid
            st.session_state['view'] = 'detail'
            database.log_interaction(st.session_state['username'], tid, action_type='search')
            st.rerun()
        except: st.error("Lỗi tìm kiếm")

    st.markdown("---")

    # 2. CARDS PLAYLIST (GIỮ NGUYÊN)
    st.subheader("Made For You 🎧")
    c1, c2, c3, c4 = st.columns(4)
    
# Discover Weekly
    with c1:
        st.image("https://misc.scdn.co/liked-songs/liked-songs-300.png", width=150)
        st.write("**Discover Weekly**")
        if st.button("Mở Playlist 🚀"):
            with st.spinner("Đang phối nhạc..."):
                pl = recommender.create_discover_playlist(st.session_state['username'], data_artifacts)
                st.session_state['playlist_name'] = "Discover Weekly"
                st.session_state['playlist_tracks'] = pl
                st.session_state['view'] = 'playlist'
                st.rerun()

    # Top Trending
    with c2:
        st.image("https://charts-images.scdn.co/assets/locale_en/regional/weekly/region_vn_default.jpg", width=150)
        st.write("**Top Popular**")
        if st.button("Mở Playlist 🔥"):
            pl = df_tracks.sort_values(by='popularity', ascending=False).head(30)
            st.session_state['playlist_name'] = "Top Trending"
            st.session_state['playlist_tracks'] = pl
            st.session_state['view'] = 'playlist'
            st.rerun()

    # Mood Mix
    with c3:
        st.image("https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=500&auto=format&fit=crop&q=60", width=150)
        st.write("**Mood Mix**")
        mood = st.selectbox("Mood", ["Happy ⚡", "Sad 🌧️", "Chill ☕"], label_visibility="collapsed")
        if st.button("Mở Playlist 🎭"):
            if "Happy" in mood: cond = (df_tracks['valence'] > 0.6)
            elif "Sad" in mood: cond = (df_tracks['valence'] < 0.4)
            else: cond = (df_tracks['acousticness'] > 0.5)
            pl = df_tracks[cond].sample(20)
            st.session_state['playlist_name'] = f"{mood} Mix"
            st.session_state['playlist_tracks'] = pl
            st.session_state['view'] = 'playlist'
            st.rerun()
            
    # Thư viện
    with c4:
        st.image("https://t.scdn.co/images/3099b3803ad9496896c43f22fe9be8c4.png", width=150)
        st.write("**Liked Songs**")
        if st.button("Xem Thư viện ❤️"):
            st.session_state['view'] = 'library'
            st.rerun()

    st.markdown("---")

    # ==================================================
    # 3. 🔥 PHẦN MỚI: GỢI Ý BÀI HÁT (QUICK PICKS) 🔥
    # ==================================================
    
    # Logic: Lấy gợi ý cá nhân, nếu không có thì lấy Top Popular
    personal_recs = recommender.get_personal_recommendations(st.session_state['username'], data_artifacts)
    
    if personal_recs is not None and not personal_recs.empty:
        st.subheader("Quick Picks cho bạn ⚡")
        display_songs = personal_recs.head(10) # Lấy 10 bài
    else:
        st.subheader("Đang thịnh hành 🚀")
        display_songs = df_tracks.sort_values(by='popularity', ascending=False).head(10)
        display_songs = display_songs.sample(frac=1) # Trộn ngẫu nhiên cho đỡ chán

    # Hiển thị dạng lưới (Grid) 5 cột x 2 dòng
    for i in range(0, len(display_songs), 5):
        cols = st.columns(5)
        batch = display_songs.iloc[i:i+5]
        
        for idx, (_, row) in enumerate(batch.iterrows()):
            with cols[idx]:
                # Ảnh bìa (Dùng ảnh random theo ID để tạo sự khác biệt giả lập)
                # Lưu ý: Vì dataset không có ảnh thật nên ta dùng placeholder đẹp
                img_url = f"https://picsum.photos/seed/{row['track_id']}/200/200"
                st.image(img_url, width="stretch")
                
                # Tên bài hát (Cắt ngắn nếu dài)
                short_name = (row['track_name'][:20] + '..') if len(row['track_name']) > 20 else row['track_name']
                st.write(f"**{short_name}**")
                
                # Tên ca sĩ
                short_artist = (row['artists'][:15] + '..') if len(row['artists']) > 15 else row['artists']
                st.caption(short_artist)
                
                # Nút Play
                if st.button("▶️ Play", key=f"qp_{row['track_id']}"):
                    st.session_state['selected_track'] = row['track_id']
                    st.session_state['view'] = 'detail'
                    database.log_interaction(st.session_state['username'], row['track_id'], action_type='play')
                    st.rerun()
        
        st.write("") # Tạo khoảng cách giữa các hàng