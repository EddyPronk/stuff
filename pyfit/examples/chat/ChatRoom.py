from User import User
from Room import Room

class ChatRoom(object):
    def __init__(self):
        self.users = {}
        self.rooms = {}

    def connectUser(self, userName):
        if self.users.has_key(userName):
            return False
        self.users[userName] = User(userName)
        return True

    def userCreatesRoom(self, userName, roomName):
        user = self.users[userName]
        self.createRoom(roomName, user)

    def createRoom(self, roomName, user):
        if self.rooms.has_key(roomName):
            raise Exception("Duplicate room name: " + roomName)
        self.rooms[roomName] = Room(roomName, user, self)

    def userEntersRoom(self, userName, roomName):
        user = self.users[userName]
        room = self.rooms[roomName]
        #room.add(user);

    def occupants(self, roomName):
        room = self.rooms[roomName]
        return room.occupantCount()
