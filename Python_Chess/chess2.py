from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import Listbox
from tkinter import StringVar
from tkinter import messagebox
from PIL import Image, ImageTk # Import Image and ImageTk modules

import chess
import chess.engine
import chess.pgn

# ---------- constants ---------
# Define colors
COLOR_NORMAL = (100, 100, 100)
COLOR_HOVER = (150, 150, 150)
COLOR_CLICK = (200, 200, 200)
TEXT_COLOR = (255, 255, 255)

WIDTH = HEIGHT = 512 # You can choose a different size
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION

BOTTOM_MARGIN = 400
RIGHT_MARGIN = 100

NORMAL_BORDER_WIDTH = 2
SELECTED_BORDER_WIDTH = 5

# UI layout as:
# root   Tk
#   gameButtons   Frame
#   mainframe     Frame
#     boardframe    Frame
#        cavas        Canvas
#     l             Label
#     rtext         Text to the right side
#     rtext_ys      y scroller for rtext
#     btext         Text to the bottom 
#     btext_xs      x scroller for btext

root = Tk()
root.title("Chess2")
root.option_add('*tearOff', FALSE)


gameButtons = ttk.Frame(root,width=700,height=40,borderwidth=5 ,relief = 'ridge',padding=(15,5,15, 5) )
mainframe = ttk.Frame(root, width=WIDTH + RIGHT_MARGIN + 20,height=HEIGHT + BOTTOM_MARGIN + 10)
headerframe = ttk.Frame(mainframe,width=WIDTH + RIGHT_MARGIN + 20,height=60, borderwidth=5, relief = 'ridge')
boardframe = ttk.Frame(mainframe,width=WIDTH, height=HEIGHT, borderwidth=5, relief = 'ridge')
gameButtons.grid(column=0,row=0,sticky='nw')
mainframe.grid(column=0,row=1)
headerframe.grid(column=0,row=0, sticky='nw')
boardframe.grid(column=0,row=1, sticky='nw')

l =ttk.Label(mainframe, text="Starting...",width = RIGHT_MARGIN + 20)
l.grid(column=0,row=3)

h_label_text = StringVar()
h_label_text.set('No game selected')
h_label =ttk.Label(headerframe,width = RIGHT_MARGIN + 20)
h_label.grid(column=0,row=0, sticky = 'nwe')
h_label['textvariable'] = h_label_text


# should replace boardframe by canvas
# boardframe.bind('<Enter>', lambda e: l.configure(text='Moved mouse inside'))
# boardframe.bind('<Leave>', lambda e: l.configure(text='Moved mouse outside'))
# boardframe.bind('<ButtonPress-1>', lambda e: l.configure(text='Clicked left mouse button'))
# boardframe.bind('<3>', lambda e: l.configure(text='Clicked third mouse button'))
# boardframe.bind('<Double-1>', lambda e: l.configure(text='Double clicked'))
# boardframe.bind('<B3-Motion>', lambda e: l.configure(text=f'third button drag to {e.x},{e.y}'))
# boardframe.bind('<B1-Motion>', lambda e: l.configure(text=f'Left button drag to {e.x},{e.y}'))


canvas = Canvas(boardframe, width=WIDTH, height=HEIGHT, background='gray75')
canvas.grid(column=0,row=0, sticky='nw')

rtext = Text(mainframe, width = 20, height = 30, wrap = "none")
rtext_ys = ttk.Scrollbar(mainframe, orient = 'vertical', command = rtext.yview)
# rtext_xs = ttk.Scrollbar(root, orient = 'horizontal', command = rtext.xview)
rtext['yscrollcommand'] = rtext_ys.set
#rtext['xscrollcommand'] = rtext_xs.set
for i in range(100):
    rtext.insert('end', f"{i} New Line\n")
rtext.delete('20.0','end')
rtext.grid(column = 1, row = 1, sticky = 'nw')
#rtext_xs.grid(column = 0, row = 1, sticky = 'we')
rtext_ys.grid(column = 2, row = 1, sticky = 'nw')

btext = Text(mainframe, width = 50, height = 7, wrap = "none")
btext_xs = ttk.Scrollbar(mainframe, orient = 'horizontal', command = btext.xview)
btext['xscrollcommand'] = btext_xs.set
# for i in range(100):
#     btext.insert('end', f"{i}.move \t")
#btext.delete('20.0','end')
btext.grid(column = 0, row = 4, sticky = 'we')
btext_xs.grid(column = 0, row = 5, sticky = 'we')

