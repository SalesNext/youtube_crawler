from typing import Dict, Any, Optional, List, Iterable
import yt_dlp
import json
from salesnext_crawler.events import CrawlEvent, DataEvent, Event
import logging
from scrapy.http.response.html import HtmlResponse
from youtube_crawler.schema.v1.youtube import Thumbnail, Comment, Video, ChannelDetail, SubtitleInfo

def parse_channel_detail(
    event: CrawlEvent[None, Event, HtmlResponse],
    response: HtmlResponse,
) -> Iterable[Event]:
    """Parse channel detail using yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
            'extract_metadata': True,
            'skip_download': True,
            'writecomments': True,  # Enable comment extraction
            'getcomments': True,    # Get comments
            'writesubtitles': True,  # Enable subtitle extraction
            'subtitleslangs': ['ja'],  # Get Japanese subtitles
            'writeautomaticsub': True,  # Get auto-generated subtitles if available
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            channel_info = ydl.extract_info(response.url, download=False)
            if not channel_info:
                logging.error(f"Failed to extract info for channel {response.url}")
                return
                
            logging.info(f"Successfully extracted info for channel {response.url}")
            
            # Log raw channel info for debugging
            logging.info("Raw channel info:")
            logging.info(json.dumps(channel_info, indent=2, default=str))
            
            # Extract channel info using ChannelDetail schema
            channel_detail = ChannelDetail(
                id=channel_info.get('id'),
                channel=channel_info.get('channel'),
                channel_id=channel_info.get('channel_id'),
                title=channel_info.get('title'),
                channel_follower_count=channel_info.get('channel_follower_count'),
                description=channel_info.get('description', ''),
                tags=channel_info.get('tags', []),
                thumbnails=channel_info.get('thumbnails', []),
                uploader_id=channel_info.get('uploader_id'),
                uploader_url=channel_info.get('uploader_url'),
                uploader=channel_info.get('uploader'),
                channel_url=channel_info.get('channel_url'),
                playlist_count=channel_info.get('playlist_count', 0),
                webpage_url=channel_info.get('webpage_url'),
                extractor=channel_info.get('extractor'),
                extractor_key=channel_info.get('extractor_key'),
                modified_date=channel_info.get('modified_date'),
                view_count=channel_info.get('view_count'),
                availability=channel_info.get('availability'),
                release_year=channel_info.get('release_year'),
                epoch=channel_info.get('epoch')
            )
            
            # Log processed channel detail for debugging
            logging.info("Processed channel detail:")
            logging.info(json.dumps(channel_detail, indent=2, default=str))
            
            yield DataEvent("channel", channel_detail)
            
            # Extract video info
            entries = channel_info.get('entries', [])
            for entry in entries:
                if entry:
                    # Get video comments and subtitles
                    video_url = entry.get('url')
                    comments = []
                    subtitles = []
                    if video_url:
                        try:
                            video_info = ydl.extract_info(video_url, download=False)
                            if video_info and isinstance(video_info, dict):
                                # Get comments
                                if 'comments' in video_info and video_info['comments']:
                                    for comment in video_info['comments']:
                                        if comment and isinstance(comment, dict):
                                            comments.append(Comment(
                                                id=comment.get('id'),
                                                text=comment.get('text', ''),
                                                author=comment.get('author', ''),
                                                author_id=comment.get('author_id', ''),
                                                author_url=comment.get('author_url', ''),
                                                like_count=comment.get('like_count', 0),
                                                timestamp=comment.get('timestamp', 0),
                                                parent_id=comment.get('parent_id'),
                                                reply_count=comment.get('reply_count', 0)
                                            ))
                                # Get subtitles
                                if 'subtitles' in video_info and video_info['subtitles']:
                                    for lang, subtitle_info in video_info['subtitles'].items():
                                        if subtitle_info and isinstance(subtitle_info, list):
                                            for fmt in subtitle_info:
                                                if fmt and isinstance(fmt, dict):
                                                    subtitles.append(SubtitleInfo(
                                                        url=fmt.get('url'),
                                                        ext=fmt.get('ext'),
                                                        name=fmt.get('name'),
                                                        protocol=fmt.get('protocol'),
                                                        data=fmt.get('data'),
                                                        lang=lang,
                                                        lang_code=lang,
                                                        is_auto=False
                                                    ))
                                elif 'automatic_captions' in video_info and video_info['automatic_captions']:
                                    for lang, subtitle_info in video_info['automatic_captions'].items():
                                        if subtitle_info and isinstance(subtitle_info, list):
                                            for fmt in subtitle_info:
                                                if fmt and isinstance(fmt, dict):
                                                    subtitles.append(SubtitleInfo(
                                                        url=fmt.get('url'),
                                                        ext=fmt.get('ext'),
                                                        name=fmt.get('name'),
                                                        protocol=fmt.get('protocol'),
                                                        data=fmt.get('data'),
                                                        lang=lang,
                                                        lang_code=lang,
                                                        is_auto=True
                                                    ))
                        except Exception as e:
                            logging.error(f"Error getting info for video {video_url}: {str(e)}")
                            logging.error(f"Video info: {video_info if 'video_info' in locals() else 'Not available'}")

                    video_detail = Video(
                        id=entry.get('id'),
                        url=entry.get('url'),
                        title=entry.get('title'),
                        description=entry.get('description', ''),
                        duration=entry.get('duration', 0),
                        view_count=entry.get('view_count', 0),
                        like_count=video_info.get('like_count', 0) if 'video_info' in locals() else 0,
                        upload_date=video_info.get('upload_date') if 'video_info' in locals() else None,
                        thumbnails=entry.get('thumbnails', []),
                        channel_id=channel_info.get('channel_id'),
                        channel_url=channel_info.get('channel_url'),
                        channel=channel_info.get('channel'),
                        uploader=channel_info.get('uploader'),
                        uploader_id=channel_info.get('uploader_id'),
                        uploader_url=channel_info.get('uploader_url'),
                        webpage_url=entry.get('webpage_url'),
                        extractor=entry.get('extractor'),
                        extractor_key=entry.get('extractor_key'),
                        timestamp=entry.get('timestamp'),
                        release_timestamp=entry.get('release_timestamp'),
                        availability=entry.get('availability'),
                        live_status=entry.get('live_status'),
                        channel_is_verified=entry.get('channel_is_verified'),
                        comments=comments,
                        subtitles=subtitles
                    )
                    yield DataEvent("video", video_detail)
            
    except Exception as e:
        logging.error(f"Error parsing channel {response.url}: {str(e)}")
        return 