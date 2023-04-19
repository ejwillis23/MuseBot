import os
os.environ['SPOTIPY_CLIENT_ID']='hidden'
os.environ['SPOTIPY_CLIENT_SECRET']='hidden'
os.environ['SPOTIPY_REDIRECT_URI']='http://0.0.0.0:8000/sign-in'

import discord
import asyncio
import spotipy
from discord.ext import commands, tasks
from itertools import cycle

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix = '.', intents=intents)
status = cycle(['Status1', 'Status2'])

#### Events ####
@client.event
async def on_ready():
    # Change status and activity / then start change_status loop
    #await client.change_presence(status=discord.Status.idle, activity=discord.Game('Testing'))
    #change_status.start()

    print('bot is ready')

# Error checking can be done per-command (see 'clear' command) or generalised
#   If error is not specified here, there will be no error output
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command Not Found')
    if isinstance(error, TypeError):
        await ctx.send('Message not sent')

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server')

@client.event
async def on_member_update(before, after):
    if len(before.roles) < len(after.roles):
        # The user has gained a new role, so lets find out which one
        newRole = next(role for role in after.roles if role not in before.roles)
        if newRole.name == "Users":
            cache_handler = spotipy.cache_handler.CacheFileHandler(username=after)
            auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-read-collaborative playlist-modify-public playlist-modify-private user-follow-read user-read-recently-played user-library-read',
                                               cache_handler=cache_handler,
                                               show_dialog=True)
            
            if not auth_manager.validate_token(cache_handler.get_cached_token()):
                # Step 1. Display sign in link when no token
                auth_url = auth_manager.get_authorize_url()
                await after.send(auth_url)
            #     print(f'{auth_url}')
            # else:
            #     print(f'{after} not added to Users')

            sp = spotipy.Spotify(auth_manager=auth_manager)
            res = sp.current_user()
            print(res['display_name'])


#### Commands ####
@client.command()
async def ping(ctx):
    await ctx.send(f'pong {round(client.latency * 1000)}ms')

@client.command()
@commands.is_owner()
async def load(ctx, extension):
    await client.load_extension(f'cogs.{extension}')
    print(f'{extension} successfully loaded')

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    print(f'{extension} successfully unloaded')

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await client.load_extension(f'cogs.{extension}')
    print(f'{extension} successfully reloaded')
    await ctx.send("Reload finished")

@client.command()
@commands.is_owner()
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit=amount)
# Error checking can be done per-command or generalised (see 'on_command_error' event)
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing Required Arguments for clear')

#@client.command()
#async def kick(ctx, member : discord.Member, *, reason=None):
#    await member.kick(reason=reason)(


#### Loops ####
@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


#### Functions ####
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with client:
        await load_extensions()
        await client.start('hidden')

asyncio.run(main())
