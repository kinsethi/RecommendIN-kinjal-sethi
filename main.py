import json
import streamlit as st #imported streamlit python pacckage
import pickle
import pandas as pd
import requests
from PIL import Image
import hashlib
import sqlite3
from streamlit_option_menu import option_menu
import hydralit_components as hc
from streamlit_lottie import st_lottie

#icon displayed in the tab bar
img = Image.open('Icon.png')
#opened page
st.set_page_config(page_title='RecommendIn', page_icon=img,layout='wide',initial_sidebar_state='collapsed')
if "key" not in st.session_state:
    st.session_state.key = False
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) #markdown for linking

user = ""


# Security
# passlib,hashlib,bcrypt,scrypt



#password for login page
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


# DB Management

conn = sqlite3.connect('data.db')
c = conn.cursor()


# DB  Functions
# all functions for sidebar
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data

#main function for the home page
def initialhome():
    with st.container():
        st.markdown("<h4 style='text-align: right; color: purple;'>New User</h4> ",
                    unsafe_allow_html=True)
        with st.container():
            movies_list = pickle.load(open('movie_list.pkl', 'rb'))
            movies = pd.DataFrame(movies_list)
            st.title('Welcome To RecommendIn')
            popular = pickle.load(open('nes.pkl', 'rb'))
            popularmovie = pd.DataFrame(popular)
            similarity = pickle.load(open('similarity.pkl', 'rb'))
            selected_movie_name = st.selectbox(
                '                  ',
                movies['title'].values)
            st.button('Recommend',disabled=True)
            st.markdown("Kindly Login to use our services")

