import unittest
import re
import string
import album

class Lineage:
    def __init__(self):
        self.r = []
        self.album = album.Album()
        self.checksums = []
        self.add(('^([0-9]+).\s+(.*)',   lambda r : self.insertTitle(r.group(1), r.group(2))))
        self.add(('([^:]+):([0-9a-f]+)', lambda r : self.insertChecksum(r.group(1), r.group(2))))
        self.add(('([0-9a-f]+) \*(.*)',  lambda r : self.insertChecksum(r.group(2), r.group(1))))

    def extract(self):
        album = Album()
        file = open("montreux.txt")
        for line in file.readlines():
            parse(line)
        album.do_print()

    def insertTitle(self,number, title):
        print 'insertTitle called with %s %s' % (number, title)

    def insertChecksum(self,filename, checksum):
        print 'insertChecksum filename=%s checksum=%s' % (filename, checksum)
        self.checksums.append((filename, checksum))

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
            track_number = re.search('([0-9]+)', s[0][res:]).group(1)
            track = self.album.track(track_number)
            track.filename = s[0]
            track.checksum = s[1]
            print "%s %s %s" % (re.search('([0-9]+)', s[0][res:]).group(1), s[0], s[1])

    def add(self, entry):
        self.r.append(entry)

    def try_match(self, line):
        for t in self.r:
            expr,b = t
            res = re.search(expr, line)
            if res is not None:
                b(res)
                break

    def parse(self, line):
        line = line.replace('\r', '')
        line = line.replace('\n', '')
        expr = r'^([0-9]+).\s+(.*)'
        res = re.search(expr, line)
        if res is not None:
            track_number = string.atoi(res.group(1))
            track = album.track(track_number)
            track.title = " ".join([ word.capitalize() for word in res.group(2).split() ])
            track.title = track.title.replace(' / ', ', ')
        expr = r'([^:]+):([0-9a-f]+)'
        res = re.search(expr, line)
        if res is not None:
            filename = res.group(1)
            checksum = res.group(2)
            res = re.search(r'([0-9]+)[-](.*).flac', filename)
            if res is not None:
                track_number = string.atoi(res.group(1))
                track = album.track(track_number)
                track.filename = filename
                track.checksum = checksum
            res = re.search(r'Track([0-9]+).flac', filename)
            if res is not None:
                track_number = string.atoi(res.group(1))
                track = album.track(track_number)
                track.filename = filename
                track.checksum = checksum
            # 0ed7b426c32f30ffc6235ec09783448e *Prince2007-07-16_t15.flac

        expr = r'([0-9a-f]+) \*(.*)'
        res = re.search(expr, line)
        if res is not None:
            filename = res.group(2)
            checksum = res.group(1)
            print res.group(2)
            res = re.search(r'.*_t([0-9]+).flac', filename)
            if res is not None:
                track_number = string.atoi(res.group(1))
                print track_number
                track = album.track(track_number)
                track.filename = filename
                track.checksum = checksum

class TestLineage(unittest.TestCase):

    def setUp(self):
        self.lineage = Lineage()
    
    def testTrack(self):
        line = '8. God Is A DJ'
        self.lineage.try_match(line)

        #self.assertEqual(number, 8)
        #self.assertEqual(title, 'God Is A DJ')

    def testChecksum1(self):
        line = 'Track01.flac:9da70b0b61fc39669b9de113a5aaacbe'
        self.lineage.try_match(line)

    def testChecksum2(self):
        line = '6dedb8e3a86bb97a137df8e21b31868f *Prince2007-07-16_t01.flac'
        self.lineage.try_match(line)

    def testDetectNumber(self):
        self.lineage.try_match('6dedb8e3a86bb97a137df8e21b31868f *Prince2007-07-16_t01.flac')
        self.lineage.try_match('6dedb8e3a86bb97a137df8e21b31868f *Prince2007-07-16_t02.flac')
        self.lineage.try_match('6dedb8e3a86bb97a137df8e21b31868f *Prince2007-07-16_t10.flac')
        self.lineage.find_track_number()
        
if __name__ == '__main__':
    unittest.main()

