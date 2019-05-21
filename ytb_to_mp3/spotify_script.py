import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .local_settings import *
from .items import Music


client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret
)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_spotify_playlist(user_id):
    spot_playlists = spotify.user_playlists(user_id)
    playlists_list = []
    for playlists in spot_playlists["items"]:
        playlists_list.append({"name": playlists["name"], "id": playlists["id"]})
    return playlists_list


def get_song_infos_from_playlist(user_id, playlist_id):
    playlist = spotify.user_playlist_tracks(user_id, playlist_id)
    music_list = []
    while playlist["next"]:
        playlist = spotify.next(playlist)
        for track in playlist["items"]:
            music = Music()
            music.title = track["track"]["name"]
            music.artist = track["track"]["artists"][0]["name"]
            music.album = track["track"]["album"]["name"]
            music.checked = True
            music_list.append(music)
    return music_list
