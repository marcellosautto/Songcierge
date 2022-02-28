import os
from threading import Thread
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
import uuid

app=Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'

if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    with app.test_request_context('/'):
        if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
            session['uuid'] = str(uuid.uuid4())

        return caches_folder + session.get('uuid')

def handle_redirect():
    return redirect("/")

@app.route('/')
def home():
   
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-read-private,user-top-read',
                                                cache_handler=cache_handler, 
                                                show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 4. Signed in, display data
    # return f'<h2>Hi {spotify.me()["display_name"]}, ' \
    #        f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
    #        f'<a href="/playlists">my playlists</a> | ' \
    #        f'<a href="/currently_playing">currently playing</a> | ' \
	# 	   f'<a href="/current_user">me</a>' \
    return "Songcierge is Online!"

def run():
    app.run(host="0.0.0.0", port=8080)

def run_thread():
    t = Thread(target=run)
    t.start