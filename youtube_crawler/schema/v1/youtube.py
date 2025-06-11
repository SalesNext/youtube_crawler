from typing import TypedDict, Dict, Any, Optional, List

class Thumbnail(TypedDict):
    url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    id: Optional[str] = None
    resolution: Optional[str] = None
    preference: Optional[int] = None

class Comment(TypedDict):
    id: Optional[str] = None
    text: Optional[str] = None
    author: Optional[str] = None
    author_id: Optional[str] = None
    author_url: Optional[str] = None
    like_count: Optional[int] = None
    timestamp: Optional[int] = None
    parent_id: Optional[str] = None
    reply_count: Optional[int] = None

class SubtitleInfo(TypedDict):
    url: Optional[str] = None
    ext: Optional[str] = None
    name: Optional[str] = None
    protocol: Optional[str] = None
    data: Optional[str] = None
    lang: Optional[str] = None
    lang_code: Optional[str] = None
    is_auto: Optional[bool] = None

class Video(TypedDict):
    id: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[float] = None
    view_count: Optional[int] = None
    thumbnails: Optional[List[Thumbnail]] = None
    channel_id: Optional[str] = None
    channel_url: Optional[str] = None
    channel: Optional[str] = None
    uploader: Optional[str] = None
    uploader_id: Optional[str] = None
    uploader_url: Optional[str] = None
    webpage_url: Optional[str] = None
    extractor: Optional[str] = None
    extractor_key: Optional[str] = None
    timestamp: Optional[int] = None
    release_timestamp: Optional[int] = None
    availability: Optional[str] = None
    live_status: Optional[str] = None
    channel_is_verified: Optional[bool] = None
    comments: Optional[List[Comment]] = None
    subtitles: Optional[List[SubtitleInfo]] = None

class ChannelDetail(TypedDict):
    id: Optional[str] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    title: Optional[str] = None
    channel_follower_count: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    thumbnails: Optional[List[Thumbnail]] = None
    uploader_id: Optional[str] = None
    uploader_url: Optional[str] = None
    uploader: Optional[str] = None
    channel_url: Optional[str] = None
    playlist_count: Optional[int] = None
    webpage_url: Optional[str] = None
    extractor: Optional[str] = None
    extractor_key: Optional[str] = None
    modified_date: Optional[str] = None
    view_count: Optional[int] = None
    availability: Optional[str] = None
    release_year: Optional[int] = None
    epoch: Optional[int] = None 