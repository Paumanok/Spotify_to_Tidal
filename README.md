# Spotify_to_Tidal
spotify to tidal playlist converter

In order to use this, you must first generate a spotify client ID and secret. Put these spotify_auth_empty.py and rename it spotify_auth.py

Next, find "playlist_id" and edit it for the playlist you want to copy.
Edit the playlist creation line in "create_playlist()" to change your target playlist name and description 

Next, since I didn't implement any usecase flow, edit the bottom of the file to run "build_json()" This does several things. First it will reach out to spotify and grab the song list from your target playlist. 
Then it will attempt to authenticate with Tidal. On the first run it will print out a link you must go to in order to authenticate with oauth. This will create a session file that will eventually expire, but keeps things going in the short term. 
Next it will do the longest leg of the journey, the search function. I cross reference 5 querys of different types to find the common(hopefully correct) song/album/artist from the source playlist. Occasionally this will fail to find some. This is due to Tidal's search being bad for the most part and doesn't mean the song doesn't exist on tidal.

This will finish with a big JSON blob in your current directory. Edit the file at the bottom again to remove "build_json" and add "create_playlist".
If you're brave you can run both but its good to verify output before cluttering your tidal playlist screen. 

By the end you should have most of a transfered playlist. Goodluck! I might update this to be more user friendly in the future. 