#login in home
def loginhome(username):
    def fetch_poster(movie_id): #fetching posters for recommended movies
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{''}?api_key=6aa985dbeded2bc870b63cd6692f4eb6&language=en-US'.format(
                movie_id))
        data = response.json()
        return "https://image.tmdb.org/t/p/w200/" + data['poster_path']

    def fetch_title(movie_id): #fetching titles for recommended movies
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{''}?api_key=6aa985dbeded2bc870b63cd6692f4eb6&language=en-US'.format(
                movie_id))
        data = response.json()
        # return data['genres'][2]['name']
        return data['title']

    def fetch_genreid(nameGenre):  #fetching genres for recommended movies
        response = requests.get(
            'https://api.themoviedb.org/3/genre/movie/list?api_key=6aa985dbeded2bc870b63cd6692f4eb6&language=en-US')
        data = response.json()
        for i in range(0, 20):
            if data['genres'][i]['name'] == nameGenre:
                return data['genres'][i]['id']

    def print(name, poster):  # setting column spaces for recommended movies
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(name[0])
            st.image(poster[0])
        with col2:
            st.text(name[1])
            st.image(poster[1])
        with col3:
            st.text(name[2])
            st.image(poster[2])
        with col4:
            st.text(name[3])
            st.image(poster[3])
        with col5:
            st.text(name[4])
            st.image(poster[4])

    def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)

    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    def upcomingMovie():  # defines feature of upcoming movies
        st.title("Upcoming Movies")
        response = requests.get(
            'https://api.themoviedb.org/3/movie/upcoming?api_key=6aa985dbeded2bc870b63cd6692f4eb6&language=en-US&page=1')
        data = response.json()
        list = []
        listPosters = []
        for i in range(0,5):
             list.append(data['results'][i]['original_title'])
             listPosters.append(fetch_poster(data['results'][i]['id']))
        print(list,listPosters)
        with st.expander("See More"): #expander will allow to see more movies according to the recommendation
            j = 6
            while j < 15:
                list = []
                listPosters = []
                for i in range(j,j+5):
                    list.append(data['results'][i]['original_title'])
                    listPosters.append(fetch_poster(data['results'][i]['id']))
                print(list,listPosters)
                j = j + 5

    def popularmovies(): # section defined for the feature of popular movies
        allmovies = []
        allmoviesposters = []
        distances = list(enumerate(popularmovie['original_title']))
        for i in distances[0:5]:
            movieid = popularmovie.iloc[i[0]].id
            title = fetch_title(movieid)
            # movie_title = popularmovie[['original_title']]
            # st.text(movie_title)
            # st.text(movieid)
            allmovies.append(title)
            allmoviesposters.append(fetch_poster(movieid))
        print(allmovies, allmoviesposters)
        with st.expander("See More"): #expander for more moives
            j = 6
            while j < 15:
                allmovies = []
                allmoviesposters = []
                for i in distances[j:j+5]:
                    movie_id = movies.iloc[i[0]].movie_id
                    movieid = popularmovie.iloc[i[0]].id
                    title = fetch_title(movieid)
                    # movie_title = popularmovie[['original_title']]
                    # st.text(movie_title)
                    # st.text(movieid)
                    allmovies.append(title)
                    allmoviesposters.append(fetch_poster(movieid))
                print(allmovies, allmoviesposters)
                j = j + 5

    def userGenreRecommend(selectedMovie): #function for recommendation according to your moive's genre
        mvid = movies[movies['title'] == selectedMovie]['movie_id'].to_json()
        end = 0
        start = 0
        for e in mvid:
            if e == ':':
                break
            else:
                start = start + 1
        for e in mvid:
            if e == '}':
                break
            else:
                end = end + 1
        calcid = mvid[start + 1:end]
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{''}?api_key=6aa985dbeded2bc870b63cd6692f4eb6&language=en-US'.format(
                calcid))
        data = response.json()
        st.title("More {} Movies".format(data['genres'][0]['name']))
        response = requests.get(
            'https://api.themoviedb.org/3/discover/movie?api_key=6aa985dbeded2bc870b63cd6692f4eb6&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_genres={''}'.format(
                data['genres'][0]['id']))
        data = response.json()
        userMovies = []
        userMoviesPoster = []
        for i in range(0, 5):
            userMovies.append(data['results'][i]['original_title'])
            userMoviesPoster.append(fetch_poster(data['results'][i]['id']))
        print(userMovies, userMoviesPoster)
        # with st.expander("See More"):
        #     j = 6
        #     while j < 15:
        #         userMovies = []
        #         userMoviesPoster = []
        #         for i in range(j,j+5):
        #             userMovies.append(data['results'][i]['original_title'])
        #             userMoviesPoster.append(fetch_poster(data['results'][i]['id']))
        #         print(userMovies, userMoviesPoster)
        #         j = j + 5

    def aboutUs():  # about us section telling about the app
        st.title('About Us')
        st.write('''
        RecommendIn is a MOVIE recommendation system which recommends you according to your choice.
        It is totally user friendly and it is for helping our users to find their movies according to their tastes.   
        we recommend you movies according to three algorithms that are weighted hybrid , weighted average and nearest 
        neighour. our website provides you with different recommendations like recommending on the basis of your choice,
        people recommendation, according to genre, cast, crew, release_date, popularity etc. We also provide astonishing 
        features like telling you about upcoming movies and recommending the best for the same.
        We have different features like subscribe button which will allow you to get notifications whenever best 
        recommendations come your way.
        It is a fully functional website which solves your problem  "Which movie is next"?         
        ''')


      # Lottie Files: https://lottiefiles.com/
        # animation



        lottie_coding = load_lottiefile("9103-entertainment.json")  # replace link to local lottie file
        lottie_hello = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_CTaizi.json")

        st_lottie(
            lottie_hello,
            speed=1,
            reverse=False,
            loop=True,
            quality="low",  # medium ; high

            height=200,
            width=200,
            key=None,
        )



    def contactUs():  # contact us section telling about the app
        # contact us
        st.title('Contact Us')
        st.write('''
        If you have general questions about your account or how to contact customer service for assistance, 
        please visit our online help center at help.recommendin.com. For questions specifically about this Privacy Statement, 
        or our use of your personal information, cookies or similar technologies, please contact our Data Protection Officer/Privacy
        Office by email at privacy@recommendin.com

        The data controller of your personal information is recommendin Entertainment Services India LLP. 
        Please note that if you contact us to assist you, for your safety and ours we may need to authenticate your 
        identity before fulfilling your request.
        
        Contact_no: 1-2093847
        Email: RecommendIn@gmail.com
        ''')
        # animation for contact us section


        lottie_coding = load_lottiefile("63228-man-watching-a-movie.json")  # replace link to local lottie file
        lottie_hello = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_qm8eqzse.json")

        st_lottie(
            lottie_hello,
            speed=1,
            reverse=False,
            loop=True,
            quality="low",  # medium ; high
              # canvas
            height=200,
            width=200,
            key=None,
        )

    def genreRecommend(currGenre, currGenreId): # function defined for genres
        st.title("Popular {} Movies".format(currGenre))
        response = requests.get(
            'https://api.themoviedb.org/3/discover/movie?api_key=6aa985dbeded2bc870b63cd6692f4eb6&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_genres={''}'.format(
                currGenreId))
        data = response.json()
        currMovies = []
        currMoviesPoster = []
        for i in range(0, 5):
            currMovies.append(data['results'][i]['original_title'])
            currMoviesPoster.append(fetch_poster(data['results'][i]['id']))
        print(currMovies, currMoviesPoster)

