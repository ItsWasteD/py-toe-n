import rpyc
import uuid

class TicTacToeService(rpyc.Service):
    rooms = []

    def __init__(self):
        self.a = 0

    def on_connect(self, conn):
        print("Client connected.")
        pass

    def on_disconnect(self, conn):
        print("Client disconnected.")
        pass

    def exposed_create_room(self):
        room_id = uuid.uuid4()
        TicTacToeService.rooms.append(room_id)

        return room_id
    
    def exposed_show_rooms(self):
        return TicTacToeService.rooms
    
    def exposed_join_room(self, room_id: str):
        pass


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(TicTacToeService, port=18861)
    t.start()