# coding: utf-8
import youtube_dl
from .utils import clean_infos
import eyed3
from .local_settings import ydl_opts


def get_video_infos(link, options=None, folder=None):
    if options:
        ydl_opts.update(options)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(link, download=False)

    # There is an 'entries' field if there are multiple videos,
    # like for a playlist
    infos_list = []
    if result and result.get("entries", False):
        for video in result["entries"]:
            if video:
                # TEST
                infos_list.append(
                    {
                        "title": video["title"],
                        "uploader": video["uploader"],
                        "url": video["webpage_url"],
                    }
                )
                ####
                # music = clean_infos(video["title"], video["uploader"])
                # music.ytb_url = video["webpage_url"]
                # download_songs(music, ydl_opts, folder)
    else:
        if result:
            # TEST
            infos_list.append(
                {
                    "title": result["title"],
                    "uploader": result["uploader"],
                    "url": result["webpage_url"],
                }
            )
            ####
            # music = clean_infos(result["title"], result["uploader"])
            # music.ytb_url = result["webpage_url"]
            # download_songs(music, ydl_opts, folder)

    return infos_list


def download_songs(music, ydl_opts, dl_to_folder=None):
    if not dl_to_folder:
        dl_to_folder = "./downloads/musics"

    music.clean()
    ydl_opts.update(
        {
            "outtmpl": "{path}/{title}.%(ext)s".format(
                path=dl_to_folder, title=music.title
            )
        }
    )

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download({music.ytb_url})

    file_path = ydl_opts["outtmpl"] % {
        "ext": ydl_opts["postprocessors"][0]["preferredcodec"]
    }

    add_metadata(file_path, music)
    music.path = file_path
    return music


def add_metadata(file_path, music):
    audiofile = eyed3.load(file_path)
    audiofile.tag.artist = music.artist
    audiofile.tag.title = music.title
    audiofile.tag.comments.set(music.ytb_url)
    audiofile.tag.album = music.album
    audiofile.tag.track_num = music.track_number

    if music.alb_image_url:
        audiofile.tag.images.set(
            type_=3,
            img_data=None,
            mime_type="image/pgn",
            description="Album cover",
            img_url=music.alb_image_url,
        )
    # audiofile.tag.images.set(
    #     type_=1,
    #     img_data=None,
    #     mime_type=None,
    #     description="Icon cover",
    #     img_url=music["alb_ico_url"],
    # )

    audiofile.tag.save()