b1text = Text(mainframe, width = 50, height = 5, wrap = "none")
b1text_xs = ttk.Scrollbar(mainframe, orient = 'horizontal', command = b1text.xview)
b1text['xscrollcommand'] = b1text_xs.set
for i in range(100):
     b1text.insert('end', f"{i}.move \t")
#btext.delete('20.0','end')
b1text.grid(column = 0, row = 6, sticky = 'we')
b1text_xs.grid(column = 0, row = 7, sticky = 'we')

mainframe.grid_columnconfigure(0, weight = 1)
mainframe.grid_rowconfigure(0, weight = 1)


#canvas.bind('<ButtonPress-1>', lambda e: l.configure(text=f'Clicked left mouse button at {e.x},{e.y}'))



#========== handle click on rtext
def get_click_position(event):
    # event.widget references the text widget that triggered the click
    text_widget = event.widget
    
    # 1. Translate pixel coordinates into a text index ('line.column')
    click_index = text_widget.index(f"@{event.x},{event.y}")
    
    # 2. Split the index into individual line and column integers
    line, column = map(int, click_index.split('.'))
    
    print(f"Pixel Coordinates: X={event.x}, Y={event.y}")
    print(f"Text Position index: '{click_index}' (Line: {line}, Column: {column})\n")

    # identify how many steps to go back, and then loop to go back
    total_moves = len(board.move_stack)
    moves_to_go_back = total_moves - (line - 1) * 2  # move back to previous line of full moves
    print(f"Go back {moves_to_go_back} moves out of {total_moves}")

    i = 0
    while i < moves_to_go_back:
        if len(board.move_stack) > 0 and running.get():
            board.pop()
            update_canvas()    
        i += 1

rtext.bind("<Button-1>", get_click_position)


IMAGES = {}
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
is_reversed = BooleanVar()

running = BooleanVar()

queening_piece = StringVar()
queening_piece.set('q')  # default queen

display_changed = [False]  # to save unnecessary re-drawing of the display

# move click control 
player_clicks = [] # list of two (row, col) tuples
sq_selected = [] # keeps track of the last click (row, col)



# recording a loaded game
game_r = [chess.pgn.Game()]
game_r_current_move = [0]
game_r_moves = []

# loaded games
games = []
games_headers = []

# the selected game
game = []

# game header 
#                 s = f'{idx} {game_to_load.headers["Event"]} {game_to_load.headers["Site"]}  
# {game_to_load.headers["Date"]} {game_to_load.headers["White"]} ({game_to_load.headers["WhiteElo"]}) 
#  {game_to_load.headers["Black"]} ({game_to_load.headers["BlackElo"]}) {game_to_load.headers["Result"]}'
h_Event = StringVar()
h_Site = StringVar()
h_Date = StringVar()
h_White = StringVar()
h_WhiteElo = StringVar()
h_Black = StringVar()
h_BlackElo = StringVar()
h_Result = StringVar()

# board analysis
analyse_board = BooleanVar(value = True)  # default - analyse

########## functions
def get_row_col_from_mouse(pos, SQ_SIZE):
    x, y = pos
    # Integer division to find which square was clicked
    col = x // SQ_SIZE
    row = y // SQ_SIZE
    # reverse the row as white is at bottom
    # map 0-7 => 7-0
#    row = 7 - row 
    if is_reversed.get():
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

# This is performance heavy.
# consider changing the logic:
# get only the current move san
# add it to the rtext, keeping global track of the rtext position
# if remove - remove the last move from rtext using rtext.delete('move_pos','end')
# (in addition to poping it from the board)
def get_san_move_stack(board_history):
    # Start from a fresh board (or the game's initial FEN if different)
    temp_board = chess.Board()
    white_turn = True
    if New_FEN[0]  != '':
        temp_board.set_fen(New_FEN[0])
        if temp_board.turn == chess.BLACK:
            white_turn = False
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

def convert_list_to_multiline(in_list, max_lines):
    # assuming input as list of strings, concatenate with a new line separator
    # (only last max_lines lines)
    out_string = ''
    list_len = len(in_list)
    if max_lines == 0:  # in this case convert the wole list
        initial_line = 0
    else:
        if list_len > max_lines:
            # set initial line
            initial_line = list_len - max_lines
        else:
            initial_line = 0

    for s in in_list[initial_line:]:
        out_string += s + '\n'

    return out_string

