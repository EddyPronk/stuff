import re
import string
import os
import album

def all_same(l):
    first_item = iter(l).next()
    for cur_item in l:
        if cur_item != first_item:
            return False
    return True

def find_diffs(data):
    for item_num, items in enumerate(zip(*data)):
        if not all_same(items):
            return item_num

class Lineage:
    def __init__(self):
        self.r = []
        self.album = album.Album()
        self.disk = self.album.disk(1)

        self.checksums = []
        self.add(('([^:]+):([0-9a-f]{32})', lambda r : self.insertChecksum(r.group(1), r.group(2))))
        self.add(('([0-9a-f]{32}) \*(.*)',  lambda r : self.insertChecksum(r.group(2), r.group(1))))
        self.add(('([0-9]+)\.\s*(.*)',   lambda r : self.insertTitle(r.group(1), r.group(2))))
        self.add(('^([0-9]+) (.*)',   lambda r : self.insertTitle(r.group(1), r.group(2))))
        self.add(('(DISC|cd|CD)\s*([0-9])',       lambda r : self.insertAlbum(r.group(2))))

    def extract(self):
        album = Album()
        file = open("montreux.txt")
        for line in file.readlines():
            parse(line)
        album.do_print()

    def read(self, filename):
        self.try_match(filename) # bit hacky
        self.input_file = open(filename)
        self.readlines()

    def readlines(self):
        for line in self.input_file.readlines():
            line = line.replace('\r', '')
            line = line.replace('\n', '')
            print line
            self.try_match(line)
        self.process()

    def insertAlbum(self, disk_number):
        self.disk = self.album.disk(string.atoi(disk_number))
        print '[disk #%s]' % disk_number

    def insertTitle(self,number, title):
        track_number = string.atoi(number)
        print '[track #%s "%s"]' % (track_number, title)
        track = self.disk.track(track_number)
        #track.title = " ".join([ word.capitalize() for word in title.split() ])
        track.title = title
        track.title = track.title.replace(' / ', ', ')

    def insertChecksum(self,filename, checksum):
        print '[checksum file=%s checksum=%s]' % (filename, checksum)
        expr = '\.(flac|ape)$'
        res = re.search(expr, filename)
        if res is not None:
            dir, filename = os.path.split(filename)
            print dir
            self.try_match(dir)
            self.disk.checksums.append((filename, checksum))
        else:
            print '[ignoring %s]' % filename


    def write_cue_sheet(self, file):
        for disk in self.album.disks.values():
            self.write_cue_sheet_(file, disk)

    def write_cue_sheet_(self, file, disk):
        #self.file = open(filename, 'w')
        #file = self.file
        file.write('PERFORMER ""\n')
        file.write('TITLE ""\n')
        file.write('YEAR ""\n')
        file.write('DISC "%d"\n' % disk.number)
        file.write('COMMENT "LAME 3.97 (--preset standard)"\n')
        file.write('\n')
        for track in disk.tracks.values():
            #file.write('TRACK %s AUDIO\n' % track.number)
            file.write('TRACK %s\n' % track.number)
            file.write('  TITLE "%s"\n' % track.title)
            #file.write('  FILE "%s" FLAC\n' % track.filename)
            file.write('  FILE "%s"\n' % track.filename)
            #file.write('  CHECKSUM "%s"\n' % track.checksum)

    def process(self):
        for disk in self.album.disks.values():
            checksums = disk.checksums
            filenames = []
            for c in checksums:
                filenames.append(c[0])
        
            res = find_diffs(filenames)

            print '[processing DISK %d]' % (disk.number)

            for s in checksums:
                track_number = string.atoi(re.search('([0-9]+)', s[0][res:]).group(1))
                track = disk.track(track_number)
                track.filename = s[0]
                track.checksum = s[1]
                print '[processed %s %s]' % (track_number, track.filename)

    def add(self, entry):
        self.r.append(entry)

    def try_match(self, line):
        for t in self.r:
            expr,b = t
            res = re.search(expr, line)
            if res is not None:
                b(res)
                break

    def try_match_test(self, line):
        for t in self.r:
            expr,b = t
            res = re.search(expr, line)
            if res is not None:
                return res.groups()

