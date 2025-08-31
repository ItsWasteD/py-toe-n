from typing import Any, TYPE_CHECKING, Callable

import rpyc

if TYPE_CHECKING:
    from client import Client

class TicTacToeService(rpyc.Service):
    rooms: list[dict[str, Any]] = []
    clients: list[rpyc.Connection] = []

    def __init__(self) -> None:
        pass

    def on_connect(self, conn) -> None:
        print(f"Client connected. {conn}")
        self.clients.append(conn)

    def on_disconnect(self, conn) -> None:
        if conn in self.clients:
            self.clients.remove(conn)

    # GAME MANAGEMENT

    def exposed_check(self, index: int, client: "Client") -> bool:
        return False

    def exposed_get_gamestate(self) -> list:
        return ["","","",
                "","","",
                "","",""]
    
class Game():
    SYMBOLS = {
        "p1": 'X',
        "p2": 'O',
    }

    def __init__(self) -> None:
        import random
        self.gamestate: dict[str, Any] = {
            "field": ["","","","","","","","",""],
            "turn": "p1" if random.randint(0,1) > 0.5 else "p2"
        }

    def has_win(self) -> bool:
        winning_indices: list[list[int]] = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]

        field: list[str] = self.gamestate["field"]
        for indices in winning_indices:
            if field[indices[0]] == field[indices[1]] and field[indices[1]] == field[indices[2]]:
                return True
        
        return False

    def check(self, index: int) -> bool:
        val: str = self.gamestate["field"][index]

        if val != "":
            return False
        else:
            self.gamestate["field"][index] = Game.SYMBOLS[self.gamestate["turn"]]
            return True

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(TicTacToeService, port=18861)
    t.start()