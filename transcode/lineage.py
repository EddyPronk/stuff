import re
import string
import os
import album

def log(level, s):
    print s
    pass

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
        self.last_track_number = 0
        self.selectDisc('1')

        self.checksums = {}
        #self.add(('^d([0-9]+)t([0-9]+)',       lambda r : self.selectDisc(r.group(1))))
        self.add(('([^:]+):([0-9a-f]{32})', lambda r : self.insertChecksum(r.group(1), r.group(2))))
        self.add(('([0-9a-f]{32}) \*(.*)',  lambda r : self.insertChecksum(r.group(2), r.group(1))))
        self.add(('^([0-9]+)\.\s*(.*)',   lambda r : self.insertTitle(r.group(1), r.group(2))))
        self.add(('^([0-9]+) (.*)',   lambda r : self.insertTitle(r.group(1), r.group(2))))
#        self.add(('(DISC|Disc|cd|CD)\s*([0-9])',       lambda r : self.selectDisc(r.group(2))))


    def extract(self):
        album = Album()
        file = open("montreux.txt")
        for line in file.readlines():
            parse(line)
        album.do_print()

    def parseDisc(self, s, comment):
        res = re.search('(DISC|Disc|cd|CD)\s*([0-9])', s)
        if res is not None:
            disc_number = res.group(2)
            print '[disc #%s matches, %s]' % (disc_number, comment)
            self.selectDisc(disc_number)
        
    def read(self, filename):
        self.selectDisc('1')
        print 'read %s' % filename
        self.last_track_number = 0
        self.parseDisc(filename, 'matches filename') # bit hacky
        self.input_file = open(filename)
        self.readlines()

    def readlines(self):
        for line in self.input_file.readlines():
            line = line.replace('\r', '')
            line = line.replace('\n', '')
            log(3, line)
            self.try_match(line)
        self.process()

    def selectDisc(self, disc_number):
    
        self.disc = self.album.disc(string.atoi(disc_number))
        log(2, '[disc #%s]' % disc_number)

    def nextDisc(self):
        disc_number = self.disc.number + 1
        log(2, '[disc #%s]' % disc_number)
        self.disc = self.album.disc(disc_number)

    def insertTitle(self,number, title):
        track_number = string.atoi(number)
        if track_number > 100:
            log(1, '[IGNORE title #%s "%s"]' % (track_number, title))
            return

        #print 'tr %d < last %d' % (track_number, self.last_track_number)
        if (track_number < self.last_track_number):
            self.nextDisc()

        self.last_track_number = track_number

        track = self.disc.track(track_number)
        res = re.search('(.*)[0-9]{2}:[0-9]{2}$', title)
        if res is not None:
            print 'not none'
            title = res.group(1)
        title = title.rstrip()
        #title = track.title.replace(' / ', ', ')
        res = re.search('(.*)\.(flac|ape|shn)$', title)
        if res is not None:
            title = res.group(1)
        log(2, '[title #%s "%s"]' % (track_number, title))
        track.title = title

    def insertChecksum(self, path, checksum):
        # fix the directory seperator
        path = path.replace('\\', '/')

        log(2, '[checksum file=%s checksum=%s]' % (path, checksum))
        expr = '\.(flac|ape|shn)$'
        dir, filename = os.path.split(path)
        res = re.search(expr, path)
        if res is not None:
            self.parseDisc(dir, 'in %s' % path)
            
            # parse d1t3.ape
            #res = re.search('d([0-9]+)t([0-9]+)', filename)
            res = re.search('d([0-9]+)\s?t([0-9]+)', filename)
            if res is not None:
                self.selectDisc(res.group(1))
            else:
                print 'no match'
        

            # parse 1-2.ape
            res = re.search('^([0-9]+)-([0-9]+)', filename)
            if res is not None:
                pass
                self.selectDisc(res.group(1))

            #
            res = re.search('^cd([0-9]+)', filename)
            if res is not None:
                pass
                self.selectDisc(res.group(1))

            self.disc.checksums[filename] = checksum
        else:
            print '[ignoring %s]' % filename


    def write_cue_sheet(self):
        for disc in self.album.discs.values():
            cue_filename = os.path.join(disc.content_root, 'disc%d.cue' % disc.number)

            class FileFaker:
                def write(self, string):
                    print string

            if not os.path.exists(cue_filename):
                print 'writing cue file for disc #%i to %s' % (disc.number, cue_filename)
                file = open(cue_filename, 'w')
                self.write_cue_sheet_(file, disc)
            else:
                print 'writing cue file for disc #%i to %s (skipping, exists)' % (disc.number, cue_filename)

    def write_cue_sheet_(self, file, disc):
        #file = self.file
        file.write('PERFORMER ""\n')
        file.write('TITLE ""\n')
        file.write('YEAR ""\n')
        file.write('DISC "%d"\n' % disc.number)
        file.write('COMMENT "LAME 3.97 (--preset standard)"\n')
        file.write('\n')
        for track in disc.tracks.values():
            track.title = " ".join([ word.capitalize() for word in track.title.split() ])
            #file.write('TRACK %s AUDIO\n' % track.number)
            file.write('TRACK %s\n' % track.number)
            file.write('  TITLE "%s"\n' % track.title)
            #file.write('  FILE "%s" FLAC\n' % track.filename)
            file.write('  FILE "%s"\n' % track.filename)
            #file.write('  CHECKSUM "%s"\n' % track.checksum)

    def process(self):
        for disc in self.album.discs.values():
            log(2, '[DISC %d]' % disc.number)
            res = find_diffs(disc.checksums.keys())
            for filename, checksum in disc.checksums.iteritems():
                track_number = string.atoi(re.search('([0-9]+)', filename[res:]).group(1))

                #self.try_match(filename)
                track = disc.track(track_number)
                track.filename = filename
                track.checksum = checksum

                if track.title == '':
                    res2 = re.search('[0-9]+ - (.*).flac', filename)
                    if res2 is not None:
                        track.title = res2.group(1)
                
                log(2, '[processed %s %s]' % (track_number, track.filename))

    def add(self, entry):
        self.r.append(entry)

    def try_match(self, line):
        for t in self.r:
            expr,b = t
            res = re.search(expr, line)
            if res is not None:
                log(3, '[%s matches %s]' % (line, expr))
                b(res)
                break

    def try_match_test(self, line):
        for t in self.r:
            expr,b = t
            res = re.search(expr, line)
            if res is not None:
                log(3, '%s matches %s' % (line, expr))
                return res.groups()

