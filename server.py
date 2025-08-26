from typing import Any

import rpyc
import uuid

class TicTacToeService(rpyc.Service):
    rooms: list[dict[str, Any]] = []

    def __init__(self) -> None:
        pass

    def on_connect(self, conn) -> None:
        print("Client connected.")

    def on_disconnect(self, conn) -> None:
        print("Client disconnected.")

    def exposed_create_room(self, client_id: uuid.UUID) -> uuid.UUID:
        room_id: uuid.UUID = uuid.uuid4()

        room: dict[str, Any] = {
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
                room["opponent"] = client_id
                
                return True
            
        return False

    def exposed_get_gamestate(self) -> list:
        return ["","","",
                "","","",
                "","",""]

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(TicTacToeService, port=18861)
    t.start()