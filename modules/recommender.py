import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import hstack
import streamlit as st
from modules import database

@st.cache_resource
def load_data_and_models():
    try:
        # Load từ folder data/
        df = pd.read_csv('data/spotify_tracks_final.csv')
        df_inter = pd.read_csv('data/user_interactions.csv')
        df_norm = pd.read_csv('data/spotify_features_normalized.csv')
        
        numeric_cols = ['danceability', 'energy', 'valence', 'tempo', 'acousticness', 'instrumentalness', 'popularity']
        matrix_audio = df_norm[numeric_cols].values
        
        tfidf = TfidfVectorizer(stop_words='english')
        matrix_genre = tfidf.fit_transform(df['track_genre'].astype(str))
        matrix_genre = matrix_genre * 5.0 # Trọng số Genre x5
        
        final_features = hstack([matrix_audio, matrix_genre])
        
        model_cbr = NearestNeighbors(n_neighbors=50, metric='cosine', algorithm='brute')
        model_cbr.fit(final_features)
        
        user_item_matrix = df_inter.pivot_table(index='track_id', columns='user_id', values='rating').fillna(0)
        model_cf = NearestNeighbors(n_neighbors=50, metric='cosine', algorithm='brute')
        model_cf.fit(user_item_matrix)
        
        return df, final_features, user_item_matrix, model_cbr, model_cf
    except FileNotFoundError:
        return None, None, None, None, None

def get_recommendations(track_id, data_artifacts, alpha=0.85):
    df_tracks, final_features, user_item_matrix, model_cbr, model_cf = data_artifacts
    
    idx = df_tracks[df_tracks['track_id'] == track_id].index[0]
    dist_cbr, ind_cbr = model_cbr.kneighbors(final_features.getrow(idx), n_neighbors=21)
    recs_cbr = df_tracks.iloc[ind_cbr.flatten()[1:]][['track_id']].copy()
    recs_cbr['cbr_score'] = 1 - dist_cbr.flatten()[1:]
    
    recs_cf = pd.DataFrame(columns=['track_id', 'cf_score'])
    if track_id in user_item_matrix.index:
        track_vec = user_item_matrix.loc[track_id].values.reshape(1, -1)
        dist_cf, ind_cf = model_cf.kneighbors(track_vec, n_neighbors=21)
        ids_cf = [user_item_matrix.index[i] for i in ind_cf.flatten()[1:]]
        recs_cf = pd.DataFrame({'track_id': ids_cf, 'cf_score': 1 - dist_cf.flatten()[1:]})
    
    hybrid = pd.merge(recs_cbr, recs_cf, on='track_id', how='outer').fillna(0).infer_objects(copy=False)
    hybrid['final_score'] = (alpha * hybrid['cbr_score']) + ((1-alpha) * hybrid['cf_score'])
    
    final = pd.merge(hybrid, df_tracks, on='track_id', how='left')
    return final.sort_values(by='final_score', ascending=False).head(10)

def get_personal_recommendations(username, data_artifacts):
    last_id = database.get_last_interaction(username)
    if last_id is None: return None
    return get_recommendations(last_id, data_artifacts)

def create_discover_playlist(username, data_artifacts, n_songs=20):
    df_tracks, _, _, _, _ = data_artifacts
    history = database.get_user_history_list(username)
    
    if history.empty:
        return df_tracks.sort_values(by='popularity', ascending=False).head(n_songs)
    
    last_tracks = history.tail(3)['track_id'].values
    playlist = pd.DataFrame()
    for tid in last_tracks:
        recs = get_recommendations(tid, data_artifacts, alpha=0.8)
        playlist = pd.concat([playlist, recs])
    
    playlist = playlist.drop_duplicates(subset='track_id')
    playlist = playlist[~playlist['track_id'].isin(history['track_id'])]
    
    if len(playlist) < n_songs:
        popular = df_tracks.sort_values(by='popularity', ascending=False).head(n_songs)
        playlist = pd.concat([playlist, popular]).drop_duplicates(subset='track_id')
        
    return playlist.sample(n=min(len(playlist), n_songs))