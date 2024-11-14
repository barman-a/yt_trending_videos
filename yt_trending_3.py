import streamlit as st
import requests
from datetime import datetime
import base64

st.set_page_config(layout="wide")

# Custom CSS for better typography and visuals
st.markdown("""
<style>
    .video-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .channel-name {
        font-size: 14px;
        color: #606060;
        margin-bottom: 10px;
    }
    .stats {
        font-size: 12px;
        color: #606060;
    }
    .thumbnail-container {
        position: relative;
        margin-bottom: 10px;
    }
    .view-count {
        position: absolute;
        bottom: 5px;
        right: 5px;
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎥 YouTube Trending Videos")

# Sidebar for country selection
st.sidebar.header("🌍 Select Country")
country = st.sidebar.radio("Choose a country:", ["USA", "UK", "India"])

# API key input
api_key = st.sidebar.text_input("🔑 Enter your YouTube API key:", type="password")

# Function to format numbers
def format_number(num):
    if num >= 1000000000:
        return f"{num/1000000000:.1f}B"
    elif num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

# Function to retrieve data from YouTube API
def get_youtube_data(region, max_result):
    url = f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode={region}&maxResults={max_result}&key={api_key}"
    response = requests.get(url)
    return response.json()

# Function to get YouTube channel data
def get_youtube_channel_data(cid):
    url = f"https://www.googleapis.com/youtube/v3/channels?id={cid}&key={api_key}&fields=items(statistics(subscriberCount,videoCount),snippet(title))&part=statistics,snippet"
    response = requests.get(url)
    return response.json()

# Function to create clickable thumbnail with view count
def clickable_thumbnail(video_id, view_count):
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    formatted_views = format_number(int(view_count))
    return f"""
    <div class="thumbnail-container">
        <a href="{video_url}" target="_blank">
            <img src="{thumbnail_url}" width="100%">
            <div class="view-count">{formatted_views} views</div>
        </a>
    </div>
    """

# Main app logic
if api_key:
    region_code = {"USA": "US", "UK": "GB", "India": "IN"}[country]
    
    with st.spinner(f"Fetching trending videos for {country}..."):
        youtube_data = get_youtube_data(region_code, 50)
        
        if 'items' in youtube_data:
            st.subheader(f"📈 Trending Videos in {country}")
            
            for i in range(0, len(youtube_data['items']), 5):
                cols = st.columns(5)
                for j, item in enumerate(youtube_data['items'][i:i+5]):
                    with cols[j]:
                        snippet = item['snippet']
                        statistics = item['statistics']
                        video_id = item['id']
                        
                        # Clickable thumbnail with view count
                        st.markdown(clickable_thumbnail(video_id, statistics['viewCount']), unsafe_allow_html=True)
                        
                        # Video title
                        st.markdown(f"<div class='video-title'>{snippet['title'][:50]}{'...' if len(snippet['title']) > 50 else ''}</div>", unsafe_allow_html=True)
                        
                        # Channel info
                        channel_id = snippet['channelId']
                        channel_data = get_youtube_channel_data(channel_id)
                        if 'items' in channel_data and channel_data['items']:
                            channel_info = channel_data['items'][0]
                            channel_title = channel_info['snippet']['title']
                            channel_url = f"https://www.youtube.com/channel/{channel_id}"
                            st.markdown(f"<div class='channel-name'><a href='{channel_url}' target='_blank'>{channel_title}</a></div>", unsafe_allow_html=True)
                            
                            # Channel stats
                            subscribers = int(channel_info['statistics']['subscriberCount'])
                            total_videos = int(channel_info['statistics']['videoCount'])
                            likes = int(statistics.get('likeCount', 0))
                            
                            st.markdown(f"""
                            <div class='stats'>
                                👥 {format_number(subscribers)} subscribers<br>
                                🎥 {format_number(total_videos)} videos<br>
                                👍 {format_number(likes)} likes
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
        else:
            st.error("Failed to fetch YouTube data. Please check your API key and try again.")
else:
    st.warning("Please enter your YouTube API key in the sidebar to proceed.")
