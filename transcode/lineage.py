import re
import string
import os
import album

class Lineage:
    def __init__(self):
        self.r = []
        self.album = album.Album()
        self.disk = self.album.disk(1)

        self.checksums = []
        self.add(('^\s*([0-9]+).\s+(.*)',   lambda r : self.insertTitle(r.group(1), r.group(2))))
        self.add(('([^:]+):([0-9a-f]+)', lambda r : self.insertChecksum(r.group(1), r.group(2))))
        self.add(('([0-9a-f]+) \*(.*)',  lambda r : self.insertChecksum(r.group(2), r.group(1))))
        self.add(('^DISC ([0-9])',       lambda r : self.insertAlbum(r.group(1))))

    def extract(self):
        album = Album()
        file = open("montreux.txt")
        for line in file.readlines():
            parse(line)
        album.do_print()

    def readlines(self):
        for line in self.input_file.readlines():
            print line
            self.try_match(line)

    def insertAlbum(self, disk_number):
        self.disk = self.album.disk(string.atoi(disk_number))

    def insertTitle(self,number, title):
        track_number = string.atoi(number)
        track = self.disk.track(track_number)
        track.title = " ".join([ word.capitalize() for word in title.split() ])
        track.title = track.title.replace(' / ', ', ')
        print '%s-%s' % (track_number, track.title)

    def insertChecksum(self,filename, checksum):
        self.checksums.append((filename, checksum))

    def write_cue_sheet(self):
        file = self.file
        file.write('PERFORMER ""\n')
        file.write('TITLE ""\n')
        file.write('YEAR ""\n')
        file.write('COMMENT "LAME 3.97 (--preset standard)"\n')
        file.write('\n')
        for track in self.album.disk(1).tracks.values():
            #file.write('TRACK %s AUDIO\n' % track.number)
            file.write('TRACK %s\n' % track.number)
            file.write('  TITLE "%s"\n' % track.title)
            #file.write('  FILE "%s" FLAC\n' % track.filename)
            #file.write('  FILE "%s"\n' % track.filename)
            #file.write('  CHECKSUM "%s"\n' % track.checksum)

    def find_track_number(self):
        i = 0
        res = 0
        while res == 0:
            c = self.checksums[0][0][i]
            for s in self.checksums:
                if c != s[0][i]:
                    res = i
                    break
            i += 1
        for s in self.checksums:
            track_number = string.atoi(re.search('([0-9]+)', s[0][res:]).group(1))
            track = self.album.disk(1).track(track_number)
            track.filename = s[0]
            track.checksum = s[1]
            track = self.album.disk(1).track(track_number)

    def add(self, entry):
        self.r.append(entry)

    def try_match(self, line):
        for t in self.r:
            expr,b = t
            res = re.search(expr, line)
            if res is not None:
                b(res)
                break

