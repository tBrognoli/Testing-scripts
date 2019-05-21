import scrapy
from .spider_config import ygg_name, ygg_pass, base_ygg_url, torrent_path
from ..items import YggItem


class YggSpider(scrapy.Spider):
    name = "ygg"

    def __init__(self, *args, **kwargs):
        super(YggSpider, self).__init__(*args, **kwargs)
        self.torrent_url = kwargs.get(" torrent_url")

    def start_requests(self):
        url = base_ygg_url
        yield scrapy.Request(url=url, callback=self.parse, meta={"cookiejar": 1})

    def parse(self, response):
        data = {"id": ygg_name, "pass": ygg_pass}
        return scrapy.FormRequest.from_response(
            response,
            formdata=data,
            callback=self.after_login,
            meta={"cookiejar": response.meta["cookiejar"]},
        )

    def after_login(self, response):
        url = f"{base_ygg_url}/user/ajax_usermenu"
        return scrapy.Request(
            url=url,
            callback=self.parse_redirect,
            meta={"cookiejar": response.meta["cookiejar"]},
        )

    def parse_redirect(self, response):
        return scrapy.Request(
            url=base_ygg_url,
            callback=self.parse_home,
            meta={"cookiejar": response.meta["cookiejar"]},
            dont_filter=True,
        )

    def parse_home(self, response):
        url = self.torrent_url
        return scrapy.Request(
            url=url,
            callback=self.parse_torrent_page,
            meta={"cookiejar": response.meta["cookiejar"]},
        )

    def parse_torrent_page(self, response):
        tree = response.selector

        tor_url = tree.xpath(
            "//table[@class='infos-torrent']//a[contains(@href, 'download_torrent')]/@href"
        ).extract_first()
        tor_url = f"{base_ygg_url}{tor_url}" if not "yggtorrent" in tor_url else tor_url

        name = tree.xpath("//h1/text()").extract_first()
        image = tree.xpath("//div[@class='default']//img/@src").extract_first()
        torrent = YggItem(name=f"{name.strip()}.torrent", url=tor_url, img_url=image)
        return scrapy.Request(
            url=tor_url,
            callback=self.save_tor_file,
            meta={"cookiejar": response.meta["cookiejar"], "item": torrent},
        )

    def save_tor_file(self, response):
        item = response.meta["item"]
        path = f"{torrent_path}{item['name']}"
        print(path)
        with open(path, "wb") as f:
            f.write(response.body)
        return item
