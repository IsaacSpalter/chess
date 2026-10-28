import pygame
import chess
import chess.engine
import asyncio

import pygame_widgets
from pygame_widgets.textbox import TextBox

#screen = pygame.display.set_mode((640, 480))
#clock = pygame.time.Clock()

pygame.init()

# text display fonts
big_font = pygame.font.SysFont(None, 48) # Use default font, size 48
# or use a specific system font (check availability first)
message_font = pygame.font.SysFont('Arial', 16)
coord_font = pygame.font.SysFont('Arial', 14)
button_font = pygame.font.SysFont('Arial', 18)

WIDTH = HEIGHT = 512 # You can choose a different size
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # For animations
#MAX_FPS = 60 # For animations
BOTTOM_MARGIN = 200
RIGHT_MARGIN = 100
screen = pygame.display.set_mode((WIDTH + RIGHT_MARGIN, HEIGHT + BOTTOM_MARGIN))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()
screen.fill(pygame.Color("white"))

background = pygame.Surface(screen.get_size())
background.fill((0, 0, 0)) # Black


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
#            print(f"piece: {piece}")
            if piece:
                if is_reversed[0]:
                    r = 7 - r
                    c = 7 - c
#                    print(f"piece: {piece} will display at row: {r} col: {c}")
                # Draw the corresponding image from the IMAGES dictionary
                screen.blit(IMAGES[str(piece)], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

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


# Button Class

# Define colors
COLOR_NORMAL = (100, 100, 100)
COLOR_HOVER = (150, 150, 150)
COLOR_CLICK = (200, 200, 200)
TEXT_COLOR = (255, 255, 255)

class Button():
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = COLOR_NORMAL
        self.font = button_font
        self.text_surface = self.font.render(text, True, TEXT_COLOR)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        # Update color on hover
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.color = COLOR_HOVER
        else:
            self.color = COLOR_NORMAL
            
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.color = COLOR_CLICK # Optional visual feedback
                self.action() # Call the associated function

# Example function to link to the button
def backword_move():
    print("Backword Move...")
    if len(board.move_stack) > 0:
        board.pop()
    else:
        print("Backword not available")

def engine_move():
    result = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(result.move)

def reverse_display():
    is_reversed[0] = not is_reversed[0]

def text_input():
    fen_text = textbox.getText()
    print(fen_text)
    # try to load the game
    board.set_fen(fen_text)

    textbox.setText('')

# create a text box for text input
textbox = TextBox(screen, 5, HEIGHT + 100, WIDTH - 5, 40, font = message_font, fontSize=16,
                borderColour=(200, 200, 200), textColour=(0, 0, 0),
                onSubmit=text_input, radius=2, borderThickness=2)

# Your multi-line text using triple quotes or explicit '\n'
multitext = """Hello World!
Goodbye World!
I'm back World!"""

def blit_multiline_text(surface, text, font, color, x, y):
    """Helper function to render and blit multi-line text."""
    # Get the height of a single line of text for correct spacing
    line_height = font.get_linesize()
    lines = text.splitlines() # Splits the string by newline characters

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

def get_san_move_stack(board_history):
    # Start from a fresh board (or the game's initial FEN if different)
    temp_board = chess.Board() 
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




# ==================================================
# Create a new board instance
# the board is global to allow Button class access

board = chess.Board()

# load stockfish engine
# This is bloabal to allow button access
engine = chess.engine.SimpleEngine.popen_uci(r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")

# Reversed Display indication
is_reversed = [False]

def main():
    # Create a new board instance
    #board = chess.Board()
    print("Welcome to Python Chess! Enter moves in UCI format (e.g., e2e4)")

    # Create the buttons
    back_button = Button(5, HEIGHT + 25, 100, 40, "Back", backword_move)
    engine_move_button = Button(115, HEIGHT + 25, 100, 40, "Engine", engine_move)
    reverse_button = Button(225, HEIGHT + 25, 100, 40, "Reverse", reverse_display)



    # load stockfish engine
    #engine = chess.engine.SimpleEngine.popen_uci(r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")


    # draw pygame board
    load_images()

    pygame.display.set_caption(f"Chess Game    {'White' if board.turn else 'Black'} turn {'REVERSED' if is_reversed[0] else 'NORMAL'}")

    screen.fill((0,0,0))
    draw_board(screen)
    draw_pieces(screen, board)

#    screen.blit(text_input.surface, (5, HEIGHT + 5))
   # example of text box draing:
    status_text_message = "Initial Game"
    draw_text(screen,status_text_message,message_font,
               (5, HEIGHT + 5))
    # Draw all buttons
    back_button.draw(screen)
    engine_move_button.draw(screen)
    reverse_button.draw(screen)
    pygame.display.flip()
    clock.tick(MAX_FPS)


 


    running = True
    player_clicks = [] # list of two (row, col) tuples

    while running: 
        # and not board.is_game_over():
        sq_selected = () # keeps track of the last click (row, col)
 
        events = pygame.event.get()

        # check widget events
        pygame_widgets.update(events)
        pygame.display.update()


        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # Check for button clicks
            back_button.check_click(event)
            engine_move_button.check_click(event)
            reverse_button.check_click(event)

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
                    print(f"Move: {uci_move}")
                    if uci_move in [move.uci() for move in board.legal_moves]:
                        # Handle Legal Move
                        board.push_uci(uci_move)
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
        else:
            pygame.display.set_caption(f"Chess Game    {'White' if board.turn else 'Black'} turn {'REVERSED' if is_reversed[0] else 'NORMAL'}")

        # refresh the display
        # screen.fill((0,0,0))
        draw_board(screen)
        draw_pieces(screen, board)
        # example of text box draing:
        draw_text(screen,status_text_message,message_font,
                (5, HEIGHT + 5))
        # display last 24 moves on right pane
        full_san_history = get_san_move_stack(board.move_stack)
        out_s = convert_list_to_multiline(full_san_history,24)
        blit_multiline_text(screen, out_s, message_font, (200, 200, 200), 5 + WIDTH, 5)


        # Draw all buttons
        back_button.draw(screen)
        engine_move_button.draw(screen)
        reverse_button.draw(screen)
#        pygame.display.flip()
        pygame.display.update()
        clock.tick(MAX_FPS)

    # end of while running main loop



    # Handle game over conditions
    print(f"Game over. Result: {board.result()}")
    if board.is_checkmate():
        print("Checkmate!")
    elif board.is_stalemate():
        print("Stalemate!")    

#    user_input = input("Want to continue: ")

    engine.quit()



if __name__ == "__main__":
    main()