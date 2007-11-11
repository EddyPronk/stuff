class Track:
    def __init__(self, album):
        self.album = album

    def __getattr__(self, name):
        return getattr(self.album, name)

class Album:
    def __init__(self):
        self.tracks = {}

    def track(self, track_number):
        if self.tracks.has_key(track_number):
            return self.tracks[track_number]
        else:
            self.tracks[track_number] = Track(track_number)
            return self.tracks[track_number]
