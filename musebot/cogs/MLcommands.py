import json
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
    
    # @commands.command()
    # async def dataTest(self, ctx, amount=1, *, songIn):
    #     message = await ctx.send("Waiting for results...")

    #     cache_handler = spotipy.cache_handler.CacheFileHandler(username=ctx.author)
    #     auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    #     if not auth_manager.validate_token(cache_handler.get_cached_token()):
    #         print("Not signed in")
    #         role = discord.utils.find(lambda m: m.name == 'Users', ctx.guild.roles)
    #         if role not in ctx.author.roles:
    #             await ctx.author.add_roles(role)

    #         sign_in(ctx.author)
    #     sp = spotipy.Spotify(auth_manager=auth_manager)

    #     # song = await songSearch(sp, songIn)
    #     song = await playlistSearch(sp, songIn)
    #     rec = dataUse[dataUse.track_name.str.lower() != songIn.lower()]
    #     waiting = "Waiting for results of " + song[2] + " by " + song[1] + "..."
    #     await message.edit(content=waiting)
    #     # waiting = "Waiting for results of " + song[2] + " by " + song[1] + "..."
    #     # await message.edit(content=waiting)
    
    #     await message.edit(content= await makeRec(amount, song, rec))

    # @commands.command()
    # async def checking(self, ctx, *, songIn):
    #     cache_handler = spotipy.cache_handler.CacheFileHandler(username=ctx.author)
    #     auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    #     if not auth_manager.validate_token(cache_handler.get_cached_token()):
    #         print("Not signed in")
    #         role = discord.utils.find(lambda m: m.name == 'Users', ctx.guild.roles)
    #         if role not in ctx.author.roles:
    #             await ctx.author.add_roles(role)

    #         sign_in(ctx.author)
    #     sp = spotipy.Spotify(auth_manager=auth_manager)

    #     # song = dataUse[(dataUse.name.str.lower() == songIn.lower())].info()
    #     # print(song)

    #     # if dataUse.isin([songIn]).any().any():
    #     #     print("Is in")
    #     #     song = dataUse[(dataUse.track_name.str.lower() == songIn.lower())].to_json()
    #     #     print(song)
    #     # else:
    #     #     print("Is out")
    #     #     print(await songSearch(ctx.author, songIn))
        
    #     # print(dataUse[(dataUse.name.str.lower() == songIn.lower())].head(1))
    #     # print(await songSearch(ctx.author, songIn))

    #     # try:
    #     #     search1 = sp.search(q=songIn, type='track', limit=1)['tracks']['items'][0]['id']
    #     #     search2 = sp.search(q="Carol of the Bells", type='track', limit=1)['tracks']['items'][0]['id']
    #     #     recco = sp.recommendations(seed_tracks=[search1, search2], limit=10)
    #     #     for idx in range(10):
    #     #         print(recco['tracks'][idx]['name'])
    #     # except:
    #     #     print("Error")

    #     try:
    #         playlists = sp.current_user_playlists(limit=26)
    #         for items in playlists['items']:
    #             if songIn.lower() in items['name'].lower():
    #                 songs = sp.playlist(items['id'], fields='name,id,tracks.items(track(name,id,popularity,artists(name)))')
    #                 print("Found")
    #                 break
    #             # print(items['name'])
    #         # print(playlists)
    #         meanslist = ["", "", songs['name'], songs['id'], 0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #         for idx, song in enumerate(songs['tracks']['items']):
    #             # print(song)
    #             audio = sp.audio_features(song['track']['id'])[0]
    #             meanslist[4] += song['track']['popularity']
    #             meanslist[5] += audio['acousticness']
    #             meanslist[6] += audio['danceability']
    #             meanslist[7] += audio['duration_ms']
    #             meanslist[8] += audio['energy']
    #             meanslist[9] += audio['instrumentalness']
    #             meanslist[10] += audio['key']
    #             meanslist[11] += audio['liveness']
    #             meanslist[12] += audio['loudness']
    #             meanslist[13] += audio['mode']
    #             meanslist[14] += audio['speechiness']
    #             meanslist[15] += audio['tempo']
    #             meanslist[16] += audio['time_signature']
    #             meanslist[17] += audio['valence']
    #         songslen = len(songs['tracks']['items'])
    #         means = ["", meanslist[1], meanslist[2], meanslist[3]]
    #         for item in meanslist[4:]:
    #             # print("here")
    #             means.append(item / songslen)
    #         print(means)
    #         # testframe = pd.json_normalize(songs['tracks']['items'])
    #         # temp = testframe.loc[:, 'track.duration_ms'].mean()
    #         # print(temp)
    #     except:
    #         print("Error")

    #     message = await ctx.send("done")
    #     await message.add_reaction("🇦")

    @commands.command()
    async def checking(self, ctx, *, songIn):
        inpSong, inpArtist = songIn.split(" by ") if " by " in songIn else (songIn, "")
        # print(inpSong, inpArtist)
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
        waiting = "Waiting for results of " + song[2] + " by " + song[1] + "...\n"
        await message.edit(content=waiting)

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

async def songSearch(sp: spotipy.Spotify, track, artist=""):
    # print(track, artist)
    if artist == "":
        input = "track:" + track
    else:
        input = "track:" + track + " artist:" + artist
    search = sp.search(q=input, type='track', limit=1)
    # search = sp.search(q=track, type='track', limit=1)
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
        playlists = sp.current_user_playlists(limit=26)
        for items in playlists['items']:
            if playlist.lower() in items['name'].lower():
                songs = sp.playlist(items['id'], fields='name,id,tracks.items(track(name,id,popularity,artists(name)))')
                print("Found")
                break

        # print(songs)
        meanslist = ["", "", songs['name'], songs['id'], 0,0,0,0,0,0,0,0,0,0,0,0,0,0]
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
            # print("here")
            means.append(item / songslen)
        # print(frame.mean(numeric_only=True))

    except:
        print("playlistSearch error")

    return means

def sign_in(author):
    cache_handler = spotipy.cache_handler.CacheFileHandler(username=author)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-read-collaborative user-follow-read user-read-recently-played user-library-read',
                                        cache_handler=cache_handler,
                                        show_dialog=True)

    sp = spotipy.Spotify(auth_manager=auth_manager)
    res = sp.current_user()
    print(res['display_name'])

def make_pretty(result):
    res_str = ""
    for idx in result.itertuples():
        res_str += (idx.track_name + "    by    " + idx.artist_name + "\n")
    # print(res_str)

    return res_str

async def setup(client):
    await client.add_cog(MLCommands(client))