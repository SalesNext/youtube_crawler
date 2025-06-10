from typing import List, Set, Dict, Any, Iterable
import requests
import re
import json
import time
import logging
from salesnext_crawler.events import CrawlEvent, Event
from scrapy.http.response.html import HtmlResponse
from scrapy import Request
from youtube_crawler.parser.parse_channel_detail import parse_channel_detail

def get_yt_initial_data(url: str) -> dict:
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Lỗi khi gửi yêu cầu: {e}")
        return None
    match = re.search(r'var ytInitialData = ({.*?});</script>', response.text, re.DOTALL)
    if not match:
        print("Không tìm thấy ytInitialData trong HTML.")
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"Lỗi khi parse JSON ytInitialData: {e}")
        return None

def get_continuation_token(data: dict) -> str:
    def extract_token(obj):
        try:
            return obj["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
        except (KeyError, TypeError):
            return None
    # Path for related videos
    try:
        results = (
            data.get("contents", {})
                .get("twoColumnWatchNextResults", {})
                .get("secondaryResults", {})
                .get("secondaryResults", {})
                .get("results", [])
        )
        for item in results:
            token = extract_token(item)
            if token:
                return token
    except Exception:
        pass
    # Path for continuation API response
    try:
        for command in data.get("onResponseReceivedEndpoints", []):
            items = command.get("appendContinuationItemsAction", {}).get("continuationItems", [])
            for item in items:
                token = extract_token(item)
                if token:
                    return token
    except Exception:
        pass
    return None

def extract_channels_from_related_response(data: dict) -> Set[str]:
    channels = set()
    # API response: onResponseReceivedEndpoints/appendContinuationItemsAction/continuationItems
    commands = data.get("onResponseReceivedEndpoints", [])
    for command in commands:
        items = command.get("appendContinuationItemsAction", {}).get("continuationItems", [])
        for item in items:
            # compactVideoRenderer
            video = item.get("compactVideoRenderer")
            if not video:
                continue
            # Path 1: longBylineText
            runs = video.get("longBylineText", {}).get("runs", [])
            if runs:
                nav = runs[0].get("navigationEndpoint", {})
                browse = nav.get("browseEndpoint", {})
                canonical = browse.get("canonicalBaseUrl")
                if canonical:
                    url = f"https://www.youtube.com{canonical}"
                    channels.add(url)
                    continue
            # Path 2: shortBylineText
            runs = video.get("shortBylineText", {}).get("runs", [])
            if runs:
                nav = runs[0].get("navigationEndpoint", {})
                browse = nav.get("browseEndpoint", {})
                canonical = browse.get("canonicalBaseUrl")
                if canonical:
                    url = f"https://www.youtube.com{canonical}"
                    channels.add(url)
                    continue
            # Path 3: channelId
            channel_id = video.get("channelId")
            if channel_id:
                url = f"https://www.youtube.com/channel/{channel_id}"
                channels.add(url)
    return channels

def fetch_channels_with_token(continuation_token: str):
    url = 'https://www.youtube.com/youtubei/v1/next?prettyPrint=false'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    data = {
        "context": {
            "client": {
                "hl": "en",
                "gl": "US",
                "clientName": "WEB",
                "clientVersion": "2.20250606.01.00",
                "platform": "DESKTOP"
            }
        },
        "continuation": continuation_token
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        channels = extract_channels_from_related_response(result)
        next_token = get_continuation_token(result)
        return channels, next_token
    except Exception as e:
        logging.error(f"Error fetching related videos: {str(e)}")
        return set(), None

def parse_channel_list_from_related_videos(
    event: CrawlEvent[None, Event, HtmlResponse],
    response: HtmlResponse,
) -> Iterable[Event]:
    """Parse channel list from related videos section (refactored like search)."""
    try:
        all_channels = set()
        crawled_channel_ids = event.metadata.get('crawled_channel_ids', set())
        initial_data = get_yt_initial_data(response.url)
        if initial_data:
            token = get_continuation_token(initial_data)
            while token:
                more_channels, next_token = fetch_channels_with_token(token)
                all_channels.update(more_channels)
                token = next_token
        logging.info(f"Found {len(all_channels)} unique channels from related videos")
        logging.info(f"Channels: {all_channels}")
        for channel_url in all_channels:
            channel_id = channel_url.split('/')[-1]
            if channel_id in crawled_channel_ids:
                logging.info(f"Skipping already crawled channel: {channel_url}")
                continue
            logging.info(f"Processing channel URL: {channel_url}")
            yield CrawlEvent(
                request=Request(
                    channel_url,
                    method="GET",
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                        "Accept-Language": "en-US,en;q=0.9",
                    }
                ),
                metadata=event.metadata,
                callback=parse_channel_detail
            )

        # Extract the list of related videos from initial_data
        videos = initial_data.get('contents', {}).get('twoColumnWatchNextResults', {}).get('secondaryResults', {}).get('secondaryResults', {}).get('results', [])

        # Uncomment the part that jumps to other videos
        for video in videos:
            video_url = video.get('url')
            if video_url:
                yield Request(
                    url=video_url,
                    callback=self.parse_channel_list_from_related_videos,
                    meta={'dont_merge_cookies': True}
                )
    except Exception as e:
        logging.error(f"Error parsing channel list from related videos: {str(e)}")
        return []
