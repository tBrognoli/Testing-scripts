# coding: utf-8
import json
import re
import Levenshtein
import spotipy
from .items import Music
from spotipy.oauth2 import SpotifyClientCredentials
from .local_settings import *


def get_boookmarks(path, bk_folder):
    with open(path + "Bookmarks") as file:
        data = json.load(file)

    musics_bk = None
    for name, data in data["roots"].items():
        if isinstance(data, dict):
            for folder in data["children"]:
                if folder["name"] == bk_folder:
                    musics_bk = folder["children"]

    if not musics_bk:
        return

    urls = []
    for folder in musics_bk:
        urls.append(folder["url"])

    return urls


def replace_all(text):
    # é == é -> False.... WTF
    dic = {"é": "é", "à": "à"}
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


useless = [
    # Match anything after 'clip'
    r"clip.+",
    # Match " - youtube"
    r"\s?-\s?YouTube",
    # Match anything in ()
    r"\(.[^(]*\)",
    # Match music video
    r"Music Video",
    # Match " .mpX"
    r".mp\d",
]

useless1 = [r"ft.+", r"feat.+"]

infos_patterns = [
    r"(?P<artist>.+?)\s?[-|/|:]+\s?(?P<song>[\w.\'\"\s&]*)",
    r"(?P<artist>.+)[\"\']((?P<song>.+))[\"']",
]


def clean_infos(name, uploader):
    name = replace_all(name)
    nname = name

    # Remove useless infos in title
    for pattern in useless:
        nname = re.sub(pattern, "", nname, flags=re.I).strip()

    # Try to separate artist and song name
    for pattern in infos_patterns:
        infos = re.search(pattern, nname, re.IGNORECASE)
        if infos:
            break

    if not infos:
        # We take the uploader as artist if we can't get it in title
        # Some uploader has "- Topic" in their name, we delete it
        artist, song = uploader.replace("- Topic", ""), nname.strip().capitalize()
    else:
        artist, song = (
            infos.group("artist").strip().capitalize(),
            infos.group("song").strip().capitalize(),
        )

    for pattern in useless1:
        artist = re.sub(pattern, "", artist, flags=re.I).strip()
        song = re.sub(pattern, "", song, flags=re.I).strip()

    quote = re.search(r"^[\"\'](?P<song>.+)[\"']", song)
    if quote:
        song = quote.group(1)
    return ask_spotify(artist, song)


def ask_spotify(artist, song):
    music = Music()

    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # We reverse artist and song in request cause we can't know yb title format
    requests = [
        "artist:%s track:%s" % (artist, song)
        if artist != "Unknown"
        else "track:%s" % song,
        "artist:%s track:%s" % (song, artist)
        if artist != "Unknown"
        else "track:%s" % artist,
        "track:%s" % song,
        "track:%s" % artist,
    ]
    # Stop if we have a match
    for request in requests:
        results = spotify.search(q=request)
        if results["tracks"]["items"]:
            break

    # Some songs are not on spotify, or yb name is too wrong
    if not results["tracks"]["items"]:
        return ask_graceNote(artist, song)

    # Parse spotify item
    for item in results["tracks"]["items"]:
        good_ratios = {}
        # Get artist and track find by spotify to compare youtube's one
        spot_artist = item["album"]["artists"][0]["name"]
        spot_track = item["name"]

        # Get artist from request to be sure we compare the good one
        re_artist = re.search(r"artist:(.+)\strack:", request)
        if re_artist:
            good_ratios.update({"artist": True})
            re_artist = re_artist.group(1)

            artist_ratio = Levenshtein.ratio(spot_artist.lower(), re_artist.lower())

            if artist_ratio < 0.7 or re_artist == "Unknown":
                good_ratios.update({"artist": False})

        # Get track from request to be sure we compare the good one
        re_track = re.search(r"track:(.+)", request)
        if re_track:
            good_ratios.update({"track": True})
            re_track = re_track.group(1)

            track_ratio = Levenshtein.ratio(spot_track.lower(), re_track.lower())

            if track_ratio < 0.5 or re_track == "Unknown":
                good_ratios.update({"track": False})

        # Avoid taking wierd version of song
        terms = [
            " mix " in spot_track.lower(),
            " remix " in spot_track.lower(),
            "instrumental" in spot_track.lower(),
        ]
        failure = False
        for term in terms:
            if term:
                failure = True
        if failure:
            break

        # Check the artist ratio,
        # FIXME use track ratio
        failure = True
        if good_ratios.get("artist") is not None:
            if good_ratios.get("artist"):
                failure = False
                break

    if failure:
        return ask_graceNote(artist, song)

    music.artist = item["album"]["artists"][0]["name"]
    music.title = item["name"]
    music.album = item["album"]["name"]
    music.track_number = item["track_number"]
    music.alb_image_url = item["album"]["images"][0]["url"]
    music.checked = True
    # alb_ico_url = item['album']['images'][2]['url']

    return music


def ask_graceNote(artist, song):
    """
    We ask gracenote only if spotify results don't match because querys number
    to this api is limited
    """
    music = Music()

    # If one is "Unknown", we don't even search and directly return music
    if artist == "Unknown" or artist == "" or song == "Unknown" or song == "":
        music.artist = artist
        music.title = song
        return music

    gn_userID = pygn.register(gn_clientID)
    queries = [
        pygn.search(clientID=gn_clientID, userID=gn_userID, artist=artist, track=song),
        pygn.search(clientID=gn_clientID, userID=gn_userID, artist=song, track=artist),
    ]
    failure = True
    for query in queries:

        gn_artist = query["album_artist_name"]

        gn_title = query["tracks"][0]["track_title"]
        artist_ratio = Levenshtein.ratio(gn_artist.lower(), artist.lower())
        track_ratio = Levenshtein.ratio(gn_title.lower(), song.lower())
        if artist_ratio > 0.7 or track_ratio > 0.7:
            failure = False
            break

    if failure:
        music.artist = artist
        music.title = song
        return music

    music.artist = gn_artist
    music.title = gn_title
    music.album = query["album_title"]
    music.track_number = query["tracks"][0]["track_number"]
    music.alb_image_url = query["album_art_url"]
    music.checked = True

    return music
