from collections.abc import Iterable
from salesnext_crawler.crawler import ScrapyCrawler
from salesnext_crawler.events import DataEvent, Event, CrawlEvent
from youtube_crawler.parser.parse_channel_list_from_related_videos import parse_channel_list_from_related_videos
from youtube_crawler.parser.parse_channel_list_from_search import parse_channel_list_from_search
from youtube_crawler.parser.parse_channel_detail import parse_channel_detail
from scrapy import Request
from urllib.parse import urljoin

class YoutubeCrawler(ScrapyCrawler):
    def __init__(
        self,
        daily: bool = False,
        search_query: str = 'vlog',
        seed_video_url: str = None,
    ):
        print("Hello World from YoutubeCrawler!")
        self.daily = daily
        self.search_query = search_query
        self.seed_video_url = seed_video_url
        print(f"Using seed video URL: {self.seed_video_url}")

    def start(self) -> Iterable[Event]:
        print("Starting YoutubeCrawler...")
        crawled_channel_ids = set()

        if self.daily:
            channel_table = self.readers["youtube_channel_table"].read()
            crawled_channel_ids = set(channel_table.select(["channel_id"]).drop_null().to_pydict()["channel_id"])

        # If we have a seed video URL, start with getting recommendations
        # if self.seed_video_url:
        #     print(f"Starting crawl from seed video: {self.seed_video_url}")
        #     yield CrawlEvent(
        #         request=Request(
        #             self.seed_video_url,
        #             method="GET"
        #         ),
        #         metadata={'crawled_channel_ids': crawled_channel_ids},
        #         callback=parse_channel_list_from_related_videos
        #     )
        if self.search_query:
        # elif self.search_query:
            # Otherwise use search
            search_url = urljoin(
                "https://www.youtube.com/results",
                f"?search_query={self.search_query}&sp=EgIQAg%253D%253D"
            )
            yield CrawlEvent(
                request=Request(
                    search_url,
                    method="GET"
                ),
                metadata={'crawled_channel_ids': crawled_channel_ids},
                callback=parse_channel_list_from_search
            )
