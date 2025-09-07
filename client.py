import tkinter as tk
from tkinter import ttk, font

from typing import Any

import rpyc
import uuid

title_font: font.Font
medium_font: font.Font

c: rpyc.Connection = rpyc.connect("localhost", 18861)
bgsrv: rpyc.BgServingThread = rpyc.BgServingThread(c)

class Client(tk.Tk):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.title("Py-toe-n")
        self.geometry("300x300")

        self.style = ttk.Style(self)
        self.style.configure("Starting.TFrame", background="green")

        global title_font
        title_font = font.Font(family="Helvetica", size=20, weight="bold")
        global medium_font
        medium_font = font.Font(family="Helvetica", size=11, weight="bold")

        container: ttk.Frame = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames: dict[str, ttk.Frame] = {}  
        for F in (WaitingRoom, GameFrame, EndFrame):
            page_name: str = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WaitingRoom")
        c.root.ready(self.update_callback)

    def update_callback(self, gamestate: dict[str, Any], player_nr: str = "") -> None:
        self.gamestate = gamestate
        if gamestate["state"] == "waiting":
            self.player_nr = player_nr
            self.after(0, lambda: self.show_frame("GameFrame"))
            if self.player_nr == gamestate["turn"]:
                self.after(0, lambda: self.frames["GameFrame"].configure(style="Starting.TFrame"))
            else:
                self.after(0, lambda: self.frames["GameFrame"].configure(style="TFrame"))
        elif gamestate["state"] == "playing":
            self.after(0, self.update_buttons(gamestate["field"]))
            if self.player_nr == gamestate["turn"]:
                self.after(0, lambda: self.frames["GameFrame"].configure(style="Starting.TFrame"))
            else:
                self.after(0, lambda: self.frames["GameFrame"].configure(style="TFrame"))
        elif gamestate["state"] == "finished":
            text = "You won!!!" if gamestate["winner"] == self.player_nr else "You lose!!!"
            self.after(0, self.frames["EndFrame"].label.config(text=text))
            self.after(0, lambda: self.show_frame("EndFrame"))
        else:
            print("Unknown game state.")

    def show_frame(self, name: str) -> None:
        frame: ttk.Frame = self.frames[name]

        frame.tkraise()

    def update_buttons(self, fields: list[str]) -> None:
        for idx,field in enumerate(fields):
            self.frames["GameFrame"].buttons[idx].config(text=field)     

class WaitingRoom(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller: Client) -> None:
        ttk.Frame.__init__(self, parent)
        self.controller: Client = controller

        label: ttk.Label = ttk.Label(self, text="Py-toe-n", font=title_font)
        label.pack(side="top", fill="y", padx=5, pady=10)

        c1: ttk.Label = ttk.Label(self, text=id(self), font=medium_font)
        c1.pack(side="left", fill="x", padx=5)

        vs: ttk.Label = ttk.Label(self, text="vs.", font=medium_font)
        vs.pack(side="left", fill="x", padx=20)

        self.c2: ttk.Label = ttk.Label(self, text="Waiting...", font=medium_font)
        self.c2.pack(side="left", fill="x", padx=5)

class GameFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller: Client) -> None:
        ttk.Frame.__init__(self, parent)
        self.controller: Client = controller

        self.buttons: list[ttk.Button] = []

        for i in range(9):
            col: int = i % 3
            row: int = i // 3
            button: ttk.Button = ttk.Button(self, text="", command=lambda idx=i: c.root.check(idx, controller.player_nr))
            button.grid(column=col, row=row, sticky="nsew", padx=2, pady=2)
            self.buttons.append(button)

        for i in range(3):
            self.grid_rowconfigure(i, weight=1, uniform="row")
            self.grid_columnconfigure(i, weight=1, uniform="col")

class EndFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller: Client) -> None:
        ttk.Frame.__init__(self, parent)
        self.controller: Client = controller

        self.label: ttk.Label = ttk.Label(self, text="", anchor="center", font=title_font)
        self.label.pack(expand=True)

if __name__ == "__main__":
    client: Client = Client()
    client.mainloop()

    bgsrv.stop()
    c.close()