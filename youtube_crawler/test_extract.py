import json
import logging
import requests
import yt_dlp

logging.basicConfig(level=logging.INFO)

def extract_channels_from_response(data: dict) -> set:
    channels = set()
    try:
        # Log the full data structure for debugging
        logging.info("Full data structure:")
        logging.info(json.dumps(data, indent=2))
        
        # Try to get search results
        sections = (
            data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
        )
        
        logging.info("Search sections:")
        logging.info(json.dumps(sections, indent=2))
        
        for section in sections:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                # Handle search results
                if "videoRenderer" in item:
                    video = item["videoRenderer"]
                elif "searchPyvRenderer" in item:
                    # Handle ads
                    ads = item["searchPyvRenderer"].get("ads", [])
                    for ad in ads:
                        video = (
                            ad.get("adSlotRenderer", {})
                                .get("fulfillmentContent", {})
                                .get("fulfilledLayout", {})
                                .get("inFeedAdLayoutRenderer", {})
                                .get("renderingContent", {})
                                .get("promotedVideoRenderer")
                        )
                        if video:
                            break
                else:
                    continue
                
                if not video:
                    continue
                
                # Try different paths to get channel URL
                # Path 1: from longBylineText
                runs = video.get("longBylineText", {}).get("runs", [])
                if runs:
                    nav = runs[0].get("navigationEndpoint", {})
                    browse = nav.get("browseEndpoint", {})
                    canonical = browse.get("canonicalBaseUrl")
                    if canonical:
                        channels.add(f"https://www.youtube.com{canonical}")
                        continue
                
                # Path 2: from shortBylineText
                runs = video.get("shortBylineText", {}).get("runs", [])
                if runs:
                    nav = runs[0].get("navigationEndpoint", {})
                    browse = nav.get("browseEndpoint", {})
                    canonical = browse.get("canonicalBaseUrl")
                    if canonical:
                        channels.add(f"https://www.youtube.com{canonical}")
                        continue
                
                # Path 3: from channelId
                channel_id = video.get("channelId")
                if channel_id:
                    channels.add(f"https://www.youtube.com/channel/{channel_id}")
        
        logging.info(f"Total channels found: {len(channels)}")
        return channels
        
    except Exception as e:
        logging.error(f"Error extracting channels from response: {str(e)}")
        return set()

# Test data - you can paste your ytInitialData here
test_data = {
    "contents": {
        "twoColumnSearchResultsRenderer": {
            "primaryContents": {
                "sectionListRenderer": {
                    "contents": [
                        {
                            "itemSectionRenderer": {
                                "contents": [
                                    {
                                        "searchPyvRenderer": {
                                            "ads": [
                                                {
                                                    "adSlotRenderer": {
                                                        "fulfillmentContent": {
                                                            "fulfilledLayout": {
                                                                "inFeedAdLayoutRenderer": {
                                                                    "renderingContent": {
                                                                        "promotedVideoRenderer": {
                                                                            "longBylineText": {
                                                                                "runs": [
                                                                                    {
                                                                                        "text": "Wix Studio",
                                                                                        "navigationEndpoint": {
                                                                                            "browseEndpoint": {
                                                                                                "browseId": "UCdJdISP2jXUxBglXAHdcpSw",
                                                                                                "canonicalBaseUrl": "/@WixStudio"
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                ]
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
}

def test_channel_detail(channel_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            # Log the raw JSON response to check the structure
            logging.info(f"Raw JSON response: {json.dumps(info, indent=2)}")
            # Check for specific fields
            view_count = info.get('view_count')
            release_year = info.get('release_year')
            availability = info.get('availability')
            modified_date = info.get('modified_date')
            logging.info(f"View Count: {view_count}")
            logging.info(f"Release Year: {release_year}")
            logging.info(f"Availability: {availability}")
            logging.info(f"Modified Date: {modified_date}")
    except Exception as e:
        logging.error(f"Error fetching channel details: {str(e)}")

# Sample channel URL for testing
channel_url = 'https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw'
test_channel_detail(channel_url) 