# main algorithms (weighted average)
    def recommend(movie):
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

        recommended_movies = []
        recommended_movies_posters = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))
        print(recommended_movies, recommended_movies_posters)
        with st.expander("See More"):
            j = 6
            while j < 20:
                recommended_movies = []
                recommended_movies_posters = []
                for i in distances[j:j+5]:
                    movie_id = movies.iloc[i[0]].movie_id
                    recommended_movies.append(movies.iloc[i[0]].title)
                    recommended_movies_posters.append(fetch_poster(movie_id))
                print(recommended_movies, recommended_movies_posters)
                j = j + 5
    # import files
    movies_list = pickle.load(open('movie_list.pkl', 'rb'))
    movies = pd.DataFrame(movies_list)
    popular = pickle.load(open('nes.pkl', 'rb'))
    popularmovie = pd.DataFrame(popular)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    genre = pickle.load(open('genres.pkl', 'rb'))
    genres = pd.DataFrame(genre)
    cast = pickle.load(open('cast.pkl', 'rb'))
    cast_movie = pd.DataFrame(cast)
    release_date = pickle.load(open('release_date.pkl', 'rb'))
    release_date_movie = pd.DataFrame(release_date)

    with st.container():
        st.markdown("<h4 style='text-align: right; color: purple;'>{}</h4> ".format(username),
                    unsafe_allow_html=True)

        with st.container(): # Navigation bar at the top
            menu_data = [
                {'id': 'Most Watched Movies', 'icon': "far fa-copy", 'label': "Most Watched Movies", 'ttip': "Most Watched Movies"}, #Most Watched Movies
                {'id': 'Category', 'icon': "bi bi-bookmarks-fill", 'label': "Category", 'ttip': "Category"},# Category
                {'id': 'Upcoming_Movie', 'icon': "bi bi-film", 'label': "Upcoming_Movies", 'ttip': "Upcoming Movie"}, #Upcoming Movie
                {'id': 'About Us', 'icon': "bi bi-people-fill", 'label': "About Us", 'ttip': "About Us"}, #About Us
                {'id': 'Contact Us', 'icon': "bi bi-telephone", 'label': "Contact Us", 'ttip': "Contact Us"}, #Contact Us
                {'id': '', 'icon': "bi bi-facebook", 'label': "", 'ttip': "facebook"}, #facebook icon
                {'id': '', 'icon': "bi bi-instagram", 'label': "", 'ttip': "Instagram"}, #instagram icon
                {'id': '', 'icon': "bi bi-twitter", 'label': "", 'ttip': "twitter"} #twitter icon
            ]  # we would be showing only icons of facebook , instagram and twitter as it for project purpose.

            over_theme = {'txc_inactive': '#FFFFFF'} # theme for navigation bar
            menu_id = hc.nav_bar(
                menu_definition=menu_data,
                override_theme=over_theme,
                home_name='Home',
                login_name=None,
                hide_streamlit_markers=False,  # will show the st hamburger as well as the navbar now!
                sticky_nav=True,  # at the top or not
                sticky_mode='sticky',  # jumpy or not-jumpy, but sticky or pinned
            )

            if menu_id == "Home":

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.empty()
                with col2:
                    # lottie_coding = load_lottiefile("81986-movie.json")  # replace link to local lottie file
                    lottie_hello = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_khzniaya.json")

                    st_lottie(
                        lottie_hello,
                        speed=1,
                        reverse=False,
                        loop=False,
                        quality="low",  # medium ; high  # canvas
                        height=200,
                         width=200,
                        key=None,
                    )
                    st.title("RecommendIn")
                    st.markdown(
                        "<p style='font-family': Snell Roundhand;'text-align: center; color: white;'>Which movie comes next?</p>",
                        unsafe_allow_html=True)
                    # st.markdown("<h1 style='text-align: center; color: white;'>RecommendIn</h1>",
                    #             unsafe_allow_html=True)
                with col3:
                    st.empty()





                if st.button('Subscribe'): #subscribe button
                    st.write('You will get notifications for your recommendations!!!')

                selected_movie_name = st.selectbox(
                    '                  ',
                    movies['title'].values)
                if st.button('Recommend', disabled=False):
                    recommend(selected_movie_name)
                    userGenreRecommend(selected_movie_name)
                st.title("Most Watched Movies")
                popularmovies()
                genreRecommend('Action',fetch_genreid('Action')) # Action Movies
                genreRecommend('Drama',fetch_genreid('Drama'))   # Drama Movies
                genreRecommend('Comedy',fetch_genreid('Comedy')) # Comedy Movies
                genreRecommend('Horror',fetch_genreid('Horror')) # Horror Movies
                genreRecommend('Romance',fetch_genreid('Romance')) # Romance Movies
                aboutUs()
                contactUs()
            elif menu_id == "Most Watched Movies":
                st.title("Most Watched Movies")
                mnames, mposters = popularmovies()
                print(mnames,mposters)
            elif menu_id == "Category":
                genreRecommend('Action',fetch_genreid('Action')) # Action Movies
                genreRecommend('Drama',fetch_genreid('Drama'))
                genreRecommend('Comedy',fetch_genreid('Comedy'))
                genreRecommend('Horror',fetch_genreid('Horror'))
                genreRecommend('Romance',fetch_genreid('Romance'))
            elif menu_id == "Upcoming_Movie":
                upcomingMovie()
            elif menu_id == "About Us":
                aboutUs()
            elif menu_id == "Contact Us":
                contactUs()

def main(user):
    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        if st.session_state.key == False:
            initialhome()
        else:
            loginhome(user)

    elif choice == "Login":

        st.subheader("Login Section")

        username = st.text_input("User Name")
        user = username
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            # if password == '12345':
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))
            if result:
                st.session_state.key = True
                st.write("Logged In as {}. Hi {} Welcome to our App".format(username, username))
                st.session_state.key = True

            else:
                st.warning("Incorrect Username/Password")
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")


main(user)
