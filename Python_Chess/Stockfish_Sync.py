import chess
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci(r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")

board = chess.Board()
while not board.is_game_over():
    result = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(result.move)

print(board)

print(f"Game over. Result: {board.result()}")
if board.is_checkmate():
    print("Checkmate!")
elif board.is_stalemate():
    print("Stalemate!")    

engine.quit()

