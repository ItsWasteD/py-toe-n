import tkinter as tk
from tkinter import ttk, font

from typing import Any

import rpyc
import uuid

title_font: font.Font = None

c: rpyc.Connection = rpyc.connect("localhost", 18861)

class ClientService(rpyc.Service):
    def __init__(self, client: "Client"):
        self.client: "Client" = client

    def exposed_update_rooms(self):
        print("Client: Updating roomlist")
        self.client.after(0,self.client.frames["RoomList"].refresh)

class Client(tk.Tk):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.title("Py-toe-n")

        global title_font
        title_font = font.Font(family="Helvetica", size=20, weight="bold")

        container: ttk.Frame = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames: dict[str, ttk.Frame] = {}  
        for F in (MenuPage, RoomList, WaitingRoom, ShowGame):
            page_name: str = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MenuPage")

    def show_frame(self, name: str) -> None:
        frame: ttk.Frame = self.frames[name]

        if hasattr(frame, "refresh"):
            frame.refresh()

        frame.tkraise()

    def create_room(self) -> uuid.UUID:
        room_id: uuid.UUID = c.root.create_room(self)
        self.show_frame("WaitingRoom")

        return room_id

    def join_room(self, room_id: uuid.UUID) -> bool:
        print(f"Join room {room_id}")

        if c.root.join_room(room_id, c):
            self.room_id: uuid.UUID = room_id
            return True
        
        return False
    
    def get_gamestate(self, room_id: uuid.UUID) -> dict[str, Any]:
            return self.gamestate

class MenuPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller: Client) -> None:
        ttk.Frame.__init__(self, parent)
        self.controller: Client = controller

        label: ttk.Label = ttk.Label(self, text="Py-toe-n", font=title_font)
        label.pack(side="top", fill="y", padx=5, pady=10)

        ttk.Button(self, text="Create room", command=controller.create_room).pack(side="top")
        ttk.Button(self, text="Join room", command=lambda: controller.show_frame("RoomList")).pack(side="top")


class RoomList(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller: Client) -> None:
        ttk.Frame.__init__(self, parent)
        self.controller: Client = controller

        label: ttk.Label = ttk.Label(self, text="Room List", font=title_font)
        label.pack(side="top", fill="y", padx=5, pady=10)

        self.room_buttons_frame: ttk.Frame = ttk.Frame(self)
        self.room_buttons_frame.pack(side="top", fill="both", expand=True)

    def refresh(self) -> None:
        print("refresh called")
        for widget in self.room_buttons_frame.winfo_children():
            widget.destroy()

        rooms: list[dict[str, Any]] = c.root.get_rooms()
        for room in rooms:
            button = ttk.Button(
                self.room_buttons_frame,
                text=f"{room['room_id']}",
                command=lambda r=room['room_id']: self.join_room(r)
            )
            button.pack(side="top")

    def join_room(self, room_id: uuid.UUID) -> None:
        self.controller.join_room(room_id)
        self.controller.show_frame("ShowGame")

class WaitingRoom(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller: Client) -> None:
        ttk.Frame.__init__(self, parent)
        self.controller: Client = controller

        label: ttk.Label = ttk.Label(self, text="Waiting Room", font=title_font)
        label.pack(side="top", fill="y", padx=5, pady=10)

        c1: ttk.Label = ttk.Label(self, text=id(self))
        c1.pack(side="left", fill="x", padx=5)

        vs: ttk.Label = ttk.Label(self, text="vs.")
        vs.pack(side="left", fill="x", padx=20)

        self.c2: ttk.Label = ttk.Label(self, text="Waiting...")
        self.c2.pack(side="left", fill="x", padx=5)

class ShowGame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller: Client) -> None:
        ttk.Frame.__init__(self, parent)
        self.controller: Client = controller

        gamestate: dict[str, Any] = c.root.get_gamestate()

        self.buttons: list[ttk.Button] = []

        for i, field in enumerate(gamestate):
            col: int = i % 3
            row: int = i // 3
            button: ttk.Button = ttk.Button(self, text=field, command=lambda: c.root.check(i, controller))
            button.grid(column=col, row=row, sticky="nsew", padx=2, pady=2)
            self.buttons.append(button)

        for i in range(3):
            self.grid_rowconfigure(i, weight=1, uniform="row")
            self.grid_columnconfigure(i, weight=1, uniform="col")

if __name__ == "__main__":
    client: Client = Client()
    c.root.register(ClientService(client))
    client.mainloop()