def convert_list_to_oneline(in_list):
    # assuming input as list of strings, concatenate with a new line separator
    # (only last max_lines lines)
    out_string = ''

    for s in in_list:
        out_string += s + '\t'

    return out_string


def leftClick(e):
#    l.configure(text=f'Clicked left mouse button at {e.x},{e.y}')
    location = (e.x, e.y) # (x, y) location of the mouse
    row, col = get_row_col_from_mouse(location, SQ_SIZE)
    print(f"location:  row: {row}  col: {col}")

    player_clicks.append((row, col)) # append for first or second click

    print(player_clicks)    

    if len(player_clicks) == 2 and running.get(): # after the second click
        if player_clicks[0] == player_clicks[1]: # user clicked the same square twice, deselect
            player_clicks.clear()
            print(f'reselected the same position {row},{col}')
        else:
            # The move is defined: from_square, to_square
            move = (player_clicks[0], player_clicks[1]) 
            uci_move = coords_to_uci(player_clicks[0], player_clicks[1])
            # if quinning a pown ask for the selected quinning piece 
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
                display_queening_selection()
                print(f"Quinning piece: {queening_piece.get()}")
                uci_move += queening_piece.get()

            print(f"Move: {uci_move}")
            if uci_move in [move.uci() for move in board.legal_moves]:
                # Handle Legal Move
                board.push_uci(uci_move)
                display_changed[0] = True
                # Reset clicks for the next turn
                player_clicks.clear()
                # stockfish engine evaluation
                #info = engine.analyse(board, chess.engine.Limit(time=0.1))

                # TODO:
                # 1. Encapsulate in a function evalPosition()
                # 2. activale whenever the canvas is refresh, and display in in a textbox

                # -----------------------------------------------
                # skip the default analysis, it is done elsewhere
                # -----------------------------------------------

                # info = engine.analyse(board, chess.engine.Limit(time=2.0), multipv=3)

                #print("Score:", info["score"]) 
                # for line in info:
                #     # Extract structural components
                #     score = line["score"].white()  # Score from White's viewpoint
                #     depth = line["depth"]
                #     pv_moves = line["pv"]          # Principal Variation (predicted line of moves)
                    
                #     # Format evaluation string (Handle checkmates vs centipawns)
                #     if score.is_mate():
                #         eval_str = f"Mate in {abs(score.mate())}"
                #     else:
                #         eval_str = f"Score: {score.score() / 100:+.2f}"
                    
                #     # Convert moves back to human-readable SAN notation (e.g., Bb5, Nf6)
                #     san_line = board.variation_san(pv_moves)
                    
                #     print(f"Depth: {depth} | {eval_str} | Line: {san_line}")
                                        
                # refresh the status message
                #status_text_message = f'Move: {uci_move} Score: {info["score"]}'
                #l.configure(text=status_text_message)

                #last_moves_message = f'Moves: {board.variation_san([chess.Move.from_uci(m) for m in board.move_stack])}'
                #print(last_moves_message)
            # Handle game over conditions
                if board.is_game_over():
                    running.set(False)
                    l.configure(text = f"Game over. Result: {board.result()}")
                    # Handle game over conditions
                    # change to Dialog Box
                    # print(f"Game over. Result: {board.result()}")
                    # if board.is_checkmate():
                    #     print("Checkmate!")
                    # elif board.is_stalemate():
                    #     print("Stalemate!")    
                    # x = input("Hit ENTER to continue")

            else:
                # Handle invalid move case
                print("Invalid move parsing from mouse clicks")
                player_clicks.clear()

    update_canvas()


def load_images():
    pieces = ['P', 'R', 'N', 'B', 'Q', 'K', 'p', 'r', 'n', 'b', 'q', 'k'] 
    pieces_file_names = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for i in range(len(pieces)):
        # Load and scale images, store in a dictionary (e.g., IMAGES)
        # Example: IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # IMAGES[pieces[i]] = pygame.transform.scale(pygame.image.load("images/" + pieces_file_names[i] + ".png"), (SQ_SIZE, SQ_SIZE))

        # using pillow library resize the image to (SQ_SIZE, SQ_SIZE)
        image = Image.open("images/" + pieces_file_names[i] + ".png").convert("RGBA")
