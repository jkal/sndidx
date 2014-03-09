#!/usr/bin/env python
import sys
import time
import pyechonest
import pickle
from pyechonest import config, artist, song

config.ECHO_NEST_API_KEY = 'FILLMEUP'

artists =  [
    'daft punk', 'justice', 'mogwai', 'm83', 'ratatat', 'explosions in the sky', 'royksopp', 'futurecop',
    'miami horror', 'tortoise', 'deadmau5', 'the xx', 'the black keys', 'the cardigans', 'garbage', 'blur',
    'fiona apple', 'apparat', 'caspian', 'empire of the sun', 'the fray', 'iced earth', 'opeth', 'megadeth',
    'nevermore', 'metallica', 'iron maiden', 'blind guardian', 'death', 'judas priest', 'in flames',
    'Wolfgang Amadeus Mozart', 'Ludwig Van Beethoven', 'Frederic Chopin', 'Sergei Rachmaninov', 'Claude Debussy',
    'Robert Schumann', 'Johann Sebastian Bach', 'Peter Ilyich Tchaikovsky', 'Franz Liszt', 'Felix Mendelssohn',
    'Louis Armstrong', 'Duke Ellington', 'Charlie Parker', 'Miles Davis', 'Billy Holiday', 'Benny Goodman',
    'Coleman Hawkins', 'Count Basie', 'John Coltrane', 'Dizzy Gillespie', 'Nina Simone', 'Arcade Fire', 'Deerhunter',
    'Moby', 'The Verve', 'Oasis', 'Fleet Foxes', 'Styx', 'Hans Zimmer', 'Cut Copy', 'Wolfmother', 'Cream',
    'Radiohead', 'Bon Iver', 'Orbital', 'Fountains of Wayne', 'Clint Mansell', 'Nada Surf', 'Chromeo', 'Gomez',
    'Gorillaz', 'mgmt', 'sigur ros', 'danger mouse', 'modest mouse', 'editors', 'foo fighters', 'the national',
    'metric', 'the frames', 'foghat', 'typhoon', 'joe satriani', 'dire straits', 'massive attack', 'eric clapton',
    'queen', 'kraftwerk', 'muse', 'creedence', 'the darkness', 'dandy warhols', 'cutting crew', 'kasabian', 'the who',
    'whitesnake', 'kansas', 'jimi hendrix', 'the prodigy', 'nine inch nails', 'ted nugent', 'al green', 'starsailor',
    'u2', 'the beatles', 'rolling stones', 'ac/dc', 'the radio dept', 'lcd soundsystem', 'unkle', 'the used',
    'kings of leon'
]

def main():
    sys.stdout.write('Extending artists:')
    extended = []
    for artist_name in artists:
        try:
            a = artist.Artist(artist_name)
            extended.append(a)
            similars = a.similar[:10]
        except pyechonest.util.EchoNestAPIError, e:
            continue

        for sim in similars:
            extended.append(sim)
            sys.stdout.write('.'); sys.stdout.flush()
        time.sleep(5)
        sys.stdout.write('zzz'); sys.stdout.flush()

    sys.stdout.write('\nDone.'); sys.stdout.flush()

    with open('artists.pickle', 'a') as f:
        pickle.dump(extended, f)

if __name__ == '__main__':
    main()