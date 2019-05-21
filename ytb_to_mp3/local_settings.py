# coding: utf8

# Spotify settings
client_id = "f5fe1c5b2eab48fbaff7657e21667884"
client_secret = "68c432068fba42ecbb753a10ea796f23"

user_id = "11132634509"

# GraceNote settings
gn_clientID = "758931050-E2B701FAFCFAF594E137F0A1C045ED4E"

# Path
bookmarks_path = "/home/thomas/.config/google-chrome/Default/"
bookmarks_folder = "Musiques"
dl_to_path = "/media/thomas/Folder/Projects/dlThat/musics"


def my_hook(infos):
    if infos["status"] == "finished":
        print("Done downloading, now converting ...")
    if infos["status"] == "downloading":
        pass
    if infos["status"] == "error":
        pass


ydl_opts = {
    "format": "bestaudio/best",
    "nocheckcertificate": True,
    "noplaylist": False,
    "ignoreerrors": True,
    "geo_bypass": True,
    "default_search": "auto",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "progress_hooks": [my_hook],
}
