#!/usr/bin/env python
import sys
from rtree import index

from pymongo import MongoClient

client = MongoClient()
db = client.local
col = db.echonest_data

def main():
    p = index.Property()
    p.dimension = 3
    idx = index.Index('3d_index', properties=p)

    i = 0
    for song in col.find():
        song_features = song['features']
        for f in song_features:
            coord = (f['timbre'], f['loudness'], f['pitch'])
            idx.insert(id=i, coordinates=coord, obj=song['song_id'])
            i += 1
        sys.stdout.write('.'); sys.stdout.flush()

if __name__ == '__main__':
    main()
