import rpyc
import uuid

class TicTacToeService(rpyc.Service):
    rooms: list[dict] = []

    def __init__(self):
        pass

    def on_connect(self, conn) -> None:
        print("Client connected.")

    def on_disconnect(self, conn) -> None:
        print("Client disconnected.")

    def exposed_create_room(self, client_id: uuid.UUID) -> uuid.UUID:
        room_id = uuid.uuid4()

        room = {
            "created_by": client_id,
            "room_id": room_id
        }

        TicTacToeService.rooms.append(room)

        print(f"Room '{room_id}' created by '{client_id}'")

        return room_id
    
    def exposed_get_rooms(self) -> list[dict]:
        return TicTacToeService.rooms
    
    def exposed_join_room(self, room_id: uuid.UUID, client_id: uuid.UUID) -> bool:
        for room in TicTacToeService.rooms:
            if room["room_id"] == room_id:
                room["oponent"] = client_id
                
                return True
            
        return False



if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(TicTacToeService, port=18861)
    t.start()