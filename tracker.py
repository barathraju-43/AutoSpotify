import spotipy
import spotipy.util as util
import os
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')

# Email credentials
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# Spotify playlist ID
PLAYLIST_ID = os.environ.get('source_playlist_id')

# Function to authenticate with Spotify API
def authenticate():
    username = os.environ.get('USERNAME')
    scope = 'playlist-modify-private playlist-modify-public'

    token = util.prompt_for_user_token(username, scope,
                                       client_id=SPOTIFY_CLIENT_ID,
                                       client_secret=SPOTIFY_CLIENT_SECRET,
                                       redirect_uri=SPOTIFY_REDIRECT_URI)

    if token:
        return spotipy.Spotify(auth=token)
    else:
        print("Can't get token for", username)
        return None

# Function to send email notifications
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, text)
    server.quit()

# Function to monitor playlist changes
def monitor_playlist():
    sp = authenticate()
    if not sp:
        return

    prev_snapshot = None

    while True:
        try:
            playlist = sp.playlist(PLAYLIST_ID)
            current_snapshot = json.dumps(playlist['tracks']['items'])
            
            if prev_snapshot is not None and prev_snapshot != current_snapshot:
                # Playlist has been modified
                # diff = json.loads(current_snapshot) - json.loads(prev_snapshot)
                current_tracks = [track['track']['name'] for track in json.loads(current_snapshot)]
                prev_tracks = [track['track']['name'] for track in json.loads(prev_snapshot)]

                added_tracks = [track for track in current_tracks if track not in prev_tracks]
                removed_tracks = [track for track in prev_tracks if track not in current_tracks]
                # added_songs = [track['track']['name'] for track in diff]
                # removed_songs = [track['track']['name'] for track in diff]
                modified_at = time.strftime('%Y-%m-%d %H:%M:%S')

                subject = 'Playlist Modification Detected'
                body = f"Playlist modified at {modified_at}.\n"
                body += f"Added Songs: {added_tracks}\n"
                body += f"Removed Songs: {removed_tracks}\n"
                send_email(subject, body)

            prev_snapshot = current_snapshot
            time.sleep(60)  # Check every minute

        except Exception as e:
            print("Error:", e)

# Start monitoring the playlist
monitor_playlist()
