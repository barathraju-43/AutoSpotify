import spotipy, os, time
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

print(SPOTIFY_CLIENT_ID)
# Set up authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri='http://localhost:8888/callback',
                                               scope='playlist-modify-public'))

def get_added_by_user(track):
    # Fetch the user who added the track
    if 'added_by' in track and track['added_by'] is not None:
        return track['added_by']['id']
    else:
        return None

def song_exists_in_playlist(playlist_id, track_uri):
    # Check if a song exists in the playlist
    playlist_tracks = sp.playlist_tracks(playlist_id)
    for item in playlist_tracks['items']:
        if item['track']['uri'] == track_uri:
            return True
    return False

def add_new_songs(source_playlist_id, destination_playlist_id):

    source_tracks = sp.playlist_tracks(source_playlist_id)

    for track in source_tracks['items']:
        # Fetch track URI and the user who added the track in the source playlist
        track_uri = track['track']['uri']
        added_by_user = get_added_by_user(track)

        # Check if the song already exists in the destination playlist
        if not song_exists_in_playlist(destination_playlist_id, track_uri):
            # Add track to the destination playlist
            sp.playlist_add_items(destination_playlist_id, [track_uri])

            # Update the description of the destination playlist
            playlist_details = sp.playlist(destination_playlist_id)
            description = playlist_details['description']

            # Append the added by information to the playlist description
            track_name = track['track']['name']
            track_description = f"{track_name} - Added by: {added_by_user}\n"
            description += track_description

            # Update the destination playlist's description
            sp.playlist_change_details(destination_playlist_id, description=description)
        else:
            print(f"Song {track['track']['name']} already exists in the destination playlist. Skipping...")

    print("Songs added to the destination playlist successfully!")


if __name__ == "__main__":
   
    source_playlist_id = os.getenv('source_playlist_id')
    destination_playlist_id = os.getenv('destination_playlist_id')

    # Set up a loop for continuous execution
    while True:
        try:
            add_new_songs(source_playlist_id, destination_playlist_id)
            print("Waiting for updates...")
        except Exception as e:
            print("An error occurred:", e)
        
        # Sleep for a specified interval before the next iteration
        time.sleep(30)  # Sleep for 30 seconds (adjust as needed)


    