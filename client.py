from tkinter import * # pyright: ignore[reportWildcardImportFromLibrary]
from tkinter import ttk

import rpyc
c = rpyc.connect("localhost", 18861)

class Client():
    def __init__(self):
        self.create_window()

    def create_window(self):
        root = Tk()
        frm = ttk.Frame(root, padding=10)
        frm.grid()
        ttk.Label(frm, text="Py-toe-n").grid(column=0,row=0)
        ttk.Button(frm, text="Create room", command=self.create_room).grid(column=0,row=1)
        ttk.Button(frm, text="Join room", command=self.join_room).grid(column=0,row=2)
        ttk.Button(frm, text="Help", command=self.show_help).grid(column=0,row=3)
        root.mainloop()

    def create_room(self):
        id = c.root.create_room()
        print(f"RoomID: {id}")

    def join_room(self):
        pass

    def show_help(self):
        pass

if __name__ == "__main__":
    Client()