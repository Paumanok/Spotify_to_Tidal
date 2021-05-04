# Spotify_to_Tidal
spotify to tidal playlist converter

In order to use this, you must first generate a spotify client ID and secret. Put these spotify_auth_empty.py and rename it spotify_auth.py

Usage:
```
  python3 spotify_to_tidal.py --build_json --playlist_id 6Ig27y0QryKLs9BWhzhfc6 --create_playlist  --playlist_name "polyvinyl test" 

```


Requirements:
spotipy 
tidalapi V07.0 (0.7 is in beta right now so you may need to clone and install manually, pip version wont work)
tqdm