#        resized_image = image.resize((SQ_SIZE, SQ_SIZE), Image.Resampling.NEAREST)
        resized_image = image.resize((SQ_SIZE, SQ_SIZE), Image.Resampling.LANCZOS)
#        IMAGES[pieces[i]] = PhotoImage(resized_image)
#        IMAGES[pieces[i]] = PhotoImage(file="images/" + pieces_file_names[i] + ".png")
        IMAGES[pieces[i]] = ImageTk.PhotoImage(resized_image)

# use canvas items like:
# canvas.create_rectangle(10, 10, 200, 50, fill='red', outline='blue')
# myimg = PhotoImage(file='pretty.png')
# canvas.create_image(10, 10, image=myimg, anchor='nw')

def draw_board():
    if is_reversed.get():
        colors = ["gray75", "white"] # Reversed Colors
        letters = 'HGFEDCBA'
        numbers = '12345678'
    else:
        colors = ["white", "gray75"] # Normal Colors
        letters = 'ABCDEFGH'
        numbers = '87654321'
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            w = NORMAL_BORDER_WIDTH
            if len(player_clicks) > 0:
                # when reversed - reverse the mapping
                if is_reversed.get():
                    if (7 - r,7 - c) == player_clicks[0]:
                        w = SELECTED_BORDER_WIDTH
                else:
                    if (r,c) == player_clicks[0]:
                        w = SELECTED_BORDER_WIDTH
            canvas.create_rectangle(c * SQ_SIZE, r * SQ_SIZE, c * SQ_SIZE + SQ_SIZE, r * SQ_SIZE + SQ_SIZE, fill=color, outline='blue', width = w)
    # draw letters 
    for c in range(DIMENSION):
        canvas.create_text(c * SQ_SIZE + 2,HEIGHT - 20, text=letters[c], anchor='nw', font='TkMenuFont', fill='red')
    # draw numbers
    for r in range(DIMENSION):
        canvas.create_text(2, r * SQ_SIZE + 2, text=numbers[r], anchor='nw', font='TkMenuFont', fill='red')

def draw_pieces():
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            square = chess.square(c, 7 - r) # Map (row, col) to algebraic notation
            piece = board.piece_at (square)
#            print(f"piece: {piece}")
            if piece:
#                    print(f"piece: {piece} will display at row: {r} col: {c}")
                # Draw the corresponding image from the IMAGES dictionary
                if is_reversed.get():
#                    screen.blit(IMAGES[str(piece)], pygame.Rect((7 - c) * SQ_SIZE, (7 - r) * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                    canvas.create_image((7 - c) * SQ_SIZE, (7 - r) * SQ_SIZE, image=IMAGES[str(piece)], anchor='nw')
                else:
#                    screen.blit(IMAGES[str(piece)], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                    canvas.create_image(c * SQ_SIZE, r * SQ_SIZE, image=IMAGES[str(piece)], anchor='nw')

#                    print(f"piece: {piece} will display at row: {r} col: {c}")
                    #user_input = input("After Draw Piece Want to continue: ")

def display_moves():
    # display last 24 moves on right pane
    full_san_history = get_san_move_stack(board.move_stack)
    out_s = convert_list_to_multiline(full_san_history,0)  # convert the wole list as we have a scroller
    out_hs = convert_list_to_oneline(full_san_history)
#   blit_multiline_text(screen, out_s, message_font, (200, 200, 200), 5 + WIDTH, 5)
    rtext.delete('1.0','end')
    rtext.insert('1.0',out_s)

    btext.delete('1.0','end')
    btext.insert('1.0',out_hs)

def evalPosition():
    # TODO:
    # 1. Encapsulate in a function evalPosition()
    # 2. activale whenever the canvas is refresh, and display in in a textbox

    b1text.delete('1.0','end')
    if analyse_board.get():
        b1text.insert('1.0','Stockfish Evaluation:\n')


        info = engine.analyse(board, chess.engine.Limit(time=0.2, depth=8), multipv=3)

        #print("Score:", info["score"]) 
        for line in info:
            # Extract structural components
            score = line["score"].white()  # Score from White's viewpoint
            depth = line["depth"]
            pv_moves = line["pv"]          # Principal Variation (predicted line of moves)
            
            # Format evaluation string (Handle checkmates vs centipawns)
            if score.is_mate():
                eval_str = f"Mate in {abs(score.mate())}"
            else:
                eval_str = f"Score: {score.score() / 100:+.2f}"
            
            # Convert moves back to human-readable SAN notation (e.g., Bb5, Nf6)
            san_line = board.variation_san(pv_moves)
            
            print(f"Depth: {depth} | {eval_str} | Line: {san_line}")
            b1text.insert('end',f"Depth: {depth} | {eval_str} | Line: {san_line}\n")



