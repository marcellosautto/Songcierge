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
    return caches_folder + session.get('uuid')

@app.route('/')
def home():
    return "Songcierge is Online!"

def run():
    app.run(host="0.0.0.0", port=8080)

def run_thread():
    t = Thread(target=run)
    t.start