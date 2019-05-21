from .add_torrent_to_queue.add_torrent import add_torrent_to_queue
from .parse_ygg.run_crawler import dl_torrent_file
import datetime
from utils.bdd_utils import create_connection


def insert_in_bdd(connection, torrent):
    """
    Create a new torrent into the torrents table
    :param connection:
    :param movie:
    :return: movie id
    """
    sql = """ INSERT IGNORE INTO torrents(name, url, img_url, date_extraction, caller, is_ebook)
              VALUES(%s, %s, %s, %s, %s, %s) """
    cursor = connection.cursor()
    cursor.execute(sql, torrent)
    connection.commit()
    cursor.close()


def select_in_bdd(connection, dict_req):
    req = " and ".join(
        [f"{db_field}='{value}'" for db_field, value in dict_req.items()]
    )
    sql = f"SELECT url FROM torrents WHERE {req}"
    cursor = connection.cursor()
    cursor.execute(sql)
    allready_in = cursor.fetchone()
    cursor.close()
    return allready_in


class Torrent:
    def __init__(self, url, is_ebook, caller):
        self.url = url
        self.caller = caller
        self.is_ebook = is_ebook
        self.name = ""
        self.img_url = ""
        self.date_extraction = ""

    def __repr__(self):
        return f"{self.name} - asked by {self.caller} - ebook={self.is_ebook}"

    def save_in_bdd(self):
        connection = create_connection()

        torrent = (
            self.name,
            self.url,
            self.img_url,
            self.date_extraction,
            self.caller,
            self.is_ebook,
        )
        insert_in_bdd(connection, torrent)
        connection.close()

    def check_if_already_dl(self):
        connection = create_connection()
        torrent = {"url": self.url}
        allready_dl = select_in_bdd(connection, torrent)
        connection.close()
        return allready_dl

    def populate_datas(self, infos):
        self.name = infos["name"]
        self.img_url = infos["img_url"]
        self.date_extraction = infos["date_extraction"]


def download_torrent(caller, torrent_url, is_ebook):
    torrent = Torrent(url=torrent_url, caller=caller, is_ebook=is_ebook)

    allready_dl = torrent.check_if_already_dl()

    # if allready_dl:
    # cursor.close()
    # connection.close()
    # send already dl torrent to asker
    # pass

    # Download torrent file from YGG
    torrent_infos = dl_torrent_file(torrent_url)
    torrent_infos["date_extraction"] = datetime.datetime.now().strftime(
        "%m/%d/%Y, %H:%M"
    )
    torrent.populate_datas(torrent_infos)

    # Add torrent's info to bdd
    torrent.save_in_bdd()

    # Download torrent
    torrent_added_to_queue = add_torrent_to_queue(torrent.name)

    return torrent
