# spotify_logic.py
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
import requests
from io import BytesIO
import textwrap

load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SECRET_ID = os.getenv("SPOTIFY_SECRET")

# Spotipy OAuth manager - uses .cache file for token persistence
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=SECRET_ID,
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-currently-playing user-read-playback-state",
    cache_path=".spotify_cache"
))

# Color scheme
BG_WHITE = "#FFFFFF"
TEXT_BLACK = "#000000"

def draw_wrapped_text(draw, text, x, y, font, fill, max_width):
    """Draw text with wrapping if it exceeds max_width"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:  # Save current line and start new one
                lines.append(' '.join(current_line))
                current_line = [word]
            else:  # Single word is too long
                lines.append(word[:20] + "...")
                current_line = []
    
    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw each line
    line_height = font.size + 5
    for i, line in enumerate(lines):
        draw.text((x, y + (i * line_height)), line, fill=fill, font=font, anchor="lm")
    
    return len(lines) * line_height  # Return total height used

def render(width: int, height: int) -> Image.Image:
    # Render Spotify 'Now Playing' screen
    img = Image.new("RGB", (width, height), TEXT_BLACK)
    draw = ImageDraw.Draw(img)
    
    font_path = FredokaOne
    title_font = ImageFont.truetype(font_path, size=25)
    artist_font = ImageFont.truetype(font_path, size=20)
    header_font = ImageFont.truetype(font_path, size=20)
    
    try:
        current_track = sp.current_user_playing_track()
        
        if current_track is None or not current_track.get('is_playing'):
            # Nothing playing
            draw.text((width/2, height/2), "Nothing Playing", 
                     fill=BG_WHITE, font=title_font, anchor="mm")
            return img
        
        # Extract track info
        track_name = current_track['item']['name']
        artists = ", ".join([artist['name'] for artist in current_track['item']['artists']])
        
        # Get album cover image URL (640x640 is the largest)
        album_images = current_track['item']['album']['images']
        cover_size = 400
        cover_x = width - cover_size - 40  # 40px margin from right
        
        if album_images:
            cover_url = album_images[0]['url']  # Largest image
            
            # Download and resize album cover
            response = requests.get(cover_url)
            cover_img = Image.open(BytesIO(response.content))
            
            cover_img = cover_img.resize((cover_size, cover_size))
            
            # Position cover on the right side
            cover_y = (height - cover_size) // 2  # Vertically centered
            img.paste(cover_img, (cover_x, cover_y))
        
        # Calculate max text width (left margin to cover start, minus some padding)
        text_x = 40  # Left margin
        max_text_width = cover_x - text_x - 20  # 20px padding before cover
        
        # Draw header on the left
        draw.text((text_x, 100), "Now Playing", fill=BG_WHITE, font=header_font, anchor="lm")
        
        # Draw track name with wrapping
        text_y_start = 180
        title_height = draw_wrapped_text(draw, track_name, text_x, text_y_start, 
                        title_font, BG_WHITE, max_text_width)
        
        # Draw artist name below track name (with wrapping)
        artist_y = text_y_start + title_height + 20  # 20px gap
        draw_wrapped_text(draw, artists, text_x, artist_y, 
                        artist_font, BG_WHITE, max_text_width)
        
    except Exception as e:
        # Error handling
        draw.text((width/2, height/2), f"Spotify Error", 
                 fill=BG_WHITE, font=title_font, anchor="mm")
        draw.text((width/2, height/2 + 50), str(e)[:50], 
                 fill=BG_WHITE, font=artist_font, anchor="mm")
    
    return img

if __name__ == "__main__":
    # Test render
    img = render(800, 480)
    img.show()