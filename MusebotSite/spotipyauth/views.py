import os
os.environ['SPOTIPY_CLIENT_ID']='hidden'
os.environ['SPOTIPY_CLIENT_SECRET']='hidden'
os.environ['SPOTIPY_REDIRECT_URI']='http://0.0.0.0:8000/sign-in'

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
import spotipy
import spotipy.util as util
from spotipy import oauth2

from .forms import NameForm, CheckForm

def next_offset(n):
    try:
        return int(n['next'].split('?')[1].split('&')[0].split('=')[1])
    except ValueError:
        return None
    except AttributeError:
        return None
    except TypeError:
        return None


def home(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CheckForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            path = 'C:/Users/elija/OneDrive/Documents/csci490/musebot/.cache-' + form.cleaned_data['your_name']
            cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=path)
            sp_oauth = oauth2.SpotifyOAuth(scope='playlist-read-collaborative user-follow-read user-read-recently-played user-library-read',
                                                cache_handler=cache_handler,
                                                show_dialog=True)
            token_info = sp_oauth.get_cached_token()
            if not token_info:
                auth_url = sp_oauth.get_authorize_url()
                return HttpResponseRedirect(auth_url)
            else:
                return HttpResponse('Already signed in')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CheckForm()

    # return HttpResponse("Home")
    return render(request, 'spotipyauth/home.html', {'form': form})

def sign_in(request):
    if request.method == 'POST':
        # print(request.POST)
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # print(form.cleaned_data)
            path = 'C:/Users/elija/OneDrive/Documents/csci490/musebot/.cache-' + form.cleaned_data['your_name']
            cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=path)
            sp_oauth = oauth2.SpotifyOAuth(scope='playlist-read-collaborative user-follow-read user-read-recently-played user-library-read',
                                                cache_handler=cache_handler,
                                                show_dialog=True)
            code = sp_oauth.parse_response_code(form.cleaned_data['token'])
            token_info = sp_oauth.get_access_token(code)

            if token_info:
                sp = spotipy.Spotify(auth=token_info['access_token'])
                results = sp.current_user_saved_tracks()

            return render(request, 'spotipyauth/sign-in.html', {'results': results['items']})
            # return HttpResponse("Sign in post")
        else:
            return HttpResponse("Sign in post else")
    else:
        if len(request.GET) > 0:
            token = 'http://localhost:8000/after-sign-in/?{}'.format(request.GET.urlencode())
            data = {'your_name': '', 'token': token}
            form = NameForm(data)
            # print(form)
            return render(request, 'spotipyauth/home.html', {'form': form})
        
def after_sign_in(request):
    results = {}
    token = 'http://localhost:8000/after-sign-in/?{}'.format(request.GET.urlencode())
    # sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI,
    #                                scope=scope, cache_path=".cache-" + username)
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path='C:/Users/elija/OneDrive/Documents/csci490/musebot/.cache')
    sp_oauth = oauth2.SpotifyOAuth(scope='playlist-read-collaborative user-follow-read user-read-recently-played user-library-read',
                                        cache_handler=cache_handler,
                                        show_dialog=True)
    code = sp_oauth.parse_response_code(token)
    token_info = sp_oauth.get_access_token(code)
    # if len(request.GET) > 0:
    #     print(request.GET)

    if token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        results = sp.current_user_saved_tracks()

    return render(request, 'spotipyauth/sign-in.html', {'results': results['items']})
    # return("Hello")

