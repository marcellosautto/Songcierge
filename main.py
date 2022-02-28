
import os
import sys
import discord
from discord import embeds
from discord import user
from discord.ext import commands
# import asyncio
# import motor.motor_asyncio
import spotipy
import uuid
import logging
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv(".env")

# Local code
from flask_app import run_thread

#initialize cache directory
caches_directory = './.spotipy_caches/'
scope = 'user-read-private,user-top-read'

# establish connection to discord and spotify web api
discord_bot = commands.Bot(command_prefix='!')
cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=caches_directory)
spotipy_auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,cache_handler=cache_handler,redirect_uri='https://songcierge-bot.herokuapp.com/callback', show_dialog=True)
spotipy_client = spotipy.Spotify(auth_manager=spotipy_auth_manager)

# spotipy_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('spotipy_auth_manager_manager_manager_manager_ID'),client_secret=os.getenv('spotipy_auth_manager_manager_manager_manager_SECRET'))
# spotify_ranges = ['short_term', 'medium_term', 'long_term']


# print msg when the bot is online
@discord_bot.event
async def on_ready():
    # spotify_username = spotipy_auth_manager.current_user()['display_name']
    print('Logged in as {0.user}'.format(discord_bot))

# free cache of user client if they go offline
# @discord_bot.event
# async def on_member_update(before, after, message):
#     if str(before.status) == "online":
#         if str(after.status) == "offline":
#             try:
#         # Remove the CACHE file (.cache-test) so that a new user can authorize.
#                 os.remove(get_session_cache_path())
#                 session.clear()
#             except OSError as e:
#                 await message.channel.send("Error: %s - %s." % (e.filename, e.strerror))

@discord_bot.command()
async def hello(ctx):
    username = ctx.message.author.name
    await ctx.send(f'Hello, {username}!')

 # Print playlists
@discord_bot.command()
async def playlists(ctx):

    # spotipy_client = spotipy.Spotify(auth_manager=spotipy_auth_manager)
    username = ctx.message.author.name
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=)
    spotipy_auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,cache_handler=cache_handler,redirect_uri='https://songcierge-bot.herokuapp.com/callback', show_dialog=True)
    spotipy_client = spotipy.Spotify(auth_manager=spotipy_auth_manager)

    if not spotipy_auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        spotipy_auth_manager.get_cached_token()

    playlists=spotipy_client.current_user_playlists()
    embeded_message = discord.Embed(title="{}'s Playlists".format(username), description="", color=0x50c878)
    embeded_message.set_thumbnail(url=spotipy_client.current_user()['images'][0]['url'])

    for i, playlist in enumerate(playlists['items']):
        embeded_message.add_field(name=str(str(i+1) + ". "),value=playlist['name'], inline=True)
 
            
    await ctx.send(embed=embeded_message)

# Print favorite songs and artists
@discord_bot.command()
async def favorites(ctx):

    username = ctx.message.author.name
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=caches_directory)
    spotipy_auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,cache_handler=cache_handler,redirect_uri='https://songcierge-bot.herokuapp.com/callback', show_dialog=True)
    spotipy_client = spotipy.Spotify(auth_manager=spotipy_auth_manager)

    embeded_message = discord.Embed(title="{}'s Favorites".format(username), description="", color=0x50c878)
    embeded_message.set_thumbnail(url=spotipy_client.current_user()['images'][0]['url'])
    embeded_message.add_field(name="Top Tracks: ", value="---------------", inline=False)

    results = spotipy_client.current_user_top_tracks(time_range='medium_term', limit=5)

    for i, track in enumerate(results['items']):
        embeded_message.add_field(name=str(str(i+1) + ". "),value="{song} by {artist}".format(song = track['name'], artist = track['artists'][0]['name']), inline=False)

        
    embeded_message.add_field(name="Top Artists: ", value="---------------", inline=False)

    results = spotipy_client.current_user_top_artists(time_range='medium_term', limit=5)
    for i, artist in enumerate(results['items']):
        embeded_message.add_field(name=str(str(i+1) + ". "),value="{artist}".format(artist = artist['name']), inline=False)
            
    await ctx.send(embed=embeded_message)

#recommend songs to user
@discord_bot.command()
async def recommend(ctx):
        # Recommend tracks to the user based on their top track and artist

    username = ctx.message.author.name
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=caches_directory)
    spotipy_auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,cache_handler=cache_handler,redirect_uri='https://songcierge-bot.herokuapp.com/callback', show_dialog=True)
    spotipy_client = spotipy.Spotify(auth_manager=spotipy_auth_manager)
    
    embeded_message = discord.Embed(title="Track and Artist Suggestions for {}".format(username), description="", color=0x50c878)
    embeded_message.set_thumbnail(url=spotipy_client.current_user()['images'][0]['url'])


    top_tracks = spotipy_client.current_user_top_tracks(time_range='medium_term', limit=5)['items']
    top_artists = results = spotipy_client.current_user_top_artists(time_range='medium_term', limit=5)['items']

    recommendations = spotipy_client.recommendations(seed_artists=[top_artists[0]['id']], seed_tracks=[top_tracks[0]['id']], limit=20)

    embeded_message.add_field(name="Recommended Tracks: ", value="---------------", inline=False)
    for i,track in enumerate(recommendations['tracks']):
        embeded_message.add_field(name=str(str(i+1) + ". "),value="{song} by {artist} - {preview_url}".format(song = track['name'], artist = track['artists'][0]['name'], preview_url = track['preview_url']), inline=False)

    await ctx.send(embed=embeded_message)
    
#     ############# HANDLE AUTHENTICATION CONDITIONS #############

#     # Assign uuid to unknown user
    
#     if not session.get('uuid'):
#         session['uuid'] = str(uuid.uuid4())

#     cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=get_session_cache_path())
#     spotipy_auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
#                                                 cache_handler=cache_handler,
#                                                 redirect_uri="https://git.heroku.com/songcierge-bot.git/", 
#                                                 show_dialog=True)
#     spotify_username = spotipy_auth_manager.current_user()['display_name']

#     if request.args.get("code"):
#         # Step 3. Being redirected from Spotify auth page
#         spotipy_auth_manager.get_access_token(request.args.get("code"))
#         return

#     if not spotipy_auth_manager.validate_token(cache_handler.get_cached_token()):
#         # Step 2. Display sign in link when no token
#         auth_url = spotipy_auth_manager.get_authorize_url()
#         await message.channel.send('Sign in to Spotify here ---> {auth_url}')

run_thread()
discord_bot.run(os.getenv('TOKEN'))
    