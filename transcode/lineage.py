import re
import string
import os

class Track:
    def __init__(self, number):
        self.number = number
        self.checksum = ''
        pass

class Album:
    def __init__(self):
        self.tracks = {}

    def track(self, track_number):
        if self.tracks.has_key(track_number):
            return self.tracks[track_number]
        else:
            self.tracks[track_number] = Track(track_number)
            return self.tracks[track_number]

    def do_print(self):
        file = open('album.cue', 'w')
        file.write('PERFORMER ""\n')
        file.write('TITLE ""\n')
        file.write('YEAR ""\n')
        file.write('COMMENT "LAME 3.97 (--preset standard)"\n')
        file.write('\n')
        for track in self.tracks.values():
            #file.write('TRACK %s AUDIO\n' % track.number)
            file.write('TRACK %s\n' % track.number)
            file.write('  TITLE "%s"\n' % track.title)
            #file.write('  FILE "%s" FLAC\n' % track.filename)
            file.write('  FILE "%s"\n' % track.filename)
            file.write('  CHECKSUM "%s"\n' % track.checksum)

def extract():
    album = Album()
    file = open("montreux.txt")
    for line in file.readlines():
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
    album.do_print()

extract()
