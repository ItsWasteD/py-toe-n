from typing import Any, TYPE_CHECKING, Callable

import rpyc

if TYPE_CHECKING:
    from client import Client

class TicTacToeService(rpyc.Service):
    clients: list[rpyc.Connection] = []
    callbacks: list[Callable] = []
    game: "Game" = None

    def __init__(self) -> None:
        if TicTacToeService.game is None:
            TicTacToeService.game = Game()

    def on_connect(self, conn) -> None:
        if len(TicTacToeService.clients) >= 2:
            return

        TicTacToeService.clients.append(conn)
        print(f"Client {len(TicTacToeService.clients)} connected. {conn}")

    def on_disconnect(self, conn) -> None:
        if conn in TicTacToeService.clients:
            TicTacToeService.clients.remove(conn)
            print(f"Client disconnected. {conn}")

    def exposed_ready(self, update_cb: Callable) -> None:
        TicTacToeService.callbacks.append(update_cb)

        if len(TicTacToeService.callbacks) == 2:
            for idx,update_cb in enumerate(TicTacToeService.callbacks):
                update_cb(TicTacToeService.game.gamestate, ["p1","p2"][idx])

            TicTacToeService.game.gamestate["state"] = "playing"

    # GAME MANAGEMENT

    def exposed_check(self, index: int, player_nr: str) -> bool:      
        field = TicTacToeService.game.gamestate["field"][index]

        result = TicTacToeService.game.check(index, player_nr)

        if TicTacToeService.game.has_win():
            TicTacToeService.game.gamestate["state"] = "finished"
            TicTacToeService.game.gamestate["winner"] = player_nr

        for update_cb in TicTacToeService.callbacks:
            update_cb(TicTacToeService.game.gamestate)

        return result
    
class Game():
    SYMBOLS = {
        "p1": 'X',
        "p2": 'O',
    }

    def __init__(self) -> None:
        import random
        self.gamestate: dict[str, Any] = {
            "state": "waiting",
            "field": ["","","","","","","","",""],
            "turn": "p1" if random.randint(0,1) > 0.5 else "p2"
        }

    def has_win(self) -> bool:
        winning_indices: list[list[int]] = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]

        field: list[str] = self.gamestate["field"]
        for indices in winning_indices:
            if field[indices[0]] != "" and field[indices[0]] == field[indices[1]] and field[indices[1]] == field[indices[2]]:
                return True
        
        return False

    def check(self, index: int, player_id: str) -> bool:
        val: str = self.gamestate["field"][index]

        if val != "" or player_id != self.gamestate["turn"]:
            return False
        else:
            self.gamestate["field"][index] = Game.SYMBOLS[player_id]
            self.gamestate["turn"] = "p2" if player_id == "p1" else "p1"
            return True

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(TicTacToeService, port=18861)
    t.start()