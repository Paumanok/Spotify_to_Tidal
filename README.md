# Spotify_to_Tidal
spotify to tidal playlist converter

In order to use this, you must first generate a spotify client ID and secret. Put these spotify_auth_empty.py and rename it spotify_auth.py

Usage:
```
spotify_to_tidal.py --build_json --playlist_id <spotify playlist id> --create_playlist  --playlist_name "<name>" 

```


Requirements:
spotipy 
tidalapi V07.0 (0.7 is in beta right now so you may need to clone and install manually, pip version wont work)
tqdm
