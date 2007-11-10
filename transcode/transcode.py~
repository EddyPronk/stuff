import string
import cue
import os

file = open('montreux.cue')
input = file.read()
tokens = cue.parse('sheet', input)

state = 'header'

track = None

class Track:
    def __init__(self, album):
        self.album = album

    def __getattr__(self, name):
        return getattr(self.album, name)

class Album:
    def __init__(self):
        self.tracks = {}

album = Album()

for token in tokens:
    key   = token[0]
    value = token[1]
    if (state == 'header'):
        album.__dict__[key.lower()] = value
        if (key == 'TRACK'):
            state = 'tracks'

    if (state == 'tracks'):
        if (key == 'TRACK'):
            if track is not None:
                album.tracks[value] = track
            track = Track(album)
            track.number = value
        track.__dict__[key.lower()] = value

album.tracks[track.number] = track

class options:
    def __init__(self):
        self.str = []
        
    def option(self, key, value):
        self.str.append('%s "%s"' % (key, value))

for track in album.tracks.values():
    opt = options()
    opt.option('--tt', track.title) # title
    opt.option('--ta', track.performer) # artist
    opt.option('--tl', track.album.title) # album
    opt.option('--ty', track.year) # year
    opt.option('--tc', track.comment) # comment
    opt.option('--tn', track.number) # track

    dir = '/media/data/transcoded'
    os.mkdir(dir)
    filename = os.path.join(dir, '%02d. %s.mp3' % (track.number, track.title))
    cmd = 'flac --decode --silent --stdout "%s" | lame - "%s" --preset standard ' % (track.file, filename) + ' '.join(opt.str)
    print cmd
    if not os.path.exists(filename):
        pass
        #os.system(cmd)
