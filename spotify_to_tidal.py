import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import tidalapi
import logging
import os.path
import time
from spotify_auth import spotify_auth

tidal_session_file = "tidal_session.json"
search_results_file = "tidal_search_results.txt"


def find_most_common(tracks):

    print("looking for the best match")
    id_tally = {}
    for query in tracks["q_results"]:
        #print("cur query: " + query["query"])
        for result in query["results"]:
            #print(result["name"])
            if "id" in result:

                if result["id"] in id_tally:
                    id_tally[result["id"]] += 1
                else:
                    id_tally[result["id"]] = 1
            else:
    
                if "tracks" in result:
                    for track in result["tracks"]:
                        if track["id"] in id_tally:
                            id_tally[track["id"]] += 1
                        else:
                            id_tally[track["id"]] = 1
    largest = None
    for t_id, tally in id_tally.items():
        if largest == None:
            largest = t_id
        else:
            if tally > id_tally[largest]:
                largest = t_id
    
    tracks["track"]["most_likely"] = largest
    print("most likely song: " +  str(largest))



def get_spotify_playlist():
    sa = spotify_auth()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=sa.client_id,
                                                                client_secret=sa.client_secret))
    playlist_id = "78YKN3vgPbQc5BX1LoePb4"
    
    #results = sp.playlist(playlist_id,fields='tracks.items.track(name,album(name,artists(name)))', offset=0)
    offset = 0
    results = sp.playlist_items(playlist_id,fields='items.track(name,album(name,artists(name))),total', offset=offset)
    n_items = len(results['items'])
    total = results['total']
    tracks = results["items"]
    while n_items < total:
        offset += 100
        results = sp.playlist_items(playlist_id,fields='items.track(name,album(name,artists(name))),total', offset=offset)
        tracks.extend(results["items"])
        n_items += len(tracks)
#    print(results)
   
    tracklist = []
    for track in tracks:
        #cur_track = track['track']['name'] + "<^>" + track['track']['album']['artists'][0]['name'] + "<^>" +  track['track']['album']['name']
        cur_track = {"name":track['track']['name'] , "artist": track['track']['album']['artists'][0]['name'], "album": track['track']['album']['name']}
     
        tracklist.append(cur_track)
    
    print("Found " + str(len(tracklist)) + " Songs on spotify playlist.")
    return tracklist

def get_tidal_session():

    session = tidalapi.Session()
    
    session.country_code = 'US'
    
    if os.path.isfile(tidal_session_file):
        with open(tidal_session_file, 'r') as fp:
            s_info = json.load(fp)
        if not session.load_oauth_session(s_info["session_id"], s_info["token_type"], s_info["access_token"]):
            print("session load failed")
            exit()
        
    else:
        session.login_oauth_simple()
        session_info = {"session_id": session.session_id, "token_type":session.token_type, "access_token":session.access_token}
        with open(tidal_session_file, 'w') as fp:
            json.dump(session_info, fp)

    return session


def build_json():
    
    tracklist = get_spotify_playlist()
    
    session = get_tidal_session()
    
    search_results = []
    
    for track in tracklist:
        #query = ' '.join(track.split('<^>')[0:2])
        #query2 = ' '.join([track.split('<^>')[0],track.split('<^>')[-1]])
        queries = [{"query" : ' '.join([track["name"]]), "models" : [tidalapi.media.Track]},
                {"query" : ' '.join([track["name"], track["artist"]]), "models" : [tidalapi.media.Track, tidalapi.artist.Artist]},
                {"query" : ' '.join([track["name"], track["artist"], track["album" ]]),"models": [tidalapi.media.Track, tidalapi.artist.Artist, tidalapi.album.Album]},
                {"query" : ' '.join([track["name"], track["album"]]), "models": [tidalapi.media.Track, tidalapi.album.Album]},
                {"query" : ' '.join([track["album"]]), "models":[tidalapi.album.Album]}]
        
        q_results = []  
    
        for query in queries:
            print("Searching for: " + query["query"])
            result = session.search(query["query"],models=query["models"])
            #print(result)
            result_array = []
            try:
                th = result["top_hit"]
                top_hit = {"name":th.name, "artist": th.artist.name, "album": th.album.name, "id":th.id}
            except:
                top_hit = None
    
            for res in result["tracks"]:
                result_array.append({ "name":res.name, "artist": res.artist.name, "album":res.album.name, "id":res.id})
            
            for res in result["albums"]:
                result_array.append({ "name": res.name, "artist": res.artist.name, "tracks": [{"track": x.name, "id": x.id} for x in res.tracks()]})
    
            search_result = {"query": query["query"], "top_hit": top_hit, "results":result_array}
    
            #print(result_array)
            q_results.append(search_result)
        
        track = {"track":track, "q_results":q_results}
        find_most_common(track)
        search_results.append(track)
    
    print("writing results")
    with open(search_results_file, 'w') as rfp:
        json.dump(search_results, rfp, indent=4)


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size)) 

def create_playlist():
    search_results = []
    
    with open(search_results_file, 'r') as rfp:
        search_results = json.load(rfp)
    
    session = get_tidal_session() 
    
    user = session.user
    
    playlist = user.create_playlist("skatest", "automating the pickitup")
    
    ids_to_add = []
    for track in search_results:
        if "most_likely" in track["track"]:
            m_l = track["track"]["most_likely"]
            if m_l is None:
                print("Could not find: " + track["track"]["name"] + ' ' + track["track"]["artist"])
            else:
                ids_to_add.append(track["track"]["most_likely"])

    print("Found " + str(len(ids_to_add)) + " tracks to populate. unfound tracks may still exist on tidal!")

    index = 0
    #print( len(ids_to_add))
    #print(len(get_spotify_playlist()))
    for group in chunker(ids_to_add, 50):
        try:
            playlist.add(group)
        except:
            print("not working: " + str(group))
            print(index)
        index +=1
    
#logging.basicConfig(level=logging.DEBUG)
#build_json()
#create_playlist()
#print(search_results)
get_spotify_playlist()







