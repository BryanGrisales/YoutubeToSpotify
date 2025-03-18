from flask import Flask, render_template, request, jsonify, session
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:5000/callback'

# Debug logging
print(f"Client ID: {SPOTIFY_CLIENT_ID}")
print(f"Client Secret: {'*' * len(SPOTIFY_CLIENT_SECRET) if SPOTIFY_CLIENT_SECRET else 'None'}")
print(f"Redirect URI: {SPOTIFY_REDIRECT_URI}")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("Missing Spotify credentials in .env file")

# Initialize Spotify OAuth
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope='playlist-modify-public playlist-modify-private'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    try:
        auth_url = sp_oauth.get_authorize_url()
        print(f"Generated auth URL: {auth_url}")  # Debug logging
        return jsonify({'auth_url': auth_url})
    except Exception as e:
        print(f"Error in /auth: {str(e)}")  # Debug logging
        return jsonify({'error': str(e)}), 500

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        print(f"Received code in callback: {code[:10]}...")  # Debug logging (first 10 chars only for security)
        
        if not code:
            error = request.args.get('error', 'No code received')
            print(f"Error in callback: {error}")  # Debug logging
            return render_template('index.html', error=error)

        token_info = sp_oauth.get_access_token(code)
        print("Successfully obtained token")  # Debug logging
        
        # Store token in session
        session['spotify_token'] = token_info
        
        return render_template('callback.html', token_info=token_info)
    except Exception as e:
        print(f"Error in /callback: {str(e)}")  # Debug logging
        return render_template('index.html', error=str(e))

@app.route('/transfer', methods=['POST'])
def transfer_playlist():
    try:
        data = request.json
        yt_playlist_url = data.get('playlist_url')
        spotify_token = data.get('spotify_token')
        
        if not yt_playlist_url or not spotify_token:
            return jsonify({'error': 'Missing required parameters'}), 400

        # Initialize Spotify client
        sp = spotipy.Spotify(auth=spotify_token)
        
        # Initialize YTMusic
        ytmusic = YTMusic()
        
        # Extract playlist ID from URL
        playlist_id = None
        if 'list=' in yt_playlist_url:
            playlist_id = yt_playlist_url.split('list=')[1].split('&')[0]
        
        if not playlist_id:
            return jsonify({'error': 'Invalid YouTube Music playlist URL'}), 400

        # Get playlist details from YouTube Music
        playlist = ytmusic.get_playlist(playlist_id)
        playlist_name = playlist['title']
        tracks = playlist['tracks']

        # Create new Spotify playlist
        user_id = sp.current_user()['id']
        spotify_playlist = sp.user_playlist_create(
            user_id,
            f"{playlist_name} (from YouTube Music)",
            public=False,
            description="Transferred from YouTube Music"
        )

        # Track statistics
        found_tracks = []
        not_found_tracks = []
        spotify_track_uris = []

        # Process each track
        for track in tracks:
            title = track['title']
            artist = track['artists'][0]['name'] if track['artists'] else ''
            
            search_query = f"{title} artist:{artist}"
            search_result = sp.search(search_query, type='track', limit=1)
            
            if search_result['tracks']['items']:
                spotify_track = search_result['tracks']['items'][0]
                spotify_track_uris.append(spotify_track['uri'])
                found_tracks.append(f"{title} - {artist}")
            else:
                not_found_tracks.append(f"{title} - {artist}")

        # Add tracks to Spotify playlist in batches of 100
        if spotify_track_uris:
            for i in range(0, len(spotify_track_uris), 100):
                batch = spotify_track_uris[i:i + 100]
                sp.playlist_add_items(spotify_playlist['id'], batch)

        return jsonify({
            'message': f'Successfully transferred {len(found_tracks)} tracks to Spotify',
            'not_found': not_found_tracks,
            'playlist_url': spotify_playlist['external_urls']['spotify']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 