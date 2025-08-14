from PIL import Image, ImageDraw
import chess
import os

# Path to your assets folder
ASSET_PATH = os.path.join(os.path.dirname(__file__), "assets")

# Draw a chess board and pieces from a python-chess board object
def draw_board(board, square_size=80):
    board_size = 8 * square_size
    light = (240, 217, 181)
    dark = (181, 136, 99)

    # Create blank image
    img = Image.new("RGB", (board_size, board_size), "white")
    draw = ImageDraw.Draw(img)

    # Draw squares
    for rank in range(8):
        for file in range(8):
            color = light if (rank + file) % 2 == 0 else dark
            top_left = (file * square_size, (7 - rank) * square_size)
            bottom_right = ((file + 1) * square_size, (8 - rank) * square_size)
            draw.rectangle([top_left, bottom_right], fill=color)

    # Place pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_symbol = piece.symbol()
            file = chess.square_file(square)
            rank = chess.square_rank(square)

            piece_file = os.path.join(ASSET_PATH, f"{'w' if piece_symbol.isupper() else 'b'}{piece_symbol.upper()}.png")
            if os.path.exists(piece_file):
                piece_img = Image.open(piece_file).resize((square_size, square_size), Image.Resampling.LANCZOS)
                x = file * square_size
                y = (7 - rank) * square_size
                img.paste(piece_img, (x, y), piece_img.convert("RGBA"))

    return img
