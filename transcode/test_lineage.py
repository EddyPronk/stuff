import unittest
import re
import string
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

class TestLineage(unittest.TestCase):

    def setUp(self):
        self.lineage = Lineage()
    
    def testDisk(self):
        disk = self.lineage.album.disk(1)

    def testTrack(self):
        line = '8. God Is A DJ'
        self.lineage.try_match(line)
        self.assertEqual(self.lineage.album.disk(1).track(8).title, 'God Is A Dj')
        
    def testChecksum1(self):
        self.lineage.try_match('Track01.flac:1234567890abcdef0123456789012345')
        self.lineage.try_match('Track02.flac:1234567890abcdef0123456789012345')
        self.lineage.find_track_number()
        self.assertEqual(self.lineage.album.disk(1).track(1).filename, 'Track01.flac')
        self.assertEqual(self.lineage.album.disk(1).track(1).checksum, '1234567890abcdef0123456789012345')

    def testChecksum2(self):
        self.lineage.try_match('1234567890abcdef0123456789012345 *Faithless2005-08-19_t07.flac')
        self.lineage.try_match('1234567890abcdef0123456789012345 *Faithless2005-08-19_t08.flac')
        track = self.lineage.album.disk(1).track(8)
        self.lineage.find_track_number()
        self.assertEqual(self.lineage.album.disk(1).track(8).filename, 'Faithless2005-08-19_t08.flac')
        self.assertEqual(self.lineage.album.disk(1).track(8).checksum, '1234567890abcdef0123456789012345')

    def testDetectNumber(self):
        self.lineage.try_match('1234567890abcdef0123456789012345 *Faithless2005-08-19_t01.flac')
        self.lineage.try_match('1234567890abcdef0123456789012345 *Faithless2005-08-19_t02.flac')
        self.lineage.try_match('1234567890abcdef0123456789012345 *Faithless2005-08-19_t07.flac')
        self.lineage.find_track_number()
        track = self.lineage.album.disk(1).track(7)

    def testMultiDisk(self):
        
        class FileFaker:
            def write(self, string):
                print string

        self.lineage.try_match('DISC 1')
        self.lineage.try_match('DISC 2')
        self.lineage.try_match('8. God Is A DJ')
        self.assertEqual(self.lineage.album.disk(2).track(8).title, 'God Is A Dj')
        self.lineage.file = FileFaker()
        self.lineage.write_cue_sheet()

    def testExample(self):
        input = '''
            01. Faithless - Reverence
            02. Faithless - She's My Baby
            03. Faithless - Take The Long Way Home
            04. Faithless - Insomnia
            05. Faithless - Bring The Family Back
            06. Faithless - Salva Mea
            07. Faithless - Dirty Old Man
            08. Faithless - God Is A DJ
        '''

        class FileFaker:
            def __init__(self, string = None):
                self.lines = string

            def readlines(self):
                for line in self.lines.splitlines():
                    yield line

            def write(self, string):
                print string

        self.lineage.input_file = FileFaker(input)
        self.lineage.file = FileFaker()
        self.lineage.readlines()
        self.lineage.write_cue_sheet()


if __name__ == '__main__':
    unittest.main()

