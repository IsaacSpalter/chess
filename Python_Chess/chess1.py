import pygame
import chess
import chess.engine
import chess.pgn
import asyncio

import pygame_widgets
from pygame_widgets.textbox import TextBox
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.button import Button
from pygame_widgets.button import ButtonArray


# for handling file selection:
import tkinter as tk
#from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import Listbox
from tkinter import StringVar
import os

#screen = pygame.display.set_mode((640, 480))
#clock = pygame.time.Clock()

pygame.init()

# ---------- constants ---------
# Define colors
COLOR_NORMAL = (100, 100, 100)
COLOR_HOVER = (150, 150, 150)
COLOR_CLICK = (200, 200, 200)
TEXT_COLOR = (255, 255, 255)

# text display fonts
big_font = pygame.font.SysFont(None, 48) # Use default font, size 48
# or use a specific system font (check availability first)
message_font = pygame.font.SysFont('Arial', 16)
coord_font = pygame.font.SysFont('Arial', 14)
button_font = pygame.font.SysFont('Arial', 16)

WIDTH = HEIGHT = 512 # You can choose a different size
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # For animations
BOTTOM_MARGIN = 400
RIGHT_MARGIN = 100

# ------ Global Variables --------
# Note: using lists to allow modifications (mutable)

screen = pygame.display.set_mode((WIDTH + RIGHT_MARGIN, HEIGHT + BOTTOM_MARGIN))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()
screen.fill(pygame.Color("white"))

background = pygame.Surface(screen.get_size())
background.fill((0, 0, 0)) # Black

# ==================================================
# Create a new board instance
# the board is global to allow Button class access

board = chess.Board()
Initial_FEN = [board.fen()]

# Text Input will load a new starting position from FEN string:
New_Position_Loaded = [False]
New_FEN = ['']

