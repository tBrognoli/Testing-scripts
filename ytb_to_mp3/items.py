# coding: utf8


class Music:
    def __init__(self):
        self.title = "Unknown"
        self.uploader = "Unknown"
        self.artist = "Unknown"
        self.album = "Unknown"
        self.track_number = None
        self.alb_image_url = None
        self.checked = False
        self.ytb_url = "Unknown"
        self.path = "Unknown"
        self.clean()

    def __repr__(self):
        return str(self.title)

    def clean(self):
        self.title = self.title.replace("/", "-")
        self.artist = self.artist.replace("/", "-")
        self.album = self.album.replace("/", "-")
        self.track_number = (
            int(self.track_number) if self.track_number is not None else None
        )