def update_canvas():
    draw_board()
    draw_pieces()
    if board.is_game_over():
        root.title(f"Chess Game    Game over. Result: {board.result()} {'REVERSED' if is_reversed.get() else 'NORMAL'}")
    else:
        root.title(f"Chess Game    {'White' if board.turn else 'Black'} turn {'REVERSED' if is_reversed.get() else 'NORMAL'}")
    display_moves()
    evalPosition()

def display_queening_selection():

    queen_peace_dic = {'Queen':'q','Rook':'r','Bishop':'b','Knight':'n'}        
    def dismiss ():
        print(f'Selected: {queen_peace_var.get()}')
        # set the global variable for queening:
        queening_piece.set(queen_peace_dic[queen_peace_var.get()])
        dlg.grab_release()
        dlg.destroy()

    dlg = Toplevel(root)
    dlg.title('Quinning Peace')
    dlg.geometry('350x100+100+400')
    dlgframe = ttk.Frame(dlg, padding=(3, 3, 3, 3))
    dlgframe.grid(column=0, row=0, sticky=(N, W, E, S))

    ttk.Label(dlgframe, text="Select a peace for quinning:  ").grid(column=1, row=1, sticky=W, pady=10)
    queen_peace_var = StringVar()
    queen_peace_var.set('Queen')
    queen_combo = ttk.Combobox(dlgframe, textvariable=queen_peace_var, values=('Queen', 'Rook', 'Bishop', 'Knight'),state=(['readonly'])).grid(column=2, row=1, sticky=W, pady=10)
    ttk.Button(dlgframe, text="Done", command=dismiss).grid(column=1,row=3,pady=10)
    dlg.protocol("WM_DELETE_WINDOW", dismiss) # intercept close button
    dlg.transient(root)   # dialog window is related to main
    dlg.wait_visibility() # can't grab until window appears, so we wait
    dlg.grab_set()        # ensure all input goes to our window
    dlg.wait_window()     # block until window is destroyed


# Menu
# win = Toplevel(root)
# menubar = Menu(win)
# win['menu'] = menubar

menubar = Menu(root)
root['menu'] = menubar


def newFile():
    print("New File")

def openFile():
    print("Open File")

def closeFile():
    print("Close File")

def exitGame():
    print("Exiting")
    engine.quit()
    root.destroy()

def reset_game():
    running.set(True)
    board.reset()
    update_canvas()

def reverseBoard():
    is_reversed.set(not is_reversed.get())
    update_canvas()

def backword_move():
    print("Backword Move...")
    if len(board.move_stack) > 0 and running.get():
        board.pop()
        update_canvas()
    else:
        messagebox.showinfo(message="Backword not available")
#        print("Backword not available")

def engine_move():
    if running.get():
        result = engine.play(board, chess.engine.Limit(time=0.1))
        board.push(result.move)
        update_canvas()
    else:
        messagebox.showinfo(message="Engine Move not available")


