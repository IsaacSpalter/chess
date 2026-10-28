import chess.pgn

# for handling file selection:
import tkinter as tk
from tkinter import *
from tkinter import ttk


from tkinter import filedialog
import os

games = []
games_headers = []
# consider passing game_headers, then upon selecting a game select by index with fetch()
def select_game(games,games_headers):
    # Create the main application window
    root = tk.Tk()
    root.title("Select Game")
    root.geometry("600x800") # sets the window size (width x height)

    game = []
    is_reversed = tk.BooleanVar(value=False)
    
    def itemSelected(*args):
        idxs = lbox.curselection()
        if len(idxs)==1:
            idx = int(idxs[0])
            game.append(games[idx])
            print(f"Selected game at index {idx}")
            root.destroy()

    def reverseChanged(*args):
        #is_reversed[0] = not is_reversed[0]
        
        print(f"reverseButton state is {is_reversed.get()}")
        games.reverse()
        games_headers.reverse()
        choicesvar.set(games_headers)

    # reverse check button
    checkReverse = ttk.Checkbutton(root, text='Reverse List', 
	    command=reverseChanged, variable=is_reversed)


    # Add a label widget
    label = tk.Label(root, text=f"Select a game from the list ({len(games_headers)}) ")
    label.pack(pady=20) # places the label in the window with vertical padding
    checkReverse.pack(pady= 10)

    # Display the games list:
    choicesvar = StringVar(value=games_headers)
    # lbox = Listbox(c, listvariable=choicesvar)
    lbox = Listbox(root, listvariable=choicesvar, width=100,height=400)

    # lbox.grid(column=0, row=0, rowspan=6, sticky=(N,S,E,W))
    lbox.pack(pady = 2)

    lbox.bind('<<ListboxSelect>>', itemSelected)

    # Start the Tkinter event loop
    root.mainloop()

    if len(game) == 0:  # nothing selected, return the first game
        return games[0]
    else:
        return game[0]



#with open("C:\Python_Chess\PGN\Tal_multi.pgn") as pgn:
#with open("C:\Python_Chess\PGN\Carlsen.pgn") as pgn:
with open("C:\Python_Chess\PGN\Tal.pgn") as pgn:
    idx = 0
    while True:
        game = chess.pgn.read_game(pgn)
        if game is None:
            break  # No more games
#        print(game.headers["Event"]) # Process game
        games.append(game)
        s = f'{idx} {game.headers["Event"]} {game.headers["Site"]}  {game.headers["Date"]} {game.headers["White"]} ({game.headers["WhiteElo"]})  {game.headers["Black"]} ({game.headers["BlackElo"]}) {game.headers["Result"]}'
#        print(s)
        games_headers.append(s)
        idx += 1
print(f"Loaded {len(games)} games")

game = select_game(games,games_headers)
print("After game selection")
print(game)

