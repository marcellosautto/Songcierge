
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
# spotipy_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('SPOTIPY_CLIENT_ID'),client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'))
spotipy_client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,redirect_uri="https://git.heroku.com/songcierge-bot.git/"))

spotify_username = spotipy_client.current_user()['display_name']
# spotify_ranges = ['short_term', 'medium_term', 'long_term']

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

        playlists = spotipy_client.current_user_playlists()
        embeded_message = discord.Embed(title="{}'s Playlists".format(spotify_username), description="", color=0x50c878)
        embeded_message.set_thumbnail(url=spotipy_client.current_user()['images'][0]['url'])

        for i, playlist in enumerate(playlists['items']):
            embeded_message.add_field(name=str(str(i+1) + ". "),value=playlist['name'], inline=True)
 
            
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

    # Recommend tracks to the user based on their top track and artist
    if message.content.startswith('$recommend'):
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