# load stockfish engine
# This is bloabal to allow button access
engine = chess.engine.SimpleEngine.popen_uci(r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")

# Reversed Display indication
is_reversed = [False]

display_changed = [False]  # to save unnecessary re-drawing of the display

# recording a loaded game
game_r = [chess.pgn.Game()]
game_r_current_move = [0]
game_r_moves = []

# -------- functions ------------

def draw_text(screen,text,font,position,color = pygame.Color("white")):
    text_surface = font.render(text,True,color)
    # clear the area of the surface to be blit
    txt_rect = text_surface.get_rect(topleft = position)
    screen.blit(background, txt_rect, txt_rect)
    screen.blit(text_surface,position)

def draw_text_transparent(screen,text,font,position,color = pygame.Color("white")):
    text_surface = font.render(text,True,color)
    screen.blit(text_surface,position)

IMAGES = {}

def load_images():
    pieces = ['P', 'R', 'N', 'B', 'Q', 'K', 'p', 'r', 'n', 'b', 'q', 'k'] 
    pieces_file_names = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for i in range(len(pieces)):
        # Load and scale images, store in a dictionary (e.g., IMAGES)
        # Example: IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        IMAGES[pieces[i]] = pygame.transform.scale(pygame.image.load("images/" + pieces_file_names[i] + ".png"), (SQ_SIZE, SQ_SIZE))
        pass # (Requires image assets in an "images" folder)

def draw_board(screen):
    if is_reversed[0]:
        colors = [pygame.Color("gray"), pygame.Color("white")] # Reversed Colors
        letters = 'HGFEDCBA'
        numbers = '12345678'
    else:
        colors = [pygame.Color("white"), pygame.Color("gray")] # Normal Colors
        letters = 'ABCDEFGH'
        numbers = '87654321'
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    # draw letters 
    for c in range(DIMENSION):
        draw_text_transparent(screen,letters[c],coord_font,(c * SQ_SIZE + 2,HEIGHT - 20),pygame.Color("black"))
    # draw numbers
    for r in range(DIMENSION):
        draw_text_transparent(screen,numbers[r],coord_font,(2, r * SQ_SIZE + 2),pygame.Color("black"))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            square = chess.square(c, 7 - r) # Map (row, col) to algebraic notation
            piece = board.piece_at (square)
#            print(f"p0iece: {piece}")
            if piece:
#                    print(f"piece: {piece} will display at row: {r} col: {c}")
                # Draw the corresponding image from the IMAGES dictionary
                if is_reversed[0]:
                    screen.blit(IMAGES[str(piece)], pygame.Rect((7 - c) * SQ_SIZE, (7 - r) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    screen.blit(IMAGES[str(piece)], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

#                    print(f"piece: {piece} will display at row: {r} col: {c}")
                    #user_input = input("After Draw Piece Want to continue: ")



# Assume SQ_SIZE is the pixel size of one square (e.g., 64 or 80)
# Assume you have a game state 'gs' or 'board' object to manage the game logic

def get_row_col_from_mouse(pos, SQ_SIZE):
    x, y = pos
    # Integer division to find which square was clicked
    col = x // SQ_SIZE
    row = y // SQ_SIZE
    # reverse the row as white is at bottom
    # map 0-7 => 7-0
#    row = 7 - row 
    if is_reversed[0]:
        row = 7 - row
        col = 7 - col
    return row, col # (row, col) tuple

def coords_to_uci(start_sq, end_sq):
    # Convert (row, col) to algebraic notation (e.g., (7, 4) -> 'e1', (6, 4) -> 'e2')
    # Depends on how you define your board orientation (0,0 is top-left usually in Pygame)
    start_file = chr(ord('a') + start_sq[1])
    start_rank = 8 - start_sq[0]
    end_file = chr(ord('a') + end_sq[1])
    end_rank = 8 - end_sq[0]
    return f"{start_file}{start_rank}{end_file}{end_rank}"




# Functions to link to the buttons --------------------------------
def backword_move():
    print("Backword Move...")
    if len(board.move_stack) > 0:
        board.pop()
        display_changed[0] = True
    else:
        print("Backword not available")

def engine_move():
    result = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(result.move)
    display_changed[0] = True

def reverse_display():
    is_reversed[0] = not is_reversed[0]
    display_changed[0] = True

def save_game():
    print("Save Game")
    # Open the file dialog and get the selected file path
    file_path = filedialog.asksaveasfilename(
        initialdir="/",  # Optional: specify initial directory
        title="Select a file to save", # Optional: set dialog title
        filetypes=(("PGN files", "*.pgn"), ("All files", "*.*")) # Optional: filter file types
    )

    # Print the selected file path
    if file_path:
        print("Selected file:", file_path)
        # You can now use the file_path variable to open the file, e.g.:
        # with open(file_path, 'r') as f:
        #     content = f.read()

        game = chess.pgn.Game.from_board(board)

        # Add game headers
        game.headers["Event"] = "Example Game"
        game.headers["White"] = "Player 1"
        game.headers["Black"] = "Player 2"

        # Write to a PGN file
        with open(file_path, "w") as f:
            exporter = chess.pgn.FileExporter(f)
            game.accept(exporter)
            print("Game exported successfully.")
    else:
        print("No file selected.")

# select game from multiple pgn:

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
#        print(f"reverseButton state is {is_reversed.get()}")
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
    lbox = Listbox(root, listvariable=choicesvar, width=100,height=400)
    lbox.pack(pady = 2)
    lbox.bind('<<ListboxSelect>>', itemSelected)

    # Start the Tkinter event loop
    root.mainloop()

    if len(game) == 0:  # nothing selected, return the first game
        return games[0]
    else:
        return game[0]


def load_game():
    print("Load Game")

    games = []
    games_headers = []

    # Open the file dialog and get the selected file path
    file_path = filedialog.askopenfilename(
        initialdir="/",  # Optional: specify initial directory
        title="Select a file to load game", # Optional: set dialog title
        filetypes=(("PGN files", "*.pgn"), ("All files", "*.*")) # Optional: filter file types
    )
    # Print the selected file path
    if file_path:
        print("Selected file:", file_path)
        try:
            pgn = open(file_path)
            #game = chess.pgn.read_game(pgn)

            # invoke the gameselect dialog
            # first prepare the list of games amd games_headers
            idx = 0
            while True:
                game_to_load = chess.pgn.read_game(pgn)
                if game_to_load is None:
                    break  # No more games
                games.append(game_to_load)
                s = f'{idx} {game_to_load.headers["Event"]} {game_to_load.headers["Site"]}  {game_to_load.headers["Date"]} {game_to_load.headers["White"]} ({game_to_load.headers["WhiteElo"]})  {game_to_load.headers["Black"]} ({game_to_load.headers["BlackElo"]}) {game_to_load.headers["Result"]}'
        #        print(s)
                games_headers.append(s)
                idx += 1
            print(f"Loaded {len(games)} games")
            game = select_game(games,games_headers)

            game_r[0] = game
            print(game_r[0])
            game_r_current_move[0] = 0

            game_r_moves.clear()
            for move in game_r[0].mainline_moves():
                game_r_moves.append(move)
        except:
            print("Unable to parse the game")
        else:
            
            print(f"Loading game {game.headers['Event']}")
#            print(game.headers)
#            print(game_r_moves)

            # Iterate through all moves and play them on a board.
            board.reset()
#            board.set_board_fen(Initial_FEN[0])
            for move in game.mainline_moves():
                board.push(move)
#                print(move)

            exporter_mainline = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
            pgn_string = game_r[0].accept(exporter_mainline)

            # strip the string of newline
            s1 = pgn_string.replace('\n',' ')


            s = convert_text_to_multiline(s1, 100)
            print(s)

            # draw_text(screen,pgn_string,message_font,
            #         (5, HEIGHT + 230))  
            # draw game header
            sh = f' {game.headers["Event"]} {game.headers["Site"]}  {game.headers["Date"]} {game.headers["White"]} ({game.headers["WhiteElo"]})  {game.headers["Black"]} ({game.headers["BlackElo"]}) {game.headers["Result"]}'
            blit_multiline_text(screen, sh, message_font, (200,200,200), 5, HEIGHT + 230)  

            # draw the game
            blit_multiline_text(screen, s, message_font, (200,200,200), 5, HEIGHT + 260)  

            #try iterating through mainline moves:
            # game_r_iter = iter(game_r.mainline_moves())
            # for i in range(10):
            #     move = next(game_r_iter)
            #     print(f"{i} {move}")

            display_changed[0] = True

    else:
        print("No file selected.")

# Handle game control buttons:

def game_reset():
    print("game_reset")
    game_r_current_move[0] = 0
    board.reset()
    display_changed[0] = True

def game_move_back():
    if game_r_current_move[0] > 0:
        game_r_current_move[0] -= 1
    print(f"game_move_back at {game_r_current_move[0]}")
    load_board_from_game(game_r_current_move[0])

def game_move():
    if game_r_current_move[0] < len(game_r_moves):
        game_r_current_move[0] += 1
    print(f"game_move at {game_r_current_move[0]}")
    load_board_from_game(game_r_current_move[0])

def game_end():
    print("game_end")
    game_r_current_move[0] = len(game_r_moves)
    print(f"game_move at {game_r_current_move[0]}")
    load_board_from_game(game_r_current_move[0])

def load_board_from_game(n):
    print(f"load board from game up to {n} moves")

    board.reset()
    i = 0

    for move in game_r_moves:
        if i > n:
            break
        else:
#            print(f"{i} {move}")
            board.push(move)
        i += 1


    display_changed[0] = True


def text_input():
    fen_text = textbox.getText()
    print(fen_text)
    # try to load the game
    try:
        try_board = chess.Board()
        try_board.set_fen(fen_text)
    except ValueError:
        print(f"Invalid FEN loaded: {fen_text}")
    else:
        print("New FEN loaded successfully")
        New_Position_Loaded[0] = True
        New_FEN[0] = fen_text

    textbox.setText('')

# create a text box for text input to load FEN position to the board
textbox = TextBox(screen, 5, HEIGHT + 100, WIDTH - 5, 40, font = message_font, fontSize=16,
                borderColour=(200, 200, 200), textColour=(0, 0, 0),
                onSubmit=text_input, radius=2, borderThickness=2)

# dropdown for selecting quinning piece
quinning_selection_dropdown = Dropdown(
    screen, 5, HEIGHT + 150, 100, 30, name='Select Quinning Piece',
    font = message_font, fontSize=14,
    choices=[
        'Quin',
        'Rook',
        'Bishop',
        'Knight'
    ],
    borderRadius=3, colour=pygame.Color('green'), values=['q', 'r', 'b', 'n'], direction='right', textHAlign='left'
)

# Game control button array

buttonArray = ButtonArray(
    # Mandatory Parameters
    screen,  # Surface to place button array on
    5,  # X-coordinate
    HEIGHT + 190,  # Y-coordinate
    200,  # Width
    30,  # Height
    (4, 1),  # Shape: 2 buttons wide, 2 buttons tall
    border=10,  # Distance between buttons and edge of array
    texts=('<<', '<', '>', '>>'),  # Sets the texts of each button (counts left to right then top to bottom)
    # When clicked, print number
    onClicks=(game_reset, game_move_back, game_move, game_end)
)



def print_value():
    print(quinning_selection_dropdown.getSelected())



# Your multi-line text using triple quotes or explicit '\n'
multitext = """Hello World!
Goodbye World!
I'm back World!"""


def blit_multiline_text(surface, text, font, color, x, y):
    """Helper function to render and blit multi-line text."""
    # Get the height of a single line of text for correct spacing
    line_height = font.get_linesize()
    lines = text.splitlines() # Splits the string by newline characters


# clear the area of the nulti text
    clear_background = pygame.Surface((WIDTH, HEIGHT))
    clear_background.fill((0, 0, 0)) # Fill with black
    surface.blit(clear_background, (x, y))

    for i, line in enumerate(lines):
        # Render each line separately
        txt_surface = font.render(line, True, color)
        # clear the area of the surface to be blit
        txt_rect = txt_surface.get_rect(topleft = (x, y + i * line_height))
        surface.blit(background, txt_rect, txt_rect)
        # Blit the surface at the correct Y position
        surface.blit(txt_surface, (x, y + i * line_height))

def convert_list_to_multiline(in_list, max_lines):
    # assuming input as list of strings, concatenate with a new line separator
    # (only last max_lines lines)
    out_string = ''
    list_len = len(in_list)
    if list_len > max_lines:
        # set initial line
        initial_line = list_len - max_lines
    else:
        initial_line = 0

    for s in in_list[initial_line:]:
        out_string += '\n' + s

    return out_string[1:]

def convert_text_to_multiline(in_text, max_line_length):
    out_string = in_text[0:max_line_length]
    end_line = max_line_length
    while end_line < len(in_text):
        out_string += '\n' + in_text[end_line:end_line + max_line_length]
        end_line += max_line_length
    
    return out_string


def get_san_move_stack(board_history):
    # Start from a fresh board (or the game's initial FEN if different)
    temp_board = chess.Board()
    if New_FEN[0]  != '':
        temp_board.set_fen(New_FEN[0])
    san_list = []
    
    # Replay each move in the history to get its SAN representation
    for move in board_history:
        # Use push_san() with the current move object
        san_list.append(temp_board.san(move))
        temp_board.push(move)

    # insert move numbers, and pair W + B half moves to full move 
    # convert ['e4', 'e5', 'Nf3', 'Bc5']
    # to: ['1. e4 e5', '2.Nf3 Bc5']

    out_list = []
    move_number = 1
    white_turn = True
    full_move = ''
    for half_move in san_list:
        if white_turn:
            full_move = str(move_number) + '.' + half_move
            # Append the last White move, if we are at the end of san_list
            if (move_number * 2) == len(san_list) + 1:
                out_list.append(full_move)
        else:
            full_move = full_move + ' ' + half_move
            out_list.append(full_move)
            move_number += 1
        white_turn = not white_turn

    return out_list


def main():
    # Create a new board instance
    #board = chess.Board()
    print("Welcome to Python Chess!")

    # Create the buttons

    back_button = Button(
        screen,  # Surface to place button on
        5,  # X-coordinate of top left corner
        HEIGHT + 25,  # Y-coordinate of top left corner
        100,  # Width
        40,  # Height
        text='Back',  # Text to display
        font = button_font,
        fontSize=12,  # Size of font
        margin=5,  # Minimum distance between text/image and edge of button
        inactiveColour=COLOR_NORMAL,  # Colour of button when not being interacted with
        hoverColour=COLOR_HOVER,  # Colour of button when being hovered over
        pressedColour=COLOR_CLICK,  # Colour of button when being clicked
        radius=5,  # Radius of border corners (leave empty for not curved)
        onClick= backword_move  # Function to call when clicked on
    )        
        
    engine_move_button = Button(
        screen,  # Surface to place button on
        115,  # X-coordinate of top left corner
        HEIGHT + 25,  # Y-coordinate of top left corner
        100,  # Width
        40,  # Height
        text='Engine',  # Text to display
        font = button_font,
        fontSize=12,  # Size of font
        margin=5,  # Minimum distance between text/image and edge of button
        inactiveColour=COLOR_NORMAL,  # Colour of button when not being interacted with
        hoverColour=COLOR_HOVER,  # Colour of button when being hovered over
        pressedColour=COLOR_CLICK,  # Colour of button when being clicked
        radius=5,  # Radius of border corners (leave empty for not curved)
        onClick= engine_move  # Function to call when clicked on
    )

    reverse_button = Button(
        screen,  # Surface to place button on
        225,  # X-coordinate of top left corner
        HEIGHT + 25,  # Y-coordinate of top left corner
        100,  # Width
        40,  # Height
        text='Reverse',  # Text to display
        font = button_font,
        fontSize=12,  # Size of font
        margin=5,  # Minimum distance between text/image and edge of button
        inactiveColour=COLOR_NORMAL,  # Colour of button when not being interacted with
        hoverColour=COLOR_HOVER,  # Colour of button when being hovered over
        pressedColour=COLOR_CLICK,  # Colour of button when being clicked
        radius=5,  # Radius of border corners (leave empty for not curved)
        onClick= reverse_display  # Function to call when clicked on
    )

    save_button = Button(
        screen,  # Surface to place button on
        335,  # X-coordinate of top left corner
        HEIGHT + 25,  # Y-coordinate of top left corner
        100,  # Width
        40,  # Height
        text='Save Game',  # Text to display
        font = button_font,
        fontSize=12,  # Size of font
        margin=5,  # Minimum distance between text/image and edge of button
        inactiveColour=COLOR_NORMAL,  # Colour of button when not being interacted with
        hoverColour=COLOR_HOVER,  # Colour of button when being hovered over
        pressedColour=COLOR_CLICK,  # Colour of button when being clicked
        radius=5,  # Radius of border corners (leave empty for not curved)
        onClick= save_game  # Function to call when clicked on
    )

    load_button = Button(
        screen,  # Surface to place button on
        445,  # X-coordinate of top left corner
        HEIGHT + 25,  # Y-coordinate of top left corner
        100,  # Width
        40,  # Height
        text='Load Game',  # Text to display
        font = button_font,
        fontSize=12,  # Size of font
        margin=5,  # Minimum distance between text/image and edge of button
        inactiveColour=COLOR_NORMAL,  # Colour of button when not being interacted with
        hoverColour=COLOR_HOVER,  # Colour of button when being hovered over
        pressedColour=COLOR_CLICK,  # Colour of button when being clicked
        radius=5,  # Radius of border corners (leave empty for not curved)
        onClick= load_game  # Function to call when clicked on
    )


    # draw pygame board
    load_images()

    pygame.display.set_caption(f"Chess Game    {'White' if board.turn else 'Black'} turn {'REVERSED' if is_reversed[0] else 'NORMAL'}")

    screen.fill((0,0,0))    # Black
    draw_board(screen)
    draw_pieces(screen, board)

#    screen.blit(text_input.surface, (5, HEIGHT + 5))
   # example of text box draing:
    status_text_message = "Initial Game"
    draw_text(screen,status_text_message,message_font,
               (5, HEIGHT + 5))
    pygame.display.flip()
    clock.tick(MAX_FPS)

    running = True
    player_clicks = [] # list of two (row, col) tuples

    while running: 
        # and not board.is_game_over():
        sq_selected = () # keeps track of the last click (row, col)
        display_changed[0] = False  

        events = pygame.event.get()
        
 
        # check widget events
        # widgets include setting new FEN via text box

# 1r1k4/p1p5/3p4/8/8/4P3/5P2/2K2R2 w - - 0 1
# 1r1k4/p1p5/3p4/8/8/4P3/5P2/2K2R2 b - - 0 1
# quinning:
# 8/2k3P1/8/8/8/8/2K4p/8 w - - 0 1


        pygame_widgets.update(events)
        pygame.display.update()

        if New_Position_Loaded[0]:
            # initialize the board
            board.clear()
            board.set_fen(New_FEN[0])
            #board.clear()
            draw_board(screen)
            draw_pieces(screen, board)
            pygame.display.flip()
            New_Position_Loaded[0] = False

            print([move.uci() for move in board.legal_moves])



        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # Check for button clicks
            # back_button.check_click(event)
            # engine_move_button.check_click(event)
            # reverse_button.check_click(event)

            # Handle user clicks within board limits
            if event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] < HEIGHT and event.pos[1] < WIDTH:
                location = event.pos # (x, y) location of the mouse
                row, col = get_row_col_from_mouse(location, SQ_SIZE)
                print(f"location: {event.pos} row: {row}  col: {col}")

                if sq_selected == (row, col): # user clicked the same square twice, deselect
                    sq_selected = ()
                    player_clicks = []
                    print(f'reselected the same position {row},{col}')
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected) # append for first or second click

                print(player_clicks)    
                if len(player_clicks) == 2: # after the second click
                    # The move is defined: from_square, to_square
                    move = (player_clicks[0], player_clicks[1]) 
                    uci_move = coords_to_uci(player_clicks[0], player_clicks[1])
                    # if quinning a pown atach the selected quinning piece 
                    #    as defined in quinning_selection_dropdown

                    # print(uci_move[0:2])
                    # print(uci_move[2:])
                    # print(player_clicks[1][0])
 
                    from_square = chess.parse_square(uci_move[0:2])
                    to_square = chess.parse_square(uci_move[2:])

                    # print(f"Moving from square: {from_square} to square: {to_square}")
                    # print(board.piece_at(from_square).symbol)
                    # print(board.piece_at(from_square).piece_type)
                    # print(chess.square_rank(to_square))
                    # if board.piece_at(from_square).piece_type == 1:
                    #     print("Pown !")

                    if board.piece_at(from_square).piece_type == 1 and chess.square_rank(to_square) in [0, 7]:
                        if quinning_selection_dropdown.getSelected() is None:
                            quinning_piece = 'q'   # Quin is the default
                        else:
                            quinning_piece = quinning_selection_dropdown.getSelected()
                        print(f"Quinning piece: {quinning_piece}")
                        uci_move += quinning_piece

                    print(f"Move: {uci_move}")
                    if uci_move in [move.uci() for move in board.legal_moves]:
                        # Handle Legal Move
                        board.push_uci(uci_move)
                        display_changed[0] = True
                        # Reset clicks for the next turn
                        sq_selected = ()
                        player_clicks = []
                        # stockfish engine evaluation
                        info = engine.analyse(board, chess.engine.Limit(time=0.1))
                        print("Score:", info["score"])                        
                        # refresh the status message
                        status_text_message = f'Move: {uci_move} Score: {info["score"]}'
                        #last_moves_message = f'Moves: {board.variation_san([chess.Move.from_uci(m) for m in board.move_stack])}'
                        #print(last_moves_message)

                    else:
                        # Handle invalid move case
                        print("Invalid move parsing from mouse clicks")
                        sq_selected = ()
                        player_clicks = []
  

      # Handle game over conditions
        if board.is_game_over():
            running = False   
            pygame.display.set_caption(f"Chess Game    Game over. Result: {board.result()} {'REVERSED' if is_reversed[0] else 'NORMAL'}")
            # Handle game over conditions
            print(f"Game over. Result: {board.result()}")
            if board.is_checkmate():
                print("Checkmate!")
            elif board.is_stalemate():
                print("Stalemate!")    
            x = input("Hit ENTER to continue")
        else:
            pygame.display.set_caption(f"Chess Game    {'White' if board.turn else 'Black'} turn {'REVERSED' if is_reversed[0] else 'NORMAL'}")

        # refresh the display
        # screen.fill((0,0,0))
        if display_changed[0]:  
            draw_board(screen)
            draw_pieces(screen, board)
            draw_text(screen,status_text_message,message_font,
                (5, HEIGHT + 5))
            # display last 24 moves on right pane
            full_san_history = get_san_move_stack(board.move_stack)
            out_s = convert_list_to_multiline(full_san_history,24)
            blit_multiline_text(screen, out_s, message_font, (200, 200, 200), 5 + WIDTH, 5)

            pygame.display.update()
        clock.tick(MAX_FPS)

    # end of while running main loop






#    user_input = input("Want to continue: ")

    engine.quit()



if __name__ == "__main__":
    main()