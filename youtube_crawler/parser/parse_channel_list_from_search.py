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

    # Check for initial search data structure
    try:
        sections = (
            data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
        )
        for section in sections:
            token = extract_token(section)
            if token:
                return token
    except Exception:
        pass

    # Check for continuation data structure
    try:
        for command in data.get("onResponseReceivedCommands", []):
            items = command.get("appendContinuationItemsAction", {}).get("continuationItems", [])
            for item in items:
                token = extract_token(item)
                if token:
                    return token
    except Exception:
        pass

    return None

def extract_channels_from_response(data: dict) -> Set[str]:
    def extract_channel_url(channel_renderer: dict) -> str:
        url = channel_renderer.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url")
        if url:
            return f"https://www.youtube.com{url}"
        channel_id = channel_renderer.get("channelId")
        if channel_id:
            return f"https://www.youtube.com/channel/{channel_id}"
        return None

    channels = set()
    commands = data.get("onResponseReceivedCommands", [])
    for command in commands:
        items = command.get("appendContinuationItemsAction", {}).get("continuationItems", [])
        for item in items:
            # Direct channelRenderer
            channel_renderer = item.get("channelRenderer")
            if channel_renderer:
                url = extract_channel_url(channel_renderer)
                if url:
                    channels.add(url)
            # Nested in itemSectionRenderer
            section_items = item.get("itemSectionRenderer", {}).get("contents", [])
            for section_item in section_items:
                channel_renderer = section_item.get("channelRenderer")
                if channel_renderer:
                    url = extract_channel_url(channel_renderer)
                    if url:
                        channels.add(url)
    return channels

def fetch_channels_with_token(continuation_token: str):
    url = 'https://www.youtube.com/youtubei/v1/search?prettyPrint=false'
    headers = {
    }
    data = {
        "context": {
            "client": {
                "hl": "ja",
                "gl": "JP",
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
        channels = extract_channels_from_response(result)
        next_token = get_continuation_token(result)
        return channels, next_token
    except Exception:
        return set(), None

def parse_channel_list_from_search(
    event: CrawlEvent[None, Event, HtmlResponse],
    response: HtmlResponse,
) -> Iterable[Event]:
    all_channels = set()
    crawled_channel_ids = event.metadata.get('crawled_channel_ids', set())
    
    initial_data = get_yt_initial_data(response.url)
    if initial_data:
        token = get_continuation_token(initial_data)
        while token:
            more_channels, next_token = fetch_channels_with_token(token)
            all_channels.update(more_channels)
            token = next_token

    # Call parse_channel_detail for each channel URL
    for channel_url in all_channels:
            
        channel_id = channel_url.split('/')[-1]
        if channel_id in crawled_channel_ids:
            logging.info(f"Skipping already crawled channel: {channel_url}")
            continue
            
        logging.info(f"Processing channel URL: {channel_url}")
        yield CrawlEvent(
            request=Request(
                channel_url,
                method="GET"
            ),
            metadata=event.metadata,
            callback=parse_channel_detail
        )