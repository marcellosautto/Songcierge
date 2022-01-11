
import os
import sys
import discord
from discord import embeds
from discord import user
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv(".env")

# establish connection to discord and spotify web api
discord_client = discord.Client()

scope = 'user-read-private,user-top-read'
spotipy_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('SPOTIPY_CLIENT_ID'),client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'))
spotipy_client = spotipy.Spotify(client_credentials_manager=spotipy_credentials_manager,auth_manager=SpotifyOAuth(scope=scope,redirect_uri="http://localhost:8080/"))

spotify_username = spotipy_client.current_user()['display_name']
spotify_ranges = ['short_term', 'medium_term', 'long_term']

# print msg when the bot is online
@discord_client.event
async def on_ready():
    print('Logged in as {0.user}'.format(discord_client))

# The bot will say hello if the '$hello' command is executed
@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    # Print playlists
    if message.content.startswith('$playlists'):

        playlists = spotipy_client.user_playlists(user=spotify_username)
        embeded_message = discord.Embed(title="{}'s Playlists".format(spotify_username), description="", color=0x50c878)
        embeded_message.set_thumbnail(url=spotipy_client.current_user()['images'][0]['url'])
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                embeded_message.add_field(name=str(str(i+1) + ". "),value=playlist['name'], inline=True)

            if playlists['next']:
                playlists = spotipy_client.next(playlists)
            else:
                break    
            
        await message.channel.send(embed=embeded_message)
    
    # Print favorite songs and artists
    if message.content.startswith('$favorites'):
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

# run bot with login token
discord_client.run(os.getenv('TOKEN'))