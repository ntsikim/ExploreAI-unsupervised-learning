import streamlit as st
import pandas as pd
from surprise import SVD, Dataset, Reader

# --- Load Data ---
@st.cache_data
def load_data():
    anime_df = pd.read_csv("anime.csv")
    train_df = pd.read_csv("train.csv")
    return anime_df, train_df

anime_df, train_df = load_data()

# --- Train Model (only once) ---
@st.cache_resource
def train_model():
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(train_df[['user_id', 'anime_id', 'rating']], reader)
    trainset = data.build_full_trainset()
    model = SVD()
    model.fit(trainset)
    return model

model = train_model()

# --- App Interface ---
st.title("🎌 Anime Recommender System")
st.write("Enter a user ID to get anime recommendations based on their past ratings.")

user_input = st.number_input("User ID:", min_value=1, max_value=train_df['user_id'].max(), value=1)

# Get all anime IDs
user_seen = train_df[train_df['user_id'] == user_input]['anime_id'].tolist()
unseen_anime = anime_df[~anime_df['anime_id'].isin(user_seen)]

# Predict ratings for unseen anime
st.write("Generating recommendations...")
unseen_anime['predicted_rating'] = unseen_anime['anime_id'].apply(lambda x: model.predict(user_input, x).est)

# Top 5 Recommendations
top_recs = unseen_anime.sort_values(by='predicted_rating', ascending=False).head(5)

st.subheader("Top 5 Recommended Anime:")
st.table(top_recs[['name', 'genre', 'type', 'predicted_rating']].reset_index(drop=True))
