import os

from transmission import Transmission

from config import torrent_path
from utils.bdd_utils import create_connection


def add_torrent_to_queue(torrent_name):
    torrent_file = f"{os.getcwd()}/downloads/torrent_files/{torrent_name}" 
    connection = create_connection()
    cursor = connection.cursor()

    client = Transmission()
    
    transmission_hash = client("torrent-add", filename=torrent_file)["torrent-added"][
        "hashString"
    ]
    cursor.execute(
        f"UPDATE torrents SET transmission_hash = '{transmission_hash}' WHERE name = \"{torrent_name}\""
    )
    connection.commit()
    cursor.close()
    connection.close()
