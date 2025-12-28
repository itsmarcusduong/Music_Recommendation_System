import streamlit as st
import streamlit.components.v1 as components
from modules import database, recommender

def show_detail_page(data_artifacts):
    df_tracks, _, _, _, _ = data_artifacts
    track_id = st.session_state['selected_track']
    song_info = df_tracks[df_tracks['track_id'] == track_id].iloc[0]

    # Nút quay lại thông minh (Nếu từ library thì quay về library)
    if st.button("⬅️ Quay lại"):
        st.session_state['view'] = 'home'
        st.rerun()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"## 💿 {song_info['track_name']}")
        st.caption(f"{song_info['artists']} • {song_info['track_genre']}")
        
        # Embed Player
        embed_url = f"https://open.spotify.com/embed/track/{track_id}?utm_source=generator"
        components.html(f'<iframe style="border-radius:12px" src="{embed_url}" width="100%" height="352" frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>', height=360)
        
        # 🔥 LOGIC LIKE / UNLIKE
        user_hist = database.get_user_history_list(st.session_state['username'])
        is_liked = track_id in user_hist['track_id'].values if not user_hist.empty else False
        
        if is_liked:
            # Nếu đã thích -> Hiện nút Bỏ thích (Màu đỏ/xám)
            if st.button("💔 Bỏ thích"):
                database.remove_rating(st.session_state['username'], track_id)
                st.toast("Đã xóa khỏi thư viện!")
                st.rerun() # Load lại để cập nhật trạng thái nút
        else:
            # Nếu chưa thích -> Hiện nút Thả tim
            if st.button("🤍 Thả tim"):
                database.add_rating(st.session_state['username'], track_id)
                database.log_interaction(st.session_state['username'], track_id, action_type='like')
                st.toast("Đã thêm vào danh sách yêu thích!")
                st.rerun()

    with col2:
        st.write("### Gợi ý tương tự")
        recs = recommender.get_recommendations(track_id, data_artifacts)
        for _, row in recs.iterrows():
            with st.container():
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{row['track_name']}**")
                if c2.button("Nghe", key=f"rec_{row['track_id']}"):
                    st.session_state['selected_track'] = row['track_id']
                    database.log_interaction(st.session_state['username'], row['track_id'], action_type='play')
                    st.rerun()
            st.divider()