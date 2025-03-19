# YouTube to Spotify Playlist Transfer

A web application that allows you to transfer your YouTube Music playlists to Spotify.

Currently deployed on https://youtubetospotify-lzsx.onrender.com via Render.

## Features

- Connect to your Spotify account
- Transfer YouTube Music playlists to Spotify
- Modern, responsive UI
- Secure authentication flow

## Setup

1. Create a Spotify Developer account and create a new application at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Get your Client ID and Client Secret from your Spotify application
3. Add your credentials to the `.env` file:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id_here
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
   SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
   ```
4. Install the required Python packages:
   ```bash
   pip install flask ytmusicapi spotipy python-dotenv
   ```

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:5000`
3. Click "Connect with Spotify" to authenticate
4. Enter your YouTube Music playlist URL
5. Click "Transfer Playlist" to start the transfer

## Requirements

- Python 3.9 or higher
- Spotify Developer account
- YouTube Music account

## Note

This application uses the unofficial YouTube Music API (ytmusicapi). Please be aware that this is not an official API and may be subject to changes or restrictions. 
