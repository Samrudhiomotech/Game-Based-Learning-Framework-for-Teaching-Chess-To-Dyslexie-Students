import asyncio
import sys
import os
import threading
import time
import requests

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import chess
import chess.engine
import pyttsx3
from PIL import Image, ImageDraw, ImageFont

# Parameters
STOCKFISH_TIME_LIMIT = 0.1
COMPUTER_MOVE_DELAY = 0.2

# Page Config
st.set_page_config(page_title="Adaptive Chess Learning", page_icon="♟", layout="centered")

# Enhanced Theme with improved button styling
st.markdown("""
<style>
/* Main background and typography */
html, body, .stApp {
    background: linear-gradient(135deg, #9FEDD7 0%, #B8F2E6 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #026670;
}

/* Main container styling */
.block-container {
    padding: 2rem;
    max-width: 1200px;
    margin: auto;
    background: rgba(237, 234, 229, 0.95);
    border-radius: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Typography improvements */
h1, h2, h3 {
    color: #026670;
    text-align: center;
    margin-bottom: 1rem;
}

h1 {
    font-size: 2.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

/* Image styling */
img {
    border-radius: 15px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

img:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

/* Main button styling */
.stButton > button {
    background: linear-gradient(45deg, #FCE181, #FEF9C7);
    color: #026670;
    border-radius: 15px;
    padding: 12px 24px;
    font-weight: bold;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(252, 225, 129, 0.4);
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(45deg, #FEF9C7, #FCE181);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(252, 225, 129, 0.6);
}

/* Suggestion button styling */
.suggestion-buttons {
    display: flex;
    gap: 10px;
    margin: 10px 0;
    flex-wrap: wrap;
}

.suggestion-button {
    background: linear-gradient(45deg, #B8F2E6, #9FEDD7);
    color: #026670;
    border: 2px solid #026670;
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
    min-width: 80px;
    box-shadow: 0 3px 10px rgba(2, 102, 112, 0.2);
}

.suggestion-button:hover {
    background: linear-gradient(45deg, #9FEDD7, #B8F2E6);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(2, 102, 112, 0.3);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #026670 0%, #024950 100%);
}

section[data-testid="stSidebar"] * {
    color: #00BFA5 !important;
}

/* Game message styling */
.game-message {
    background: linear-gradient(135deg, #FCE181, #FEF9C7);
    color: #026670;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}

/* Turn indicator styling */
.turn-indicator {
    background: linear-gradient(45deg, #026670, #024950);
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
    box-shadow: 0 4px 15px rgba(2, 102, 112, 0.3);
}

/* Move history styling */
.move-history {
    background: rgba(255, 255, 255, 0.9);
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
    max-height: 200px;
    overflow-y: auto;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}

/* Input styling */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.9);
    border: 2px solid #B8F2E6;
    border-radius: 10px;
    color: #DAA520;
    font-weight: 500;
}

.stTextInput > div > div > input:focus {
    border-color: #FCE181;
    box-shadow: 0 0 10px rgba(252, 225, 129, 0.5);
    color: #B8860B;
}

.stTextInput > div > div > input::placeholder {
    color: #DAA520;
    opacity: 0.8;
}

/* Success/Error message styling */
.stSuccess {
    background: linear-gradient(45deg, #9FEDD7, #B8F2E6);
    color: #026670;
    border-radius: 10px;
    border: none;
}

.stError {
    background: linear-gradient(45deg, #FFB3BA, #FFDFBA);
    color: #8B0000;
    border-radius: 10px;
    border: none;
}

.stInfo {
    background: linear-gradient(45deg, #BFEFFF, #E0F6FF);
    color: #026670;
    border-radius: 10px;
    border: none;
}

.stWarning {
    background: linear-gradient(45deg, #FFEB9C, #FFF2CC);
    color: #8B4513;
    border-radius: 10px;
    border: none;
}

/* Developer credit styling */
.developer-credit {
    text-align: center;
    margin-top: 20px;
    padding: 15px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    backdrop-filter: blur(5px);
}

/* Statistics styling */
.game-stats {
    background: rgba(255, 255, 255, 0.8);
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "board" not in st.session_state:
    st.session_state.board = chess.Board()

if "tts_engine" not in st.session_state:
    st.session_state.tts_engine = pyttsx3.init()
    st.session_state.speaking_lock = threading.Lock()

if "stockfish" not in st.session_state:
    stockfish_path = r"C:\\Users\\omote\\Desktop\\stockfish\\stockfish.exe"
    if not os.path.exists(stockfish_path):
        st.error(f"Stockfish not found at {stockfish_path}")
        st.stop()
    st.session_state.stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)

if "game_message" not in st.session_state:
    st.session_state.game_message = ""

if "player_white" not in st.session_state:
    st.session_state.player_white = "Human"

if "player_black" not in st.session_state:
    st.session_state.player_black = "Computer"

if "auto_play" not in st.session_state:
    st.session_state.auto_play = True

if "move_history" not in st.session_state:
    st.session_state.move_history = []

if "game_stats" not in st.session_state:
    st.session_state.game_stats = {"moves_played": 0, "captures": 0, "checks": 0}

# ADD THIS: Flag to track when computer should play
if "computer_should_play" not in st.session_state:
    st.session_state.computer_should_play = False

board = st.session_state.board
tts_engine = st.session_state.tts_engine
speaking_lock = st.session_state.speaking_lock
stockfish = st.session_state.stockfish

@st.cache_resource
def load_piece_images():
    pieces = {}
    colors = ['w', 'b']
    types = ['p', 'r', 'n', 'b', 'q', 'k']
    for color in colors:
        for t in types:
            path = f'assets/{color}{t}.png'
            if os.path.exists(path):
                pieces[color + t] = Image.open(path).resize((64, 64), Image.Resampling.LANCZOS)
            else:
                st.error(f"Missing piece image: {path}")
                st.stop()
    return pieces

piece_images = load_piece_images()

def draw_board(board):
    SQUARE_SIZE = 64
    BOARD_SIZE = 8 * SQUARE_SIZE
    MARGIN = 50
    TOTAL_SIZE = BOARD_SIZE + MARGIN
    light_color = (240, 217, 181)
    dark_color = (181, 136, 99)
    background_color = (2, 102, 112)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    img = Image.new('RGB', (TOTAL_SIZE, TOTAL_SIZE), background_color)
    draw = ImageDraw.Draw(img)
    
    # Draw squares
    for row in range(8):
        for col in range(8):
            square_color = light_color if (row + col) % 2 == 0 else dark_color
            x1 = MARGIN + col * SQUARE_SIZE
            y1 = row * SQUARE_SIZE
            draw.rectangle([x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE], fill=square_color)
    
    # Highlight last move if available
    if board.move_stack:
        last_move = board.move_stack[-1]
        from_square = last_move.from_square
        to_square = last_move.to_square
        
        for square in [from_square, to_square]:
            row = 7 - (square // 8)
            col = square % 8
            x1 = MARGIN + col * SQUARE_SIZE
            y1 = row * SQUARE_SIZE
            # Highlight with a colored border
            draw.rectangle([x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE], 
                         outline=(255, 255, 0), width=4)
    
    # Draw pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            key = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().lower()
            piece_img = piece_images.get(key)
            if piece_img:
                x = MARGIN + col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                img.paste(piece_img, (x, y), piece_img.convert("RGBA"))
    
    # Draw coordinates
    columns = 'abcdefgh'
    for idx, char in enumerate(columns):
        x = MARGIN + idx * SQUARE_SIZE + SQUARE_SIZE // 2
        y = BOARD_SIZE + 5
        draw.text((x - 8, y), char, fill="white", font=font)
    
    for idx in range(8):
        row_number = str(8 - idx)
        x = 10
        y = idx * SQUARE_SIZE + SQUARE_SIZE // 2 - 12
        draw.text((x, y), row_number, fill="white", font=font)
    
    return img

def speak_message_async(message, rate=150):
    def speak_worker(msg):
        with speaking_lock:
            tts_engine.setProperty('rate', rate)
            tts_engine.say(msg)
            tts_engine.runAndWait()
    threading.Thread(target=speak_worker, args=(message,), daemon=True).start()

def get_best_moves(board, count=3):
    """Get the best moves from both Stockfish and Lichess database"""
    moves = []
    
    # Get Stockfish suggestion
    try:
        stockfish_move = stockfish.play(board, chess.engine.Limit(time=STOCKFISH_TIME_LIMIT))
        if stockfish_move and stockfish_move.move:
            moves.append(stockfish_move.move.uci())
    except Exception as e:
        st.warning(f"Stockfish error: {e}")
    
    # Get Lichess opening database suggestions
    try:
        fen = board.fen()
        url = f"https://explorer.lichess.ovh/lichess?variant=standard&fen={fen}"
        response = requests.get(url, timeout=5)
        data = response.json()
        lichess_moves = data.get("moves", [])
        for move_data in lichess_moves[:2]:  # Get top 2 from database
            move_uci = move_data['uci']
            if move_uci not in moves:
                moves.append(move_uci)
    except Exception as e:
        pass  # Silently fail for lichess API
    
    # Ensure we have at least some moves by getting random legal moves if needed
    if len(moves) < count:
        legal_moves = list(board.legal_moves)
        for move in legal_moves:
            if move.uci() not in moves:
                moves.append(move.uci())
                if len(moves) >= count:
                    break
    
    return moves[:count]

def check_game_state():
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        speak_message_async(f"Checkmate! {winner} wins!")
        st.session_state.game_message = f"🎉 Checkmate! {winner} wins! 🎉"
    elif board.is_stalemate():
        speak_message_async("Stalemate!")
        st.session_state.game_message = "🤝 Stalemate! It's a draw! 🤝"
    elif board.is_insufficient_material():
        speak_message_async("Draw due to insufficient material!")
        st.session_state.game_message = "🤝 Draw - Insufficient material! 🤝"
    elif board.is_check():
        speak_message_async("Check!")
        st.session_state.game_message = "⚠️ Check! ⚠️"
        st.session_state.game_stats["checks"] += 1
    else:
        st.session_state.game_message = ""

def play_computer_move():
    """Function to handle computer moves"""
    try:
        computer_move = stockfish.play(board, chess.engine.Limit(time=0.5))
        if computer_move and computer_move.move:
            # Get the SAN before pushing the move
            comp_move_san = board.san(computer_move.move)
            
            if board.is_capture(computer_move.move):
                st.session_state.game_stats["captures"] += 1
            
            board.push(computer_move.move)
            
            # Add computer move to history (Black's move)
            if st.session_state.move_history:
                st.session_state.move_history[-1] += f" {comp_move_san}"
            else:
                st.session_state.move_history.append(f"1... {comp_move_san}")
            
            st.session_state.game_stats["moves_played"] += 1
            st.success(f"🤖 Computer played {computer_move.move.uci()} ({comp_move_san})")
            speak_message_async(f"Computer plays {comp_move_san}")
            check_game_state()
            
            # Reset the flag
            st.session_state.computer_should_play = False
            return True
    except Exception as e:
        st.error(f"Computer move error: {e}")
        st.session_state.computer_should_play = False
    return False

def play_move(move_uci):
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            # Get SAN before pushing the move
            move_san = board.san(move)
            
            # Check if it's a capture
            if board.is_capture(move):
                st.session_state.game_stats["captures"] += 1
            
            # Store the turn before making the move
            was_white_turn = board.turn == chess.WHITE
            
            board.push(move)
            
            # Add to move history
            move_number = len(st.session_state.move_history) // 2 + 1
            if was_white_turn:  # White just moved
                st.session_state.move_history.append(f"{move_number}. {move_san}")
            else:  # Black just moved
                if st.session_state.move_history:
                    st.session_state.move_history[-1] += f" {move_san}"
                else:
                    st.session_state.move_history.append(f"1... {move_san}")
            
            st.session_state.game_stats["moves_played"] += 1
            
            st.success(f"✅ Move {move_uci} ({move_san}) played.")
            speak_message_async(f"Move {move_san} played")
            check_game_state()
            
            # FIXED: Set flag for computer to play if it's black's turn and auto-play is enabled
            if board.turn == chess.BLACK and not board.is_game_over() and st.session_state.auto_play:
                st.session_state.computer_should_play = True
                if st.session_state.get("debug_mode", False):
                    st.write("Debug: Setting computer_should_play = True")
            
            return True
        else:
            st.error("❌ Illegal move.")
            speak_message_async("Illegal move.")
            return False
    except Exception as e:
        st.error(f"❌ Invalid move input: {e}")
        speak_message_async("Invalid move input.")
        return False

# === MAIN UI ===
st.title("♟ Adaptive Chess Learning ♟")

# DEBUG: Add debug info
if st.session_state.get("debug_mode", False):
    st.write(f"Debug: computer_should_play = {st.session_state.computer_should_play}")
    st.write(f"Debug: auto_play = {st.session_state.auto_play}")
    st.write(f"Debug: board.turn = {'BLACK' if board.turn == chess.BLACK else 'WHITE'}")
    st.write(f"Debug: game_over = {board.is_game_over()}")

# FIXED: Check if computer should play at the start of each render
if st.session_state.computer_should_play and st.session_state.auto_play and board.turn == chess.BLACK and not board.is_game_over():
    st.info("🤖 Computer is thinking...")
    time.sleep(COMPUTER_MOVE_DELAY)
    if play_computer_move():
        st.rerun()

# Game status message
if st.session_state.game_message:
    st.markdown(f"""
    <div class='game-message'>
    {st.session_state.game_message}
    </div>
    """, unsafe_allow_html=True)

# Turn indicator
current_turn = "White" if board.turn == chess.WHITE else "Black"
turn_symbol = "♔" if board.turn == chess.WHITE else "♛"
st.markdown(f"""
<div class='turn-indicator'>
{turn_symbol} {current_turn} to move
</div>
""", unsafe_allow_html=True)

# Chess board
st.image(draw_board(board))

# Move suggestions (only show for white/human player)
if board.turn == chess.WHITE and not board.is_game_over():
    st.subheader("💡 Suggested Moves:")
    suggestions = get_best_moves(board, 3)
    
    if suggestions:
        col1, col2, col3 = st.columns(3)
        
        for i, move_uci in enumerate(suggestions):
            try:
                move = chess.Move.from_uci(move_uci)
                move_san = board.san(move)
                
                with [col1, col2, col3][i]:
                    if st.button(f"🎯 {move_uci}\n({move_san})", key=f"suggest_{i}"):
                        if play_move(move_uci):
                            st.rerun()
            except:
                pass

# Manual move input
st.subheader("🎯 Enter your move:")
move_input = st.text_input("Type move (UCI notation, e.g. e2e4):", 
                          key="move_uci_value", 
                          placeholder="Enter your move here...")

col1, col2 = st.columns([2, 1])
with col1:
    if st.button("🚀 Play Move"):
        if move_input.strip():
            speak_message_async(f"Trying move {move_input.strip()}")
            if play_move(move_input.strip()):
                st.rerun()
        else:
            st.warning("⚠️ Please enter a move.")
            speak_message_async("Please enter a move.")

with col2:
    if st.button("🔄 Clear Input"):
        st.rerun()

# === SIDEBAR ===
with st.sidebar:
    st.header("🎮 Game Controls")
    
    # Game statistics
    st.markdown("""
    <div class='game-stats'>
    <h4>📊 Game Statistics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Moves", st.session_state.game_stats["moves_played"])
        st.metric("Captures", st.session_state.game_stats["captures"])
    with col2:
        st.metric("Checks", st.session_state.game_stats["checks"])
        st.metric("Turn", len(board.move_stack) + 1)

    st.markdown("---")
    
    # Auto-play toggle
    st.session_state.auto_play = st.checkbox("🤖 Auto-play Computer (Black)", value=st.session_state.auto_play)
    
    # Debug toggle
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    st.session_state.debug_mode = st.checkbox("🐛 Debug Mode", value=st.session_state.debug_mode)
    
    # FIXED: Add manual computer move button for debugging
    if st.button("🤖 Force Computer Move"):
        if board.turn == chess.BLACK and not board.is_game_over():
            if play_computer_move():
                st.rerun()
        else:
            st.warning("Not computer's turn or game is over")
    
    # Control buttons
    if st.button("↩️ Undo Move"):
        if board.move_stack:
            last_move = board.pop()
            if st.session_state.move_history:
                st.session_state.move_history.pop()
            st.session_state.game_stats["moves_played"] = max(0, st.session_state.game_stats["moves_played"] - 1)
            # Reset computer play flag
            st.session_state.computer_should_play = False
            st.info(f"⏪ Move {last_move.uci()} undone.")
            speak_message_async(f"Move {last_move.uci()} undone.")
            st.rerun()
        else:
            st.warning("🚫 No moves to undo.")
            speak_message_async("No moves to undo.")

    if st.button("🔄 Reset Game"):
        board.reset()
        st.session_state.move_history = []
        st.session_state.game_stats = {"moves_played": 0, "captures": 0, "checks": 0}
        st.session_state.game_message = ""
        st.session_state.computer_should_play = False  # Reset flag
        st.info("🆕 Game reset.")
        speak_message_async("Game reset.")
        st.rerun()

    # Move history
    if st.session_state.move_history:
        st.markdown("### 📜 Move History")
        st.markdown("""
        <div class='move-history'>
        """, unsafe_allow_html=True)
        
        for move in st.session_state.move_history[-10:]:  # Show last 10 moves
            st.text(move)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Game analysis
    if st.button("🔍 Position Analysis"):
        try:
            info = stockfish.analyse(board, chess.engine.Limit(time=1.0))
            score = info["score"].relative
            if score.is_mate():
                st.info(f"🏁 Mate in {score.mate()} moves")
            else:
                cp_score = score.score() / 100.0
                if cp_score > 0:
                    st.info(f"📈 White is better by {cp_score:.2f}")
                elif cp_score < 0:
                    st.info(f"📉 Black is better by {abs(cp_score):.2f}")
                else:
                    st.info("⚖️ Position is equal")
        except Exception as e:
            st.warning("Unable to analyze position")

    if st.button("🚪 Quit"):
        stockfish.quit()
        st.stop()

    st.markdown("---")
    st.markdown("""
    <div class='developer-credit'>
        <strong>🚀 Developed by Soham</strong><br>
        <em>Adaptive Chess Learning</em><br>
        <small>Enhanced with AI assistance</small>
    </div>
    """, unsafe_allow_html=True)