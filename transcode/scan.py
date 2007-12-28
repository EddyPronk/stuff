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

options.overwrite = True

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

    def make_lineage(self):
        l = lineage.Lineage(options)
        l.on_cue_sheet_written = self.callback
        return l

    def __init__(self, callback):
        self.callback = callback
        self.lineage = self.make_lineage()
        self.album_dir = ''
        self.disc_number = 1
        self.parent_done = False # metadata in parent has not been read

    def on_enter_dir(self, dir, parent = None):
        res = re.search('(CD|cd|Disc)\s*([0-9])', dir)
        if res is not None:
            self.disc_number = string.atoi(res.group(2))
        else:
            self.disc_number = 1
        self.media_files = []

    def on_leaving_dir(self, dir, parent = None):
        if len(self.media_files):
            content_dir = os.getcwd()
            self.lineage.album.disc(self.disc_number).content_root = content_dir
            txt = self.glob(content_dir, '\.(txt|ffp|md5)$')
            if len(txt):
                print 'searching for meta data -- found!'
            else:
                print 'searching for meta data -- not found, trying parent dir'

            content = glob.glob("*.flac") 

            if not self.parent_done:
                chdir(parent)
                extra_txt = self.glob(parent, '\.(txt|ffp|md5)$')

                if len(extra_txt):
                    print 'searching for meta data in parent because we have a multi disc set -- found!'
                    album_dir = os.getcwd()
                    txt.extend(extra_txt)
                else:
                    print 'searching for meta data -- not found!'
                    album_dir = dir
                self.parent_done = True

                if len(txt):
                    self.album_dir = album_dir
                    content_root = os.getcwd()

                class FileFaker:
                    def write(self, string):
                        pass

                self.lineage.parse(txt, content)

            else:
                print 'already have info from parent'

        print 'leaving %s' % dir

        if dir == self.album_dir:
            print 'write_cue_sheet in %s' % os.getcwd()
            self.lineage.write_cue_sheets()
            self.lineage = self.make_lineage()
            self.album_dir = ''
            self.parent_done = False
        self.media_files = []

    def on_file(self, file):
        expr = '\.(flac|ape|shn)$'
        res = re.search(expr, file)
        if res is not None and os.path.isfile(file):
            self.media_files.append(file)
            #os.system('rm %s' % file)

    def glob(self, parent, pattern):
        txt = glob.glob("*") 
        newlist = []
        for l in txt:
            res = re.search(pattern, l)
            if res is not None and os.path.isfile(l):
                newlist.append(os.path.join(parent, l))
        return newlist

#s.scan('/media/data')
#s.scan('/media/data/done')
#s.scan('/media/data/done/Prince - Indigo2, London, 6 September 2007')
#s.scan('/home/epronk/4dafunk/4DaFunk/4DaFunk Open Sessions')
#s.scan('/home/epronk/4dafunk')
#s.scan('/home/epronk/zappa')
#s.scan('/home/epronk/pol')

class RegressionTester:
    def __init__(self):
        self.tests = 0
        self.failed = 0
        
    def compare(self, file):
        self.tests += 1
        expected_file = file + '.expected'
        #os.system('cp "%s" "%s"' % (file, expected_file))
        cmd = 'diff "%s" "%s"' % (file, expected_file)
        res = os.system(cmd)
        if(res != 0):
            self.failed += 1
        else:
            os.remove(file)

    def report(self):
        print 'ran %i tests, failed %i' % (self.tests, self.failed)
        

tester = RegressionTester()
f = ScanGuy(callback=tester.compare)
s = Scanner(f)
s.scan('/home/epronk/src/transcode-testing')
#s.scan('/home/epronk/src/transcode-testing/amy')
#s.scan('/home/epronk/src/transcode-testing/1982-07-04 - Rock Werchter [FM]')
#s.scan('/home/epronk/src/transcode-testing/4DaFunk/4DaFunk Open Sessions')

#s.scan('/media/data/done/Rock Over Germany/')
#s.scan('/media/data/test')
#s.scan('/media/data/[05.24.92]  Flanders Expo')
#s.scan('/media/data/Prince and the Revolution - Stockholm 1986')
#s.scan('/media/data/Parliament Funkadelic Unreleased SBD/')
#s.scan('/media/data/done/test') #Prince - Indigo2, London, 6 September 2007/')
tester.report()
