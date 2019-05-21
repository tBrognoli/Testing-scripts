# coding: utf8
from .utils import clean_infos
from .downloader import get_video_infos, download_songs
import sys
from .local_settings import ydl_opts
from .spotify_script import get_song_infos_from_playlist


def dl_song(musics_links):
    files_paths = []
    for link in musics_links:
        videos_list = get_video_infos(link, {"noplaylist": True})
        for video in videos_list:
            music = clean_infos(video["title"], video["uploader"])
            music.ytb_url = video["url"]
            files_paths.append(download_songs(music, ydl_opts))
    return files_paths
