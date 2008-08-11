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

import sys, os, os.path
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst
import time
import threading
#import events
import gobject
import ID3

import string
import cuesheet
import glob
import re

gobject.threads_init()

class Transcode(gst.Bin):
	
    def __init__(self, input_filename, output_filename):
        gst.Bin.__init__(self)

        self.done = threading.Event()
        self.player = gst.Pipeline("player")
        source = gst.element_factory_make('filesrc', 'file-source')
        self.player.add(source)
        self.decoder = gst.element_factory_make('decodebin', 'decoder')
        self.decoder.connect("pad-added", self.demuxer_callback)
        self.player.add(self.decoder)
        self.encoder = gst.element_factory_make('lame', 'mp3-encoder')
        self.encoder.set_property('preset', 1001) # standard
        #self.encoder.set_property('preset', 'standard') # standard
        # bug in gst, file size mp3 is smaller then expected
        #self.encoder.set_property('preset', 1002) # to try
        self.player.add(self.encoder)
        self.file = gst.element_factory_make('filesink', 'lame')
        self.file.set_property('location', output_filename)
        
        self.player.add(self.file)
        gst.element_link_many(source, self.decoder) #, encoder, file)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

        self.player.get_by_name("file-source").set_property('location', input_filename)
        self.player.set_state(gst.STATE_PLAYING)
	self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def on_message(self, bus, message):
        t = message.type
        #print 'message type %s' % t
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.mainloop.quit()
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug

    def demuxer_callback(self, demuxer, pad):
        parent = pad.get_parent_element()
        #print 'pad added for %s' % parent.get_name()
        gst.element_link_many(self.decoder, self.encoder, self.file)

def chdir(dir):
    #print 'chdir %s' % dir
    os.chdir(dir)

class Scanner:
    def __init__(self, object):
        self.object = object

    def glob(self, parent, pattern):
        txt = glob.glob("*") 
        newlist = []
        for l in txt:
            res = re.search(pattern, l)
            if res is not None and os.path.isfile(l):
                newlist.append(os.path.join(parent, l))

        return newlist

    def scan(self, dir):
        self.traverse(dir)
    
    def traverse(self, dir, parent = None):
        cwd = os.getcwd()
        chdir(dir)
        self.object.on_enter_dir(dir, cwd)
        list = glob.glob("*")
        for l in list:
            if os.path.isdir(l):
                self.traverse(l, os.getcwd())
            else:
                self.object.on_file(l)

        self.object.on_leaving_dir(os.getcwd(), cwd)
        chdir(cwd)

class DirectoryVisitor:
    def glob(self, parent, pattern):
        txt = glob.glob("*") 
        newlist = []
        for l in txt:
            res = re.search(pattern, l)
            if res is not None and os.path.isfile(l):
                newlist.append(os.path.join(parent, l))
        return newlist

    def on_enter_dir(self, file, a): pass
    def on_leaving_dir(self, file, a): pass
    def on_file(self, file): pass

def transcode(cue_sheet):
    dir, filename = os.path.split(cue_sheet)
    os.chdir(dir)
    file = open(filename)
    input = file.read()
    tokens = cuesheet.parse('sheet', input)

    state = 'header'

    track = None

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

    output_root_dir = '/media/data/transcoded'
    album_dir = '%s - %s (Disc %s)' % (album.performer, album.title, album.disc)
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
        if not os.path.exists(filename):
            #mplayer -vo null -vc dummy -af resample=44100 fz-1980-05-24-d1t10.shn -ao pcm:file=/dev/stdout -quiet | lame - foo.mp3            
            lame = 'lame - "%s" --quiet --preset standard ' % filename + ' '.join(opt.str)

            root, ext = os.path.splitext(track.file)
            if(ext == '.flac'):
                cmd = 'flac --decode --silent --stdout "%s" | %s' % (track.file, lame)
                print cmd
                os.system(cmd)
            elif(ext == '.ape'):
                cmd = 'mac "%s" /dev/stdout -d 2>/dev/null| %s>/dev/null' % (track.file, lame)
                os.system(cmd)
            elif(ext == '.shn'):
                # works, but failed for one track. Now using gstreamer
                #cmd = 'mplayer -vo null -vc dummy -af resample=44100 "%s" -ao pcm:file=/dev/stdout -quiet | %s' % (track.file, lame)
                Transcode(track.file, filename)

                if not os.path.exists(filename):
                    print "mp3 file not found, can't add id3 tags"
                    return

                id3info = ID3.ID3(filename)
                id3info["TITLE"] = track.title
                id3info["ARTIST"] = track.performer
                id3info["ALBUM"] = track.album.title
                id3info["YEAR"] = track.year
                #id3info["COMMENT"] = track.comment
                id3info["TRACKNUMBER"] = track.number
                id3info.write()
            else:
                print "dodgy %s" % track.file

        else:
            print "%s exists" % filename
        

class CueSheetVisitor(DirectoryVisitor):
    def on_enter_dir(self, dir, a):
        sheets = self.glob(os.getcwd(), '\.(cue)$')
        for s in sheets:
            transcode(s)

class options:
    def __init__(self):
        self.str = []
        
    def option(self, key, value):
        self.str.append('%s "%s"' % (key, value))

class Track:
    def __init__(self, album):
        self.album = album

    def __getattr__(self, name):
        return getattr(self.album, name)

class Album:
    def __init__(self):
        self.tracks = {}


f = CueSheetVisitor()
s = Scanner(f)

#s.scan('/home/epronk/zappa')
s.scan('/home/epronk/ttd')
#s.scan('/home/epronk/transcode-testing/fz1980-05-24.shnf')
#s.scan('/home/epronk/4dafunk')
