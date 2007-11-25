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

import os
import re
import glob
import string
import lineage
from optparse import OptionParser

parser = OptionParser()

(options, args) = parser.parse_args()


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

class FlayGuy:
    def on_dir(self, dir):
        print 'entering %s' % dir
    def on_leaving_dir(self, file):
        print 'leaving %s' % file
    def on_file(self, file):
        print 'file %s' % file

class ScanGuy:
    def __init__(self):
        self.lineage = lineage.Lineage()
        self.album_dir = ''
        self.disc_number = 1
        self.parent_done = False # metadata in parent has not been read

    def on_enter_dir(self, dir, parent = None):
        print 'entering %s' % dir
        res = re.search('(CD|cd|Disc)\s*([0-9])', dir)
        if res is not None:
            self.disc_number = string.atoi(res.group(2))
        self.media_files = []

    def on_leaving_dir(self, dir, parent = None):
        if len(self.media_files):
            content_dir = os.getcwd()
            self.lineage.album.disc(self.disc_number).content_root = content_dir
            print 'media files for disc %i in %s' % (self.disc_number, content_dir)
            txt = self.glob(content_dir, '\.(txt|ffp|md5)$')
            if len(txt):
                print 'searching for meta data -- found!'
            else:
                print 'searching for meta data -- not found, trying parent dir'

            if not self.parent_done:
                chdir(parent)
                extra_txt = self.glob(parent, '\.(txt|ffp|md5)$')

                if len(extra_txt):
                    print 'searching for meta data in parent because we have a multi disc set -- found!'
                    album_dir = os.getcwd()
                    txt.extend(extra_txt)
                else:
                    print 'searching for meta data -- not found!'
                self.parent_done = True

                self.album_dir = album_dir
                if len(txt):
                    print 'root %s' % album_dir
                    content_root = os.getcwd()

                class FileFaker:
                    def write(self, string):
                        #print string
                        pass

                file = FileFaker()
                for l in txt:
                    #log(2, 'read meta data from %s' % l)
                    self.lineage.read(l)
            else:
                print 'already have info from parent'

        print 'leaving %s' % dir

        if dir == self.album_dir:
            print 'RESET'
            self.lineage.write_cue_sheet()
            self.lineage = lineage.Lineage()
            self.album_dir = ''
            self.parent_done = False
        self.media_files = []

    def on_file(self, file):
        expr = '\.(flac|ape)$'
        res = re.search(expr, file)
        if res is not None and os.path.isfile(file):
            self.media_files.append(file)

    def glob(self, parent, pattern):
        txt = glob.glob("*") 
        newlist = []
        for l in txt:
            res = re.search(pattern, l)
            if res is not None and os.path.isfile(l):
                newlist.append(os.path.join(parent, l))
        return newlist

f = ScanGuy()
s = Scanner(f)
#s.scan('/media/data')
#s.scan('/media/data/done')
#s.scan('/media/data/done/Prince - Indigo2, London, 6 September 2007')
#s.scan('/home/epronk/4dafunk/4DaFunk/4DaFunk Open Sessions')
s.scan('/home/epronk/4dafunk')
#s.scan('/media/data/done/Rock Over Germany/')
#s.scan('/media/data/test')
#s.scan('/media/data/[05.24.92]  Flanders Expo')
#s.scan('/media/data/Prince and the Revolution - Stockholm 1986')
#s.scan('/media/data/Parliament Funkadelic Unreleased SBD/')
#s.scan('/media/data/done/test') #Prince - Indigo2, London, 6 September 2007/')
