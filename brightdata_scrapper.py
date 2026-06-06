import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_ids_from_channel(channel_url, max_videos=10):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': max_videos * 3,
    }
    video_ids = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url + "/videos", download=False)
        if 'entries' in info:
            for entry in info['entries']:
                if len(video_ids) >= max_videos:
                    break
                if entry.get('id'):
                    video_ids.append(entry['id'])
    return video_ids

def get_video_ids_from_keyword(keyword, max_videos=10, country=None):
    search_url = f"ytsearch{max_videos}:{keyword}"
    ydl_opts = {'quiet': True, 'extract_flat': True}
    video_ids = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_url, download=False)
        if 'entries' in info:
            for entry in info['entries']:
                if entry.get('id'):
                    video_ids.append(entry['id'])
    return video_ids

def get_video_details(video_id):
    ydl_opts = {'quiet': True}
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'id': video_id,
                'shortcode': video_id,
                'url': url,
                'title': info.get('title', ''),
                'channel_name': info.get('uploader', ''),
                'channel_url': info.get('uploader_url', ''),
                'views': info.get('view_count', 0),
                'likes': info.get('like_count', 0),
                'date_posted': info.get('upload_date', ''),
                'description': info.get('description', ''),
                'formatted_transcript': []
            }
    except Exception as e:
        return {
            'id': video_id,
            'shortcode': video_id,
            'url': url,
            'title': 'Unknown',
            'channel_name': '',
            'channel_url': '',
            'views': 0,
            'likes': 0,
            'date_posted': '',
            'description': '',
            'formatted_transcript': []
        }

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return [
            {
                'start_time': t['start'],
                'end_time': t['start'] + t['duration'],
                'text': t['text']
            }
            for t in transcript
        ]
    except:
        return []

def trigger_scraping_channels(api_key, channel_urls, num_videos, start_date, end_date, sort_by, keyword):
    videos = []
    for url in channel_urls:
        if not url.strip():
            continue
        video_ids = get_video_ids_from_channel(url.strip(), max_videos=num_videos)
        for vid_id in video_ids:
            video = get_video_details(vid_id)
            video['formatted_transcript'] = get_transcript(vid_id)
            videos.append(video)
    return {"snapshot_id": "local", "_videos": videos}

def trigger_scraping_niche(api_key, keyword, num_videos, start_date, end_date, country, endpoint):
    videos = []
    video_ids = get_video_ids_from_keyword(keyword, max_videos=num_videos, country=country)
    for vid_id in video_ids:
        video = get_video_details(vid_id)
        video['formatted_transcript'] = get_transcript(vid_id)
        videos.append(video)
    return {"snapshot_id": "local", "_videos": videos}

def get_progress(api_key, snapshot_id):
    return {"status": "ready"}

def get_output(api_key, snapshot_id, format="json"):
    return [[]]
