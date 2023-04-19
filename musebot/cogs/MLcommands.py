import json
from urllib.parse import urlencode
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import spotipy
import discord
from discord.ext import commands
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

### Data setup ###
dataUse = pd.read_csv("tracks/SpotifyFeatures.csv")
dataUse.drop_duplicates(subset="track_id", keep='first', inplace=True)
df = dataUse.drop(columns=['genre', 'artist_name', 'track_name', 'track_id', 'key', 'mode', 'time_signature'])
df.corr(numeric_only=True)

datatypes = ['int64', 'float64']
normarization = dataUse.select_dtypes(include=datatypes)
for col in normarization.columns:
    MinMaxScaler(col)

# kmeans = KMeans(n_clusters=10)
# features = kmeans.fit_predict(normarization)
# dataUse['features'] = features
# MinMaxScaler(dataUse['features'])

class MLCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
       print('bot is ready ML')

    @commands.command()
    async def pingML(self, ctx):
        await ctx.send('pong ML')

    @commands.command()
    async def songRec(self, ctx, amount=1, *, songIn):
        inpSong, inpArtist = songIn.split(" by ") if " by " in songIn else (songIn, "")
        message = await ctx.send("Waiting for results...")

        cache_handler = spotipy.cache_handler.CacheFileHandler(username=ctx.author)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            print("Not signed in")
            role = discord.utils.find(lambda m: m.name == 'Users', ctx.guild.roles)
            if role not in ctx.author.roles:
                await ctx.author.add_roles(role)

            sign_in(ctx.author)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        song = await songSearch(sp, inpSong, inpArtist)
        rec = dataUse[dataUse.track_name.str.lower() != songIn.lower()]
        waiting = "Waiting for results of " + song[2] + " by " + song[1] + "...\n"
        await message.edit(content=waiting)
    
        waiting = "Reccomendations for " + song[2] + " by " + song[1] + ":\n"
        
        await message.edit(content= waiting + await makeRec(amount, song, rec))
    
    @commands.command()
    async def playlistRec(self, ctx, amount=1, *, playIn):
        message = await ctx.send("Waiting for results...")

        cache_handler = spotipy.cache_handler.CacheFileHandler(username=ctx.author)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            print("Not signed in")
            role = discord.utils.find(lambda m: m.name == 'Users', ctx.guild.roles)
            if role not in ctx.author.roles:
                await ctx.author.add_roles(role)

            sign_in(ctx.author)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        song = await playlistSearch(sp, playIn)
        rec = dataUse[dataUse.track_name.str.lower() != playIn.lower()]
        waiting = "Waiting for results of playlist input " + song[2] + "...\n"
        await message.edit(content=waiting)
    
        waiting = "Reccomendations for " + song[2] + ":\n"
        await message.edit(content= waiting + await makeRec(amount, song, rec))

    @commands.command()
    async def RecWithFriends(self, ctx: commands.Context, amount: int, name, *username: discord.Member):
        msg = ""
        for user in username:
            # msg += user.mention + " "
            msg += "@" + user.display_name + " "
        await ctx.send(f"{msg}: Input songs or your playlists! (e.g.: \"song: Disco Man by Remi Wolf, playlist: Fall Car\")")

        def check(m: discord.Message):
            return m.channel == ctx.channel and m.author in username # m.content == "hello"

        songs = []
        for i in username:
            msg = await self.client.wait_for("message", check=check)

            context = await self.client.get_context(msg)
            cache_handler = spotipy.cache_handler.CacheFileHandler(username=context.author)
            auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
            if not auth_manager.validate_token(cache_handler.get_cached_token()):
                print("Not signed in")
                role = discord.utils.find(lambda m: m.name == 'Users', context.guild.roles)
                if role not in context.author.roles:
                    await context.author.add_roles(role)

                sign_in(context.author)
            sp = spotipy.Spotify(auth_manager=auth_manager)

            # inpSong, inpArtist = msg.content.split(" by ") if " by " in msg.content else (msg.content, "")
            division = msg.content.split(", ")
            # print(division)
            for inp in division:
                # print(inp)
                sopl, inputsopl = inp.split(": ") if ":" in inp else ("song", inp)
                # print(sopl, inputsopl)
                if sopl.lower() == "song":
                    inpSong, inpArtist = inputsopl.split(" by ") if "by" in inputsopl else (inputsopl, "")
                    song = await songSearch(sp, inpSong, inpArtist)
                    # print("S")
                else:
                    inpSong = inputsopl
                    song = await playlistSearch(sp, inputsopl)
                    # print("P")

                if len(song) == 0:
                    await ctx.send(f"{msg.author}: Couldn't find {inputsopl}")
                else: 
                    songs.append(song)
                    await ctx.send(f"{msg.author} results: {song[2]} by {song[1]}")

        meanslist = [songs[0][0], songs[0][1], songs[0][2], songs[0][3], 0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # print(meanslist)
        for song in songs:
            # print(i, song)
            meanslist[4] += song[4]
            meanslist[5] += song[5]
            meanslist[6] += song[6]
            meanslist[7] += song[7]
            meanslist[8] += song[8]
            meanslist[9] += song[9]
            meanslist[10] += song[10]
            meanslist[11] += song[11]
            meanslist[12] += song[12]
            meanslist[13] += song[13]
            meanslist[14] += song[14]
            meanslist[15] += song[15]
            meanslist[16] += song[16]
            meanslist[17] += song[17]
        songslen = len(songs)
        means = ["", meanslist[1], meanslist[2], meanslist[3]]
        for item in meanslist[4:]:
            means.append(item / songslen)

        rec = dataUse[dataUse.track_name.str.lower() != inpSong.lower()]
        waiting = "Waiting for results...\n"
        message = await ctx.send(waiting)

        playlists = sp.current_user_playlists(limit=50)
        playlist = 0
        for items in playlists['items']:
            if name.lower() in items['name'].lower():
                playlist = sp.playlist(items['id'], fields='external_urls,name,id,tracks.items(track(name,id,artists(name)))')
                break
        if playlist == 0:
            playlist = sp.user_playlist_create(user=sp.me()['id'], name=name)
        # print(playlist)

        id_list = await makeRec(amount, means, rec)
        songlist = []
        playidlist = []
        for song in playlist['tracks']['items']:
            playidlist.append(song['track']['id'])
        for songid in id_list:
            if songid not in playidlist:
                songlist.append(songid)

        # print(songlist, songidlist, playidlist)
        if len(songlist) > 0:
            sp.playlist_add_items(playlist['id'], songlist)

        waiting = "Resulting playlistt:\n"
        await message.edit(content= waiting + playlist['external_urls']['spotify'])

    @commands.command()
    async def checking(self, ctx: commands.Context, name):
        cache_handler = spotipy.cache_handler.CacheFileHandler(username=ctx.author)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            print("Not signed in")
            role = discord.utils.find(lambda m: m.name == 'Users', ctx.guild.roles)
            if role not in ctx.author.roles:
                await ctx.author.add_roles(role)

            sign_in(ctx.author)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        playlists = sp.current_user_playlists(limit=50)
        playlist = 0
        for items in playlists['items']:
            if name.lower() in items['name'].lower():
                playlist = sp.playlist(items['id'], fields='external_urls,name,id,tracks.items(track(name,id,artists(name)))')
                break
        if playlist == 0:
            playlist = sp.user_playlist_create(user=sp.me()['id'], name=name)
        # print(playlist)

        songlist = []
        songidlist = ['5njHdo6Ev5nVdssMYdcaZ5', '27sBcXtgTBSJRdUxei1a7J']
        playidlist = []
        for song in playlist['tracks']['items']:
            playidlist.append(song['track']['id'])
        for songid in songidlist:
            if songid not in playidlist:
                songlist.append(songid)

        # print(songlist, songidlist, playidlist)
        if len(songlist) > 0:
            sp.playlist_add_items(playlist['id'], songlist)

        await ctx.send(playlist['external_urls']['spotify'])

async def songSearch(sp: spotipy.Spotify, track, artist=""):
    # print(track, artist)
    # if artist == "":
    #     input = "track:" + track
    # else:
    #     input = "track:" + track + " artist:" + artist
    if artist == "":
        input = track
    else:
        input = track + " " + artist
    search = sp.search(q=input, type='track', limit=5)
    if len(search['tracks']['items']) <= 0:
        print("Error")
        return []
    audio = sp.audio_features([search['tracks']['items'][0]['id']])[0]
    testing = [
        audio['type'], 
        search['tracks']['items'][0]['artists'][0]['name'], 
        search['tracks']['items'][0]['name'], 
        audio['id'], 
        search['tracks']['items'][0]['popularity'],
        audio['acousticness'],
        audio['danceability'],
        audio['duration_ms'],
        audio['energy'],
        audio['instrumentalness'],
        audio['key'],
        audio['liveness'],
        audio['loudness'],
        audio['mode'],
        audio['speechiness'],
        audio['tempo'],
        audio['time_signature'],
        audio['valence'],
        # 0,
    ]

    return testing

async def playlistSearch(sp: spotipy.Spotify, playlist):
    try:
        playlists = sp.current_user_playlists(limit=50)
        songs = []
        for items in playlists['items']:
            if playlist.lower() in items['name'].lower():
                songs = sp.playlist(items['id'], fields='name,id,tracks.items(track(name,id,popularity,artists(name)))')
                # print("Found")
                break
        if len(songs) == 0:
            print("Error")
            return []

        # print(songs)
        meanslist = ["", sp.current_user()['display_name'], songs['name'], songs['id'], 0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # print(meanslist)
        for song in songs['tracks']['items']:
            # print(song)
            audio = sp.audio_features(song['track']['id'])[0]
            meanslist[4] += song['track']['popularity']
            meanslist[5] += audio['acousticness']
            meanslist[6] += audio['danceability']
            meanslist[7] += audio['duration_ms']
            meanslist[8] += audio['energy']
            meanslist[9] += audio['instrumentalness']
            meanslist[10] += audio['key']
            meanslist[11] += audio['liveness']
            meanslist[12] += audio['loudness']
            meanslist[13] += audio['mode']
            meanslist[14] += audio['speechiness']
            meanslist[15] += audio['tempo']
            meanslist[16] += audio['time_signature']
            meanslist[17] += audio['valence']
        songslen = len(songs['tracks']['items'])
        means = ["", meanslist[1], meanslist[2], meanslist[3]]
        for item in meanslist[4:]:
            means.append(item / songslen)
        # print(frame.mean(numeric_only=True))

    except:
        print("playlistSearch error")

    return means

async def sign_in(author):
    cache_handler = spotipy.cache_handler.CacheFileHandler(username=author)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-read-collaborative user-follow-read user-read-recently-played user-library-read',
                                        cache_handler=cache_handler,
                                        show_dialog=True)

    sp = spotipy.Spotify(auth_manager=auth_manager)
    res = sp.current_user()
    print(res['display_name'])

async def makeRec(amount: int, song: list, rec):
    distance = []
    for songs in rec.values:
        d = 0
        for col in np.arange(len(rec.columns)):
            if not col in [0, 1, 2, 3, 10, 13, 16]:
                d = d + np.absolute(float(song[col]) - float(songs[col]))
        distance.append(d)
    rec['distance'] = distance
    rec = rec.sort_values('distance')
    columns = ['artist_name', 'track_name', 'track_id']
    
    result = rec[columns][:amount]
    result.drop_duplicates(subset="track_id", keep='first', inplace=True)
    non_dupes = len(result.index)
    i = non_dupes
    while non_dupes < amount:
        result = rec[columns][:amount+i]
        result.drop_duplicates(subset="track_id", keep='first', inplace=True)
        i += 1
        non_dupes = len(result.index)

    return make_pretty(result)

def make_pretty(result):
    res_ids = []
    for idx in result.itertuples():
        res_ids.append(idx.track_id)
    # print(res_str)

    return res_ids

async def setup(client):
    await client.add_cog(MLCommands(client))