import chess
import chess.engine
import asyncio

# stockfish async run example:

async def main():
    # Provide the exact path to your Stockfish executable
    engine_path = r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe" # Example path
    
    # Start the engine process
    transport, engine = await chess.engine.popen_uci(engine_path)

    board = chess.Board()
    # Play a game
    while not board.is_game_over():
        # Get the best move within a time limit (e.g., 0.1 seconds)
        result = await engine.play(board, chess.engine.Limit(time=0.1))
        board.push(result.move)
        #print(f"Board position: {board.fen()}")

    # Analyze the final position
    info = await engine.analyse(board, chess.engine.Limit(depth=20))
    print(f"Final score: {info['score']}")
    print(board)

    print(f"Game over. Result: {board.result()}")
    if board.is_checkmate():
        print("Checkmate!")
    elif board.is_stalemate():
        print("Stalemate!")    


    # Quit the engine process
    await engine.quit()

# Run the asynchronous function
asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())
asyncio.run(main())

# end of stockfish
