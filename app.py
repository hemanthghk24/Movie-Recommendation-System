import streamlit as st
import pickle
import requests
import ast

# ---- Page Styling ----
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://i.postimg.cc/wvtpvZRV/movie.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(8px);
        z-index: -1;
    }

    h1, h2, h3, h4, h5, h6, p, label, .stSelectbox, .stButton {
        color: white !important;
        text-shadow: 1px 1px 2px #000000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Load Data ----
movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))

# Ensure genres are in list format
movies['genres'] = movies['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# ---- TMDb Poster Fetch ----
api_key = "8265bd1679663a7ea12ac168da84d2e8"  # Ideally store in st.secrets

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Error"

# ---- Genre Filtering ----
all_genres = sorted({genre for sublist in movies['genres'] for genre in sublist})
selected_genres = st.multiselect("🎬 Filter by Genre(s):", all_genres)

# Filter movie list
if selected_genres:
    filtered_movies = movies[movies['genres'].apply(lambda g: any(genre in g for genre in selected_genres))]
else:
    filtered_movies = movies

movies_list = filtered_movies['title'].values

# ---- UI ----
st.header("🎥 Movie Recommendation System")

selected_movie = st.selectbox("📽️ Select a movie:", movies_list)

# ---- Recommendation Function ----
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distance[1:]:
        movie_data = movies.iloc[i[0]]
        if not selected_genres or any(genre in movie_data['genres'] for genre in selected_genres):
            recommended_movie_names.append(movie_data['title'])
            recommended_movie_posters.append(fetch_poster(movie_data['id']))
        if len(recommended_movie_names) == 5:
            break

    return recommended_movie_names, recommended_movie_posters

# ---- Button & Display ----
if st.button("🔍 Recommend"):
    movie_name, movie_poster = recommend(selected_movie)

    if movie_name:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(movie_name[0])
            st.image(movie_poster[0])
        with col2:
            st.text(movie_name[1])
            st.image(movie_poster[1])
        with col3:
            st.text(movie_name[2])
            st.image(movie_poster[2])
        with col4:
            st.text(movie_name[3])
            st.image(movie_poster[3])
        with col5:
            st.text(movie_name[4])
            st.image(movie_poster[4])
    else:
        st.warning("No matching recommendations found for the selected genres.")

