# -*- coding: utf-8 -*-
import json
from .spiders.spider_config import torrent_path
import os


class YggPipeline(object):
    def process_item(self, item, spider):

        return item


class JsonPipeline(object):
    def open_spider(self, spider):
        self.file = open(f"{torrent_path}item.json", "w+")
        self.file.write("[")

    def close_spider(self, spider):
        self.file.write("]")
        self.file.close()

    def process_item(self, item, spider):
        line = (
            json.dumps(dict(item), sort_keys=True, indent=4, separators=(",", ": "))
            + "\n"
        )

        self.file.write(line)
        return item
