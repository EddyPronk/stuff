class Room(object):
    def __init__(self, roomName, owner, chat):
        self.name = roomName
        self.owner = owner
        self.chat = chat

    def occupantCount(self):
        return 0 # users.size()
