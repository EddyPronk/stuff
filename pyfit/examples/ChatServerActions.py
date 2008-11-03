from chat.ChatRoom import ChatRoom

class ChatServerActions(object):
    def __init__(self):
	self.chat = ChatRoom()
	self.userName = ""
	self.roomName = ""

    def user(self, userName):
        self.userName = userName

    def connect(self):
        self.chat.connectUser(self.userName)

    def room(self, roomName):
        self.roomName = roomName

    def new_room(self):
        self.chat.userCreatesRoom(self.userName, self.roomName)

    def enter_room(self):
        self.chat.userEntersRoom(self.userName, self.roomName)

    def occupant_count(self):
        return self.chat.occupants(self.roomName)

    def disconnect(self):
        return self.chat.disconnectUser(self.userName)
