#! /usr/bin/env python

# Copyright (C) 2007 Eddy Pronk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import string
import cuesheet
import os

cue_sheet = '/home/epronk/4dafunk/4DaFunk/4DaFunk Open Sessions/cd1/disc1.cue'

dir, filename = os.path.split(cue_sheet)
os.chdir(dir)
file = open(filename)
input = file.read()
tokens = cuesheet.parse('sheet', input)

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

output_root_dir = '/media/data/transcoded'
album_dir = '%s - %s' % (album.performer, album.title)
dir = os.path.join(output_root_dir, album_dir)

if not os.path.exists(dir):
    os.mkdir(dir)

for track in album.tracks.values():
    opt = options()
    opt.option('--tt', track.title) # title
    opt.option('--ta', track.performer) # artist
    opt.option('--tl', track.album.title) # album
    opt.option('--ty', track.year) # year
    opt.option('--tc', track.comment) # comment
    opt.option('--tn', track.number) # track

    filename = os.path.join(dir, '%02d. %s.mp3' % (track.number, track.title))
    lame = 'lame - "%s" --quiet --preset standard ' % filename + ' '.join(opt.str)
    #cmd = 'flac --decode --silent --stdout "%s" | %s' % (track.file, lame)
    cmd = 'mac "%s" /dev/stdout -d 2>&1 >/dev/null| %s>/dev/null' % (track.file, lame)
    print cmd
    #os.system(cmd)
