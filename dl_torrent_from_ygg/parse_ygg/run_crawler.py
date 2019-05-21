import os
import subprocess
import json
from config import torrent_path

items = []


def dl_torrent_file(torrent_url):
    owd = os.getcwd()
    os.chdir(f"{owd}/scripts/dl_torrent_from_ygg/parse_ygg/ygg")
    subprocess.call(["scrapy", "crawl", "ygg", f"-a torrent_url={torrent_url}"])

    os.chdir(owd)
    item_file = open(f"{torrent_path}item.json")
    return json.load(item_file)[0]
