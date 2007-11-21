import unittest
import re
import string
import album
import lineage

class FileFaker:
    def __init__(self, string = None):
        self.lines = string

    def readlines(self):
        for line in self.lines.splitlines():
            yield line

    def write(self, string):
        print string

if __name__ == '__main__':
    import unittest
    class H(unittest.TestCase):
        def test_all_same_string_false(self):
            self.assertEqual(False, lineage.all_same(iter('aazaa')))

        def test_all_same_string_true(self):
            self.assertEqual(True, lineage.all_same(iter('aaaaa')))

        def test_all_same_list_False(self):
            self.assertEqual(False, lineage.all_same(['A','v','A','A']))


        def test_all_same_list_True(self):
            self.assertEqual(True, lineage.all_same(['A','A','A','A']))
        
        def test_all_same_raw_string_true(self):
            self.assertEqual(True, lineage.all_same('aaaaa'))


    class I(unittest.TestCase):
        def test_track(self):
            self.assertEqual([5,6], lineage.find_diffs( ['track%.2d.whatever' % n  for n in range(12) ]))

        def test_track(self):
            self.assertEqual([5,6], lineage.find_diffs( ['track%.2d.whatever' % n  for n in range(12) ]))

        def test_track(self):
            tracks = ["Track01.ape", "Track02.ape", "Track03.ape"]
            self.assertEqual(6, lineage.find_diffs(tracks))

        def test_track2(self):
            tracks = ["01. Reverence.ape", "02. She's My Baby.ape", "10. Take The Long Way Home.ape"]
            self.assertEqual(0, lineage.find_diffs(tracks))

class TestLineage(unittest.TestCase):

    def setUp(self):
        self.lineage = lineage.Lineage()
    
    def testDisk(self):
        disk = self.lineage.album.disk(1)

    def testTrack(self):
        line = '8. God Is A DJ'
        self.lineage.try_match(line)
        self.assertEqual(self.lineage.album.disk(1).track(8).title, 'God Is A Dj')

    def testTrackWithoutSpace(self):
        line = '8.God Is A DJ'
        self.lineage.try_match(line)
        self.assertEqual(self.lineage.album.disk(1).track(8).title, 'God Is A Dj')

    def testTrackWithoutSpace(self):
        self.lineage.try_match('CD2')
        self.lineage.try_match('08. God Is A DJ')
        self.lineage.try_match('1234567890abcdef0123456789012345 *CD2/Track07.flac')
        self.lineage.try_match('1234567890abcdef0123456789012345 *CD2/Track08.flac')
        self.lineage.process()
        #self.lineage.try_match('Track01.flac:1234567890abcdef0123456789012345')
        #self.lineage.try_match('Track02.flac:1234567890abcdef0123456789012345')
        #self.lineage.process()
        self.assertEqual(self.lineage.album.disk(2).track(8).title, 'God Is A DJ')
        self.assertEqual(self.lineage.album.disk(2).track(8).filename, 'Track08.flac')


    def testTrack(self):
        line = '08 God Is A DJ'
        self.assertEqual(self.lineage.try_match_test(line), ('08' , 'God Is A DJ'))
        self.lineage.try_match(line)
        self.assertEqual(self.lineage.album.disk(1).track(8).title, 'God Is A DJ')
        
    def testRe(self):
        self.lineage.try_match_test('Track01.flac:1234567890abcdef0123456789012345')
        self.lineage.try_match_test('Track10.flac:1234567890abcdef0123456789012345')
        print 'here'
        self.assertEqual(self.lineage.try_match_test('DISC 2'), ('DISC' , '2'))
        print 'here'
        self.assertEqual(self.lineage.try_match_test('Disc 2'), ('Disc' , '2'))
        #self.assertEqual(self.lineage.try_match_test('d3t01.flac'), ('3' , '01'))

    def testChecksum1(self):
        self.lineage.try_match('Track01.flac:1234567890abcdef0123456789012345')
        self.lineage.try_match('Track02.flac:1234567890abcdef0123456789012345')
        self.lineage.process()
        self.assertEqual(self.lineage.album.disk(1).track(1).filename, 'Track01.flac')
        self.assertEqual(self.lineage.album.disk(1).track(1).checksum, '1234567890abcdef0123456789012345')

    def testChecksum2(self):
        print 'testChecksum2'
        input = '''
1234567890abcdef0123456789012345 *Faithless2005-08-19_t07.flac
1234567890abcdef0123456789012345 *Faithless2005-08-19_t08.flac
        '''
        self.lineage.input_file = FileFaker(input)
        self.lineage.readlines()
        self.assertEqual(self.lineage.album.disk(1).track(8).filename, 'Faithless2005-08-19_t08.flac')
        self.assertEqual(self.lineage.album.disk(1).track(8).checksum, '1234567890abcdef0123456789012345')

    def testChecksum3(self):
        print 'testChecksum2'
        input = '''
1234567890abcdef0123456789012345 *01. Reverence.ape
1234567890abcdef0123456789012345 *02. She's My Baby.ape
1234567890abcdef0123456789012345 *10. Take The Long Way Home.ape
        '''
        self.lineage.input_file = FileFaker(input)
        self.lineage.readlines()
        self.assertEqual(self.lineage.album.disk(1).track(10).filename, '10. Take The Long Way Home.ape')

    def testFilenameWithDiskNumber(self):
        self.lineage.try_match('d1t01.flac')
        #self.assertEqual(self.lineage.disk.number, 1)
        self.lineage.try_match('d2t01.flac')
        #self.assertEqual(self.lineage.disk.number, 2)
        
        
    def testDetectNumber(self):
        self.lineage.try_match('1234567890abcdef0123456789012345 *Faithless2005-08-19_t01.flac')
        self.lineage.try_match('1234567890abcdef0123456789012345 *Faithless2005-08-19_t02.flac')
        self.lineage.try_match('1234567890abcdef0123456789012345 *Faithless2005-08-19_t07.flac')
        self.lineage.process()
        self.assertEqual(self.lineage.album.disk(1).track(7).filename, 'Faithless2005-08-19_t07.flac')

    def testMultiDisk(self):
        
        class FileFaker:
            def write(self, string):
                print string

        self.lineage.try_match('DISC 1')
        self.lineage.try_match('DISC 2')
        self.lineage.try_match('8. God Is A DJ')
        self.assertEqual(self.lineage.album.disk(2).track(8).title, 'God Is A DJ')
        file = FileFaker()
        self.lineage.write_cue_sheet(file)

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

        self.lineage.input_file = FileFaker(input)
        file = FileFaker()
        self.lineage.readlines()
        self.lineage.write_cue_sheet(file)


if __name__ == '__main__':
    unittest.main()