def save_game():
    print("Save Game")
    # Open the file dialog and get the selected file path
    file_path = filedialog.asksaveasfilename(
        initialdir=".",  # Optional: specify initial directory
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

#================================================================
# select game from multiple pgn:
def convert_text_to_multiline(in_text, max_line_length):
    out_string = in_text[0:max_line_length]
    end_line = max_line_length
    while end_line < len(in_text):
        out_string += '\n' + in_text[end_line:end_line + max_line_length]
        end_line += max_line_length
    
    return out_string

def load_selected_game():
    game_r.clear()
    game_r.append(game[0])
#            print(game_r[0])
    game_r_current_move[0] = 0

    load_selected_game_header()

    game_r_moves.clear()
    for move in game_r[0].mainline_moves():
        game_r_moves.append(move)
    # Iterate through all moves and play them on a board.
    board.reset()
#            board.set_board_fen(Initial_FEN[0])
    for move in game_r[0].mainline_moves():
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
    sh = f' {game_r[0].headers["Event"]} {game_r[0].headers["Site"]}  {game_r[0].headers["Date"]} {game_r[0].headers["White"]} ({game_r[0].headers["WhiteElo"]})  {game_r[0].headers["Black"]} ({game_r[0].headers["BlackElo"]}) {game_r[0].headers["Result"]}'
# >>>
#            blit_multiline_text(screen, sh, message_font, (200,200,200), 5, HEIGHT + 230)  

    # draw the game
# >>>
#            blit_multiline_text(screen, s, message_font, (200,200,200), 5, HEIGHT + 260)  

    #try iterating through mainline moves:
    # game_r_iter = iter(game_r.mainline_moves())
    # for i in range(10):
    #     move = next(game_r_iter)
    #     print(f"{i} {move}")
# >>>
#            display_changed[0] = True

def load_selected_game_header():
#    sh = f' {game_r[0].headers["Event"]} {game_r[0].headers["Site"]}  {game_r[0].headers["Date"]} {game_r[0].headers["White"]} ({game_r[0].headers["WhiteElo"]})  {game_r[0].headers["Black"]} ({game_r[0].headers["BlackElo"]}) {game_r[0].headers["Result"]}'
    sh = f' {game_r[0].headers["White"]} ({game_r[0].headers["WhiteElo"]})   {game_r[0].headers["Black"]} ({game_r[0].headers["BlackElo"]})    {game_r[0].headers["Result"]} \n  {game_r[0].headers["Date"]} {game_r[0].headers["Event"]} {game_r[0].headers["Site"]}  '
    h_label_text.set(sh)



def select_game():
    # Create the game selection window
    r = Toplevel(root)
    r.title("Select Game")
    r.geometry("600x800") # sets the window size (width x height)

    game.clear()
    is_reversed = BooleanVar(value=False)

    def itemSelected(*args):
        idxs = lbox.curselection()
        if len(idxs)==1:
            idx = int(idxs[0])
            game.append(games[idx])
            print(f"Selected game at index {idx}")
#            print(f"Loading game {game.headers['Event']}")
            load_selected_game()

            r.grab_release()
            r.destroy()

    def reverseChanged(*args):
#        print(f"reverseButton state is {is_reversed.get()}")
        games.reverse()
        games_headers.reverse()
        choicesvar.set(games_headers)

    dlgframe = ttk.Frame(r, padding=(3, 3, 3, 3))
    dlgframe.grid(column=0, row=0, sticky=(N, W, E, S))
    label = Label(dlgframe, text=f"Select a game from the list ({len(games_headers)}) ").grid(column=1, row=1, sticky=W, pady=10)
    # reverse check button
    checkReverse = ttk.Checkbutton(dlgframe, text='Reverse List', 
	    command=reverseChanged, variable=is_reversed).grid(column=1, row=2, sticky=W, pady=10)

    # Display the games list:
    choicesvar = StringVar(value=games_headers)
    lbox = Listbox(dlgframe, listvariable=choicesvar, width=100,height=400) 
    lbox.grid(column=1, row=3, sticky=W, pady=10)
    lbox.bind('<<ListboxSelect>>', itemSelected)

#    r.protocol("WM_DELETE_WINDOW", itemSelected) # intercept close button
    r.transient(root)   # dialog window is related to main
    r.wait_visibility() # can't grab until window appears, so we wait
    r.grab_set()        # ensure all input goes to our window
    r.wait_window()     # block until window is destroyed


def load_games():
    print("Load Games")

    games.clear()
    games_headers.clear()

    # Open the file dialog and get the selected file path
    file_path = filedialog.askopenfilename(
        initialdir=".",  # Optional: specify initial directory
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

        except:
            print("Unable to parse the game")

# Handle game control buttons:

def game_reset():
    print("game_reset")
    game_r_current_move[0] = 0
    board.reset()
    display_changed[0] = True
    update_canvas()

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

    update_canvas()


# load board from fen string
# 1r1k4/p1p5/3p4/8/8/4P3/5P2/2K2R2 w - - 0 1
# 1r1k4/p1p5/3p4/8/8/4P3/5P2/2K2R2 b - - 0 1
# quinning:
# 8/2k3P1/8/8/8/8/2K4p/8 w - - 0 1

def load_board_from_FEN():
    def dismiss ():
        fen_text = FEN_var.get()
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
            # shold be blobal and loaded to board
#            FEN_var.set(fen_text)
            running.set(True)
            board.clear()
            board.set_fen(fen_text)
            update_canvas()

        dlg.grab_release()
        dlg.destroy()

    dlg = Toplevel(root)
    dlg.title('Load Board  from FEN')
    dlg.geometry('500x100+100+400')
    dlgframe = ttk.Frame(dlg, padding=(3, 3, 3, 3))
    dlgframe.grid(column=0, row=0, sticky=(N, W, E, S))

    ttk.Label(dlgframe, text="FEN string: ").grid(column=0, row=0, sticky=W, pady=10)
    FEN_var = StringVar()
    FEN_var.set('')
    text_FEN = Entry(dlgframe,textvariable=FEN_var,width=60)
    text_FEN.grid(column=1,row=0,sticky=W,pady=5)
    ttk.Button(dlgframe, text="Done", command=dismiss).grid(column=1,row=1,pady=10)
    dlg.protocol("WM_DELETE_WINDOW", dismiss) # intercept close button
    dlg.transient(root)   # dialog window is related to main
    dlg.wait_visibility() # can't grab until window appears, so we wait
    dlg.grab_set()        # ensure all input goes to our window
    dlg.wait_window()     # block until window is destroyed






#================================================================


menu_file = Menu(menubar)
menu_game = Menu(menubar)
menu_rgame = Menu(menubar)
menubar.add_cascade(menu=menu_file, label='File')
menubar.add_cascade(menu=menu_game, label='Game')
menubar.add_cascade(menu=menu_rgame, label='Replay Game')

menu_file.add_command(label='New', command=newFile)
menu_file.add_command(label='Open...', command=openFile)
menu_file.add_command(label='Close', command=closeFile)
menu_file.add_command(label='Save...', command=save_game)
menu_file.add_command(label='Exit', command=exitGame)

menu_game.add_command(label="Reverse Board", command=reverseBoard)
menu_game.add_command(label="Move Back", command=backword_move)
menu_game.add_command(label="Engine Move", command=engine_move)
menu_game.add_command(label="Reset Game", command=reset_game)

menu_rgame.add_command(label="Load Games", command=load_games)
menu_rgame.add_command(label="Select Game", command=select_game)
menu_rgame.add_separator()
menu_rgame.add_command(label="Reset Selected Game", command=game_reset)
menu_rgame.add_command(label="Move Selected Game", command=game_move)
menu_rgame.add_command(label="Move Back Selected Game", command=game_move_back)
menu_rgame.add_command(label="Move End Selected Game", command=game_end)
menu_rgame.add_separator()
menu_rgame.add_command(label="Load Board from FEN", command=load_board_from_FEN)

# gameButtons:
engine_button = ttk.Button(gameButtons, text='Engine Move', command=engine_move)
engine_button.grid(column=0,row=0)
back_button = ttk.Button(gameButtons, text='Backword', command=backword_move)
back_button.grid(column=1,row=0)
reverse_button = ttk.Button(gameButtons, text='Reverse Board', command= reverseBoard)
reverse_button.grid(column=2,row=0)
reset_button = ttk.Button(gameButtons, text='Reset Game', command=reset_game)
reset_button.grid(column=3,row=0)
# engine_button = ttk.Button(gameButtons, text='Engine', command=engine_move)
# engine_button.grid(column=0,row=0)

game_reset_button = ttk.Button(gameButtons, text=' << ', command=game_reset)
game_reset_button.grid(column=4,row=0)
game_move_button = ttk.Button(gameButtons, text='  > ', command=game_move)
game_move_button.grid(column=5,row=0)
game_move_back_button = ttk.Button(gameButtons, text='  < ', command=game_move_back)
game_move_back_button.grid(column=6,row=0)
game_end_button = ttk.Button(gameButtons, text=' >> ', command=game_end)
game_end_button.grid(column=7,row=0)

analyse_cbutton = ttk.Checkbutton(gameButtons,text='Analyse',variable=analyse_board,onvalue=True,offvalue=False)
analyse_cbutton.grid(column=8,row=0)

# bind leftClick for moving

canvas.bind('<ButtonPress-1>', leftClick)

# bind root window closing
root.protocol("WM_DELETE_WINDOW", exitGame)

# initialize:
load_images()
#update_canvas()
reset_game()

root.mainloop()

