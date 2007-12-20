class Track:
    def __init__(self, track_number, album = None):
        self.number = track_number
        self.album = album

    def __getattr__(self, name):
        if self.album is None:
            return ''
        else:
            return getattr(self.album, name)

class Disc:
    def __init__(self, disc_number):
        self.tracks = {}
        self.checksums = {}
        self.number = disc_number
        self.content_root = ''

    def track(self, track_number):
        if self.tracks.has_key(track_number):
            return self.tracks[track_number]
        else:
            self.tracks[track_number] = Track(track_number)
            return self.tracks[track_number]

class Album:
    def __init__(self):
        self.discs = {}
        self.disc(1)

    def disc(self, disc_number):
        if self.discs.has_key(disc_number):
            disc = self.discs[disc_number]
        else:
            self.discs[disc_number] = Disc(disc_number)
            disc = self.discs[disc_number]
            disc.number = disc_number
            disc.content_root = self.discs[1].content_root
        return disc
