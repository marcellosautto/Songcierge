
import os
import sys
import discord
from discord import embeds
from discord import user
import spotipy
from flask import Flask, session, request, redirect
from flask_session import Session
import uuid
# from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv(".env")


#initialize flask session
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '..flask_session/'
Session(app)


#initialize cache directory
caches_directory = './.spotipy_caches/'

if not os.path.exists(caches_directory):
    os.makedirs(caches_directory)

#getter for cache path
def get_session_cache_path():
    return caches_directory + session.get('uuid')

# establish connection to discord and spotify web api
discord_client = discord.Client()

scope = 'user-read-private,user-top-read'
# spotipy_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('spotipy_auth_manager_manager_manager_manager_ID'),client_secret=os.getenv('spotipy_auth_manager_manager_manager_manager_SECRET'))
# spotify_ranges = ['short_term', 'medium_term', 'long_term']

# print msg when the bot is online
@discord_client.event
async def on_ready():
    print('Logged in as {0.user}'.format(discord_client))

# free cache of user client if they go offline
@discord_client.event
async def on_member_update(before, after, message):
    if str(before.status) == "online":
        if str(after.status) == "offline":
            try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
                os.remove(get_session_cache_path())
                session.clear()
            except OSError as e:
                await message.channel.send("Error: %s - %s." % (e.filename, e.strerror))

# The bot will say hello if the '$hello' command is executed
@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    ############# HANDLE AUTHENTICATION CONDITIONS #############

    # Assign uuid to unknown user
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=get_session_cache_path())
    spotipy_auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                                cache_handler=cache_handler,
                                                redirect_uri="https://git.heroku.com/songcierge-bot.git/", 
                                                show_dialog=True)
    spotify_username = spotipy_auth_manager.current_user()['display_name']

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        spotipy_auth_manager.get_access_token(request.args.get("code"))
        return

    if not spotipy_auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = spotipy_auth_manager.get_authorize_url()
        await message.channel.send('Sign in to Spotify here ---> {auth_url}')


    spotipy_client = spotipy.Spotify(auth_manager=spotipy_auth_manager)

    # Print playlists
    if message.content.startswith('$playlists'):

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=get_session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return

        spotipy_client = spotipy.Spotify(auth_manager=auth_manager)

        playlists =spotipy_client.current_user_playlists()
        embeded_message = discord.Embed(title="{}'s Playlists".format(spotify_username), description="", color=0x50c878)
        embeded_message.set_thumbnail(url=spotipy_client.current_user()['images'][0]['url'])

        for i, playlist in enumerate(playlists['items']):
            embeded_message.add_field(name=str(str(i+1) + ". "),value=playlist['name'], inline=True)
 
            
        await message.channel.send(embed=embeded_message)
    
    # Print favorite songs and artists
    if message.content.startswith('$favorites'):
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=get_session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return

        spotipy_client = spotipy.Spotify(auth_manager=auth_manager)

        embeded_message = discord.Embed(title="{}'s Favorites".format(spotify_username), description="", color=0x50c878)
        embeded_message.set_thumbnail(url=spotipy_client.current_user()['images'][0]['url'])
        embeded_message.add_field(name="Top Tracks: ", value="---------------", inline=False)

        results = spotipy_client.current_user_top_tracks(time_range='medium_term', limit=5)

        for i, track in enumerate(results['items']):
            embeded_message.add_field(name=str(str(i+1) + ". "),value="{song} by {artist}".format(song = track['name'], artist = track['artists'][0]['name']), inline=False)

        
        embeded_message.add_field(name="Top Artists: ", value="---------------", inline=False)

        results = spotipy_client.current_user_top_artists(time_range='medium_term', limit=5)
        for i, artist in enumerate(results['items']):
            embeded_message.add_field(name=str(str(i+1) + ". "),value="{artist}".format(artist = artist['name']), inline=False)
            
        await message.channel.send(embed=embeded_message)

    # Recommend tracks to the user based on their top track and artist
    if message.content.startswith('$recommend'):

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=get_session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return

        spotipy_client = spotipy.Spotify(auth_manager=auth_manager)

        embeded_message = discord.Embed(title="Track and Artist Suggestions for {}".format(spotify_username), description="", color=0x50c878)
        embeded_message.set_thumbnail(url=spotipy_client.current_user()['images'][0]['url'])


        top_tracks = spotipy_client.current_user_top_tracks(time_range='medium_term', limit=5)['items']
        top_artists = results = spotipy_client.current_user_top_artists(time_range='medium_term', limit=5)['items']

        recommendations = spotipy_client.recommendations(seed_artists=[top_artists[0]['id']], seed_tracks=[top_tracks[0]['id']], limit=20)

        embeded_message.add_field(name="Recommended Tracks: ", value="---------------", inline=False)
        for i,track in enumerate(recommendations['tracks']):
            embeded_message.add_field(name=str(str(i+1) + ". "),value="{song} by {artist} - {preview_url}".format(song = track['name'], artist = track['artists'][0]['name'], preview_url = track['preview_url']), inline=False)

        await message.channel.send(embed=embeded_message)


# run bot with login token
discord_client.run(os.getenv('TOKEN'))