import tkinter as tk
from tkinter import ttk

import rpyc
import uuid

c = rpyc.connect("localhost", 18861)

class Client(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MenuPage, RoomList):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MenuPage")

        self.client_id = uuid.uuid4()

    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()

    def show_room_list(self, root: tk.Tk) -> None:
        pass

    def create_room(self) -> None:
        id: uuid.UUID = c.root.create_room(self.client_id)

    def join_room(self, room_id: uuid.UUID) -> None:
        print(f"Join room {room_id}")

    def show_help(self) -> None:
        pass

class MenuPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Py-toe-n")
        label.pack(side="top", fill="y", padx=5, pady=10)

        ttk.Button(self, text="Create room", command=controller.create_room).pack(side="top")
        ttk.Button(self, text="Join room", command=lambda: controller.show_frame("RoomList")).pack(side="top")
        ttk.Button(self, text="Help", command=controller.show_help).pack(side="top")


class RoomList(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Room List")
        label.pack(side="top", fill="y", padx=5, pady=10)

        rooms = c.root.get_rooms()

        for room in rooms:
            button = ttk.Button(self, text=f"{room['room_id']} - Oponent: {room['oponent']}", command=lambda: controller.join_room(room['room_id']))
            button.pack(side="top")

if __name__ == "__main__":
    client = Client()
    client.mainloop()