import os
import re
import glob
import string
import lineage

class Scanner:
    def glob(self, parent, pattern):
        txt = glob.glob("*") 
        newlist = []
        for l in txt:
            res = re.search(pattern, l)
            if res is not None and os.path.isfile(l):
                newlist.append(os.path.join(parent, l))

        return newlist

    def scan(self, dir):
        self.disc = None
        self.album_list = []
        self.traverse(dir)
	uniquedict = {}
	for i in self.album_list:
            uniquedict[i] = 0
        print
    
    def traverse(self, dir, parent = None):
        cwd = os.getcwd()
        os.chdir(dir)
        media_files = []
        list = glob.glob("*")
        for l in list:
            if os.path.isdir(l):
                res = re.search('(CD|Disc)\s*([0-9])', l)
                if res is not None:
                    self.disc = string.atoi(res.group(2))
                self.traverse(l, os.getcwd())
            else:
                expr = '\.(flac|ape)$'
                res = re.search(expr, l)
                if res is not None and os.path.isfile(l):
                    media_files.append(l)

        if len(media_files):
            print
            print 'media files for found in:'
            print os.getcwd()
            content_dir = os.getcwd()
            album_dir = os.getcwd()
            txt = self.glob(album_dir, '\.(txt|ffp|md5)$')
            if len(txt):
                print 'searching for meta data -- found!'
            else:
                print 'searching for meta data -- not found, trying parent dir'

            if self.disc is not None:
                print 'multi disc set, disk %s' % self.disc
                os.chdir(parent)
                extra_txt = self.glob(parent, '\.(txt|ffp|md5)$')

                if len(extra_txt):
                    print 'searching for meta data in parent because we have a multi disc set -- found!'
                    album_dir = os.getcwd()
                    txt.extend(extra_txt)
                else:
                    print 'searching for meta data -- not found!'

            if len(txt):
                print 'root %s' % album_dir
                print txt

            self.album_list.append(album_dir)

            print 'content in %s' % content_dir
            ding = lineage.Lineage()

            class FileFaker:
                def write(self, string):
                    #print string
                    pass

            file = FileFaker()
            for l in txt:
                print 'read meta data from %s' % l
                ding.read(l)

            cue_filename = os.path.join(content_dir, 'tracklist.cue')
            print 'writing cue file to %s' % cue_filename
            ding.write_cue_sheet(file)

        os.chdir(cwd)

s = Scanner()
#s.scan('/media/data')
s.scan('/media/data/[05.24.92]  Flanders Expo')
#s.scan('/media/data/Prince and the Revolution - Stockholm 1986')
#s.scan('/media/data/Parliament Funkadelic Unreleased SBD/')
#s.scan('/media/data/done/test') #Prince - Indigo2, London, 6 September 2007/')
