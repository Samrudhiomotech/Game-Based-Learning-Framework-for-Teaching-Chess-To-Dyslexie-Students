import streamlit as st
import chess
import chess.engine
import random
from PIL import Image, ImageDraw, ImageFont
import sys
import asyncio
import io
import os

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# === CONFIGURATION ===
STOCKFISH_PATH = r"C:\Users\omote\Desktop\stockfish\stockfish.exe"
PIECE_FOLDER = "assets"

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Chess Puzzle - 2 Pieces Battle",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === SESSION STATE INITIALIZATION ===
if "fen" not in st.session_state:
    st.session_state.fen = None
if "game_history" not in st.session_state:
    st.session_state.game_history = []
if "wins" not in st.session_state:
    st.session_state.wins = {"human": 0, "computer": 0, "draws": 0}
if "current_move_arrows" not in st.session_state:
    st.session_state.current_move_arrows = []
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Medium"
if "current_game_moves" not in st.session_state:
    st.session_state.current_game_moves = 0
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "puzzle_start_time" not in st.session_state:
    st.session_state.puzzle_start_time = None

# === COMPACT CSS STYLING ===
st.markdown("""
<style>
/* Main background and typography */
html, body, .stApp {
    background: linear-gradient(135deg, #9FEDD7 0%, #B8F2E6 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #026670;
    margin: 0;
    padding: 0;
}

/* Remove default padding and margins */
.block-container {
    padding: 0.5rem 1rem;
    max-width: 100vw;
    margin: 0;
    background: rgba(237, 234, 229, 0.95);
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* Compact typography */
h1 {
    font-size: 1.5rem;
    text-align: center;
    margin: 0.2rem 0;
    color: #026670;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

h2, h3 {
    font-size: 1.2rem;
    margin: 0.3rem 0;
    color: #026670;
}

/* Compact button styling */
.stButton > button {
    background: linear-gradient(45deg, #FCE181, #FEF9C7);
    color: #026670;
    border-radius: 8px;
    padding: 4px 8px;
    font-weight: bold;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(252, 225, 129, 0.4);
    width: 100%;
    font-size: 0.8rem;
    height: 35px;
    margin: 2px 0;
}

.stButton > button:hover {
    background: linear-gradient(45deg, #FEF9C7, #FCE181);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(252, 225, 129, 0.6);
}

/* Compact sidebar */
.css-1d391kg {
    padding: 0.5rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #026670 0%, #024950 100%);
    width: 250px !important;
}

section[data-testid="stSidebar"] * {
    color: 	#26A69A !important;
    font-size: 0.85rem !important;
}

/* Compact board container */
.board-container {
    background: white;
    padding: 8px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    text-align: center;
    margin: 0 auto;
    max-width: 450px;
}

/* Compact game status */
.game-status {
    background: linear-gradient(135deg, #FCE181, #FEF9C7);
    padding: 8px;
    border-radius: 8px;
    text-align: center;
    margin: 8px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    font-size: 0.9rem;
}

/* Compact stats */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin: 8px 0;
}

.stat-item {
    background: rgba(255, 255, 255, 0.9);
    padding: 6px;
    border-radius: 6px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    font-size: 0.8rem;
}

.stat-value {
    font-size: 1.1rem;
    font-weight: bold;
    color: #026670;
}

/* Move suggestions grid */
.moves-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 4px;
    margin: 8px 0;
}

/* Compact metrics */
.metric-container {
    background: rgba(255, 255, 255, 0.8);
    padding: 4px 8px;
    border-radius: 6px;
    text-align: center;
    margin: 2px;
    font-size: 0.8rem;
}

/* Remove extra spacing */
.element-container {
    margin-bottom: 0.5rem !important;
}

.stMarkdown {
    margin-bottom: 0.3rem;
}

/* Compact selectbox */
.stSelectbox {
    margin-bottom: 0.5rem;
}

/* Footer styling */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(2, 102, 112, 0.9);
    color: white;
    text-align: center;
    padding: 5px;
    font-size: 0.7rem;
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)

# === LOAD STOCKFISH ENGINE ===
@st.cache_resource
def load_engine():
    if not os.path.exists(STOCKFISH_PATH):
        st.warning("⚠️ Stockfish not found. Using basic AI.")
        return None
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        return engine
    except Exception as e:
        st.warning(f"⚠️ Could not load Stockfish: {e}")
        return None

# === BASIC AI FALLBACK ===
def get_basic_ai_move(board):
    """Simple AI that prioritizes captures, then random moves"""
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
   
    # Prioritize captures
    captures = [move for move in legal_moves if board.is_capture(move)]
    if captures:
        return random.choice(captures)
   
    # Then checks
    checks = []
    for move in legal_moves:
        board_copy = board.copy()
        board_copy.push(move)
        if board_copy.is_check():
            checks.append(move)
    if checks:
        return random.choice(checks)
   
    # Random move
    return random.choice(legal_moves)

# === SCORING SYSTEM ===
def calculate_score(difficulty, moves, time_taken, result):
    """Calculate score based on performance"""
    base_scores = {"Easy": 10, "Medium": 20, "Hard": 35}
    base_score = base_scores[difficulty]
    
    # Bonus for fewer moves
    move_bonus = max(0, 20 - moves * 2)
    
    # Time bonus (faster = better)
    time_bonus = max(0, 30 - time_taken) if time_taken else 0
    
    # Result multiplier
    if result == "win":
        multiplier = 1.5
    elif result == "draw":
        multiplier = 0.8
    else:
        multiplier = 0.3
    
    total_score = int((base_score + move_bonus + time_bonus) * multiplier)
    return max(total_score, 1)

# === PUZZLE GENERATION ===
def generate_puzzle_fen(difficulty="Medium"):
    """Generate a 2-piece puzzle with varying difficulty"""
    piece_sets = {
        "Easy": [('Q', 'r'), ('R', 'q'), ('Q', 'b'), ('R', 'r')],
        "Medium": [('Q', 'n'), ('R', 'b'), ('B', 'q'), ('N', 'r')],
        "Hard": [('N', 'n'), ('B', 'b'), ('R', 'n'), ('Q', 'k')]
    }
   
    attempts = 0
    while attempts < 50:
        attempts += 1
        squares = random.sample(chess.SQUARES, 4)
        board = chess.Board(None)

        king_squares = [sq for sq in squares[:2] if chess.square_distance(squares[0], squares[1]) > 1]
        if len(king_squares) < 2:
            continue
           
        board.set_piece_at(king_squares[0], chess.Piece.from_symbol('K'))
        board.set_piece_at(king_squares[1], chess.Piece.from_symbol('k'))

        white_piece, black_piece = random.choice(piece_sets[difficulty])
        remaining_squares = [sq for sq in squares[2:] if sq not in king_squares]
       
        if len(remaining_squares) >= 2:
            board.set_piece_at(remaining_squares[0], chess.Piece.from_symbol(white_piece))
            board.set_piece_at(remaining_squares[1], chess.Piece.from_symbol(black_piece))
        else:
            continue

        board.turn = chess.WHITE

        if board.is_valid() and not board.is_checkmate() and not board.is_stalemate():
            return board.fen()
   
    return "8/8/8/3k4/8/3K4/3Q4/3r4 w - - 0 1"

# === OPTIMIZED BOARD DRAWING ===
def draw_board_with_arrows(board, move_arrows=None, suggested_moves=None):
    # Optimized sizes for perfect screen fit
    square_size = 45
    board_size = square_size * 8
    margin = 25
    img_size = board_size + 2 * margin
   
    img = Image.new("RGB", (img_size, img_size), "#9FEDD7")
    draw = ImageDraw.Draw(img)
   
    try:
        font_large = ImageFont.truetype("arial.ttf", 12)
        font_small = ImageFont.truetype("arial.ttf", 9)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    light_square = (254, 249, 199)
    dark_square = (252, 225, 129)
   
    # Draw squares with highlights
    for rank in range(8):
        for file in range(8):
            x = margin + file * square_size
            y = margin + (7 - rank) * square_size
           
            color = light_square if (rank + file) % 2 == 0 else dark_square
            draw.rectangle([x, y, x + square_size, y + square_size], fill=color)
           
            # Highlight suggested moves
            if suggested_moves:
                square = chess.square(file, rank)
                for move in suggested_moves:
                    if move.to_square == square:
                        draw.rectangle([x + 2, y + 2, x + square_size - 2, y + square_size - 2],
                                     outline="#026670", width=2)
                    elif move.from_square == square:
                        draw.rectangle([x + 2, y + 2, x + square_size - 2, y + square_size - 2],
                                     outline="#9FEDD7", width=2)
   
    # Draw pieces
    for rank in range(8):
        for file in range(8):
            piece = board.piece_at(chess.square(file, rank))
            if piece:
                x = margin + file * square_size
                y = margin + (7 - rank) * square_size
               
                color_prefix = 'w' if piece.color == chess.WHITE else 'b'
                piece_symbol = piece.symbol().upper()
                piece_path = f"{PIECE_FOLDER}/{color_prefix}{piece_symbol}.png"
               
                try:
                    piece_img = Image.open(piece_path).resize((square_size - 6, square_size - 6))
                    img.paste(piece_img, (x + 3, y + 3), piece_img if piece_img.mode == 'RGBA' else None)
                except:
                    piece_unicode = {
                        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
                        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
                    }
                    symbol = piece_unicode.get(piece.symbol(), piece.symbol())
                    draw.text((x + square_size//2 - 6, y + square_size//2 - 6),
                             symbol, fill="#026670", font=font_large)
   
    # Draw move arrows
    if move_arrows:
        for move in move_arrows:
            from_file = chess.square_file(move.from_square)
            from_rank = chess.square_rank(move.from_square)
            to_file = chess.square_file(move.to_square)
            to_rank = chess.square_rank(move.to_square)
           
            start_x = margin + from_file * square_size + square_size // 2
            start_y = margin + (7 - from_rank) * square_size + square_size // 2
            end_x = margin + to_file * square_size + square_size // 2
            end_y = margin + (7 - to_rank) * square_size + square_size // 2
           
            draw.line([(start_x, start_y), (end_x, end_y)], fill="#026670", width=3)
           
            import math
            angle = math.atan2(end_y - start_y, end_x - start_x)
            arrowhead_length = 8
            arrowhead_angle = math.pi / 6
           
            x1 = end_x - arrowhead_length * math.cos(angle - arrowhead_angle)
            y1 = end_y - arrowhead_length * math.sin(angle - arrowhead_angle)
            x2 = end_x - arrowhead_length * math.cos(angle + arrowhead_angle)
            y2 = end_y - arrowhead_length * math.sin(angle + arrowhead_angle)
           
            draw.polygon([(end_x, end_y), (x1, y1), (x2, y2)], fill="#026670")

    # Draw coordinates
    for i in range(8):
        draw.text((5, margin + (7 - i) * square_size + square_size//2 - 4),
                 str(i + 1), fill="#026670", font=font_small)
        draw.text((margin + i * square_size + square_size//2 - 2, img_size - 18),
                 chr(ord('a') + i), fill="#026670", font=font_small)

    return img

# === MAIN APP LAYOUT ===
st.title("♟️ Chess Puzzle: 2-Piece Battle")

# Initialize game if needed
if st.session_state.fen is None:
    st.session_state.fen = generate_puzzle_fen(st.session_state.difficulty)
    st.session_state.current_game_moves = 0
    import time
    st.session_state.puzzle_start_time = time.time()

board = chess.Board(st.session_state.fen)
engine = load_engine()

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### 🎯 Battle Control")
   
    # Difficulty selection
    st.session_state.difficulty = st.selectbox(
        "🎚️ Difficulty:",
        ["Easy", "Medium", "Hard"],
        index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty)
    )
   
    # Stats
    st.markdown("### 📊 Statistics")
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-item">
            <div class="stat-value">{st.session_state.wins['human']}</div>
            <div>🏆 Wins</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{st.session_state.wins['computer']}</div>
            <div>🤖 Losses</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{st.session_state.wins['draws']}</div>
            <div>🤝 Draws</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{st.session_state.total_score}</div>
            <div>⭐ Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
   
    st.markdown("---")
   
    # Game info
    st.markdown("### 📝 Current Game")
    st.markdown(f"**Moves:** {st.session_state.current_game_moves}")
    st.markdown(f"**Difficulty:** {st.session_state.difficulty}")
   
    # New puzzle button
    if st.button("🆕 New Puzzle", type="primary"):
        st.session_state.fen = generate_puzzle_fen(st.session_state.difficulty)
        st.session_state.current_move_arrows = []
        st.session_state.current_game_moves = 0
        import time
        st.session_state.puzzle_start_time = time.time()
        st.rerun()
   
    st.markdown("---")
   
    # Instructions
    st.markdown("### 📖 Rules")
    st.markdown("""
    **🟡 You are WHITE**
    - Click move buttons
    - Capture or checkmate!
   
    **⚫ AI is BLACK**  
    - Moves automatically
   
    **🎯 Win Conditions:**
    - Checkmate ♔
    - Capture pieces ⚔️
    - Force stalemate 🤝
    """)

# === MAIN GAME AREA ===
col1, col2 = st.columns([3, 2])

with col1:
    # Board display
    st.markdown('<div class="board-container">', unsafe_allow_html=True)
    current_arrows = st.session_state.current_move_arrows
    board_image = draw_board_with_arrows(board, current_arrows)
    st.image(board_image, width=400)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Game status
    st.markdown('<div class="game-status">', unsafe_allow_html=True)
   
    if board.is_game_over():
        result = board.result()
        outcome = board.outcome()
       
        # Calculate and add score
        import time
        time_taken = time.time() - st.session_state.puzzle_start_time if st.session_state.puzzle_start_time else 0
       
        if outcome.winner == chess.WHITE:
            st.success("🏆 **YOU WIN!**")
            game_score = calculate_score(st.session_state.difficulty, st.session_state.current_game_moves, time_taken, "win")
            st.session_state.wins["human"] += 1
            st.session_state.total_score += game_score
            st.success(f"**+{game_score} points!**")
        elif outcome.winner == chess.BLACK:
            st.error("🤖 **AI WINS!**")
            game_score = calculate_score(st.session_state.difficulty, st.session_state.current_game_moves, time_taken, "loss")
            st.session_state.wins["computer"] += 1
            st.session_state.total_score += game_score
            st.info(f"**+{game_score} points**")
        else:
            st.warning("🤝 **DRAW!**")
            game_score = calculate_score(st.session_state.difficulty, st.session_state.current_game_moves, time_taken, "draw")
            st.session_state.wins["draws"] += 1
            st.session_state.total_score += game_score
            st.info(f"**+{game_score} points**")
       
        st.markdown(f"**Result:** {result}")
        st.markdown(f"**Moves:** {st.session_state.current_game_moves}")
        st.markdown(f"**Time:** {time_taken:.1f}s")
       
    else:
        turn_player = "Your Turn 🟡" if board.turn == chess.WHITE else "AI Turn 🤖"
        st.info(f"**{turn_player}**")
       
        if board.is_check():
            st.warning("⚠️ **CHECK!**")
       
        st.markdown(f"**Moves:** {st.session_state.current_game_moves}")
   
    st.markdown('</div>', unsafe_allow_html=True)

    # Current game metrics
    if not board.is_game_over():
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="metric-container">
                <div class="stat-value">{len(list(board.legal_moves))}</div>
                <div>Legal Moves</div>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            material_balance = 0
            piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9}
            for piece_type, value in piece_values.items():
                white_count = len(board.pieces(chess.Piece.from_symbol(piece_type.upper()).piece_type, chess.WHITE))
                black_count = len(board.pieces(chess.Piece.from_symbol(piece_type).piece_type, chess.BLACK))
                material_balance += (white_count - black_count) * value
            
            st.markdown(f"""
            <div class="metric-container">
                <div class="stat-value">{material_balance:+d}</div>
                <div>Material</div>
            </div>
            """, unsafe_allow_html=True)

# === MOVE SUGGESTIONS ===
if board.turn == chess.WHITE and not board.is_game_over():
    st.markdown("### 💡 Your Move Options")
   
    try:
        if engine:
            depth_map = {"Easy": 8, "Medium": 12, "Hard": 16}
            depth = depth_map[st.session_state.difficulty]
            suggestions = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=3)
            moves_to_show = [result["pv"][0] for result in suggestions]
        else:
            legal_moves = list(board.legal_moves)
            moves_to_show = random.sample(legal_moves, min(3, len(legal_moves)))
       
        # Display moves in compact grid
        cols = st.columns(3)
       
        for i, move in enumerate(moves_to_show):
            with cols[i]:
                move_desc = f"{chess.square_name(move.from_square)}-{chess.square_name(move.to_square)}"
               
                # Add move type icons
                if board.is_capture(move):
                    move_desc += " ⚔️"
                elif board.gives_check(move):
                    move_desc += " ⚠️"
               
                if st.button(move_desc, key=f"move_{i}"):
                    # Show move arrow
                    st.session_state.current_move_arrows = [move]
                   
                    # Execute move
                    board.push(move)
                    st.session_state.fen = board.fen()
                    st.session_state.current_game_moves += 1
                   
                    # AI response
                    if not board.is_game_over():
                        try:
                            if engine:
                                depth_map = {"Easy": 6, "Medium": 10, "Hard": 14}
                                ai_depth = depth_map[st.session_state.difficulty]
                                ai_result = engine.analyse(board, chess.engine.Limit(depth=ai_depth))
                                ai_move = ai_result["pv"][0]
                            else:
                                ai_move = get_basic_ai_move(board)
                           
                            if ai_move:
                                board.push(ai_move)
                                st.session_state.fen = board.fen()
                                st.session_state.current_game_moves += 1
                                st.session_state.current_move_arrows = [ai_move]
                        except Exception as e:
                            st.error(f"AI Error: {e}")
                   
                    st.rerun()
                   
    except Exception as e:
        st.error(f" Analysis Error: {e}")
        # Fallback to simple moves
        legal_moves = list(board.legal_moves)[:3]
        cols = st.columns(3)
       
        for i, move in enumerate(legal_moves):
            with cols[i]:
                if st.button(f"{move.uci()}", key=f"fallback_{i}"):
                    board.push(move)
                    st.session_state.fen = board.fen()
                    st.session_state.current_game_moves += 1
                   
                    if not board.is_game_over():
                        ai_move = get_basic_ai_move(board)
                        if ai_move:
                            board.push(ai_move)
                            st.session_state.fen = board.fen()
                            st.session_state.current_game_moves += 1
                   
                    st.rerun()

# === FOOTER ===
st.markdown("""
<div class="footer">
    🎯 Master tactical chess skills through 2-piece battles! Each puzzle challenges your strategic thinking.
</div>
""", unsafe_allow_html=True)