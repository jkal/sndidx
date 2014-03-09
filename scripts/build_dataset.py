#!/usr/bin/env python

import sys
import json
import requests
import scipy
import pickle
import time
import pyechonest
from pyechonest import config, artist, song
from pymongo import MongoClient
config.ECHO_NEST_API_KEY = 'FILLMEUP'

client = MongoClient()
db = client.local
col = db.echonest_data

def get_metadata(song):
    metadata = {
        'song_id': song.id,
        'title': song.title,
        'artist': song.artist_name,
        'artist_id': song.artist_id,
    }
    return metadata

def get_segments(song):
    song.get_audio_summary()
    analysis_url = song.audio_summary['analysis_url']

    r = requests.get(analysis_url)
    analysis = r.json()

    return analysis['segments']

def extract_features(segments):
    features = []
    for segment in segments:
        segments_dict = {}
        segments_dict['start'] = segment['start']
        segments_dict['duration'] = segment['duration']
        segments_dict['loudness'] = segment['loudness_max']
        segments_dict['timbre'] = scipy.array(segment['timbre']).var()
        segments_dict['pitch'] = scipy.array(segment['pitches']).mean()
        features.append(segments_dict)
    return features

def main():
    artists = pickle.load(open('artists.pickle'))
    sys.stdout.write('Building...'); sys.stdout.flush()

    start = len(artists)/2+350
    for i, artist in enumerate(artists[start:]):
        try:
            songs = song.search(artist_id=artist.id)
        except pyechonest.util.EchoNestAPIError, e:
            sys.stdout.write('XXX'); sys.stdout.flush()
            continue

        for j, sng in enumerate(songs):
            metadata = get_metadata(sng)
            try:
                segments = get_segments(sng)
            except pyechonest.util.EchoNestAPIError, e:
                time.sleep(30)
                continue

            features = extract_features(segments)
            metadata.update({
                'features': features,
            })
            col.insert(metadata)
            sys.stdout.write('.')
            sys.stdout.flush()

            if j % 5 == 0:
                sys.stdout.write('zzz'); sys.stdout.flush()
                time.sleep(2)

        sys.stdout.write('zzz'); sys.stdout.flush()
        time.sleep(2)
        
if __name__ == '__main__':
    main()