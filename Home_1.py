import streamlit as st
from PIL import Image
import random
import time

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Chess Level 1 - Learn Chess Pieces",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === SESSION STATE INITIALIZATION ===
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'learn'
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_total' not in st.session_state:
    st.session_state.quiz_total = 0
if 'current_piece' not in st.session_state:
    st.session_state.current_piece = None
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# === ENHANCED CSS STYLING ===
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

/* Button styling */
.stButton > button {
    background: linear-gradient(45deg, #FCE181, #FEF9C7);
    color: #026670;
    border-radius: 15px;
    padding: 12px 24px;
    font-weight: bold;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(252, 225, 129, 0.4);
}

.stButton > button:hover {
    background: linear-gradient(45deg, #FEF9C7, #FCE181);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(252, 225, 129, 0.6);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #026670 0%, #024950 100%);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Custom card styling */
.piece-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    transition: transform 0.3s ease;
}

.piece-card:hover {
    transform: translateY(-3px);
}

/* Quiz styling */
.quiz-container {
    background: linear-gradient(135deg, #FCE181, #FEF9C7);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

/* Progress bar styling */
.progress-container {
    background: #E8E8E8;
    border-radius: 10px;
    padding: 3px;
    margin: 20px 0;
}

.progress-bar {
    background: linear-gradient(45deg, #026670, #9FEDD7);
    height: 20px;
    border-radius: 8px;
    transition: width 0.5s ease;
}

/* Metrics styling */
.metric-card {
    background: rgba(255, 255, 255, 0.8);
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    backdrop-filter: blur(5px);
}
</style>
""", unsafe_allow_html=True)

# === ENHANCED PIECE DATA ===
piece_data = {
    "white": {
        "Pawn ♙": {
            "file": "wp.png",
            "description": "The foot soldier of chess. Moves forward one square, captures diagonally. Can promote to any piece upon reaching the opposite end!",
            "points": 1,
            "movement": "Forward 1 square (2 on first move)"
        },
        "Knight ♘": {
            "file": "wn.png", 
            "description": "The only piece that can jump! Moves in an L-shape: 2 squares in one direction, then 1 perpendicular.",
            "points": 3,
            "movement": "L-shaped jumps"
        },
        "Bishop ♗": {
            "file": "wb.png",
            "description": "Glides diagonally across the board. Each player starts with one light-squared and one dark-squared bishop.",
            "points": 3,
            "movement": "Diagonal lines"
        },
        "Rook ♖": {
            "file": "wr.png", 
            "description": "The castle tower! Moves horizontally and vertically across ranks and files. Essential for castling.",
            "points": 5,
            "movement": "Straight lines (horizontal/vertical)"
        },
        "Queen ♕": {
            "file": "wq.png",
            "description": "The most powerful piece! Combines rook and bishop movements. Can move in any direction, any distance.",
            "points": 9,
            "movement": "All directions"
        },
        "King ♔": {
            "file": "wk.png",
            "description": "The most important piece! Moves one square in any direction. Losing your king means losing the game!",
            "points": "∞",
            "movement": "One square in any direction"
        }
    },
    "black": {
        "Pawn ♟": {
            "file": "bp.png",
            "description": "Same as white pawn, but moves from black's perspective towards white's side of the board.",
            "points": 1,
            "movement": "Forward 1 square (2 on first move)"
        },
        "Knight ♞": {
            "file": "bn.png",
            "description": "Identical movement to white knight. The horse that jumps over obstacles!",
            "points": 3,
            "movement": "L-shaped jumps"
        },
        "Bishop ♝": {
            "file": "bb.png",
            "description": "Same diagonal movement as white bishop. Controls squares of one color only.",
            "points": 3,
            "movement": "Diagonal lines"
        },
        "Rook ♜": {
            "file": "br.png",
            "description": "Same horizontal and vertical movement as white rook. Castle strength!",
            "points": 5,
            "movement": "Straight lines (horizontal/vertical)"
        },
        "Queen ♛": {
            "file": "bq.png",
            "description": "Same all-direction movement as white queen. The black army's general!",
            "points": 9,
            "movement": "All directions"
        },
        "King ♚": {
            "file": "bk.png",
            "description": "Same limited movement as white king. The piece you must protect at all costs!",
            "points": "∞",
            "movement": "One square in any direction"
        }
    }
}

# === SIDEBAR NAVIGATION ===
with st.sidebar:
    st.title("🎯 Chess Level 1")
    
    mode = st.radio(
        "Choose Learning Mode:",
        ["📚 Learn Pieces", "🧩 Quiz Mode", "📊 Progress"],
        index=0 if st.session_state.current_mode == 'learn' else (1 if st.session_state.current_mode == 'quiz' else 2)
    )
    
    if mode == "📚 Learn Pieces":
        st.session_state.current_mode = 'learn'
    elif mode == "🧩 Quiz Mode":
        st.session_state.current_mode = 'quiz'
    else:
        st.session_state.current_mode = 'progress'
    
    st.markdown("---")
    
    # Instructions based on mode
    if st.session_state.current_mode == 'learn':
        st.markdown("""
        **Learning Mode Instructions:**
        - Study each piece's appearance
        - Read their descriptions carefully  
        - Note the point values
        - Compare white vs black pieces
        - Take your time to memorize!
        """)
    elif st.session_state.current_mode == 'quiz':
        st.markdown("""
        **Quiz Mode Instructions:**
        - Identify the chess piece shown
        - Click your answer
        - Get instant feedback
        - Build your recognition skills!
        """)
    else:
        st.markdown("""
        **Progress Tracking:**
        - View your quiz statistics
        - Track learning progress
        - Reset scores if needed
        """)

# === MAIN CONTENT BASED ON MODE ===

if st.session_state.current_mode == 'learn':
    # === LEARNING MODE ===
    st.title("♟️ Level 1: Learn Chess Pieces")
    st.markdown("### Master the fundamentals by learning each piece's role and movement!")
    
    # Piece overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><h4>6</h4><p>Piece Types</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h4>32</h4><p>Total Pieces</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h4>2</h4><p>Colors</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><h4>64</h4><p>Board Squares</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display pieces in enhanced cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("♙ White Army")
        for piece_name, piece_info in piece_data["white"].items():
            with st.container():
                st.markdown('<div class="piece-card">', unsafe_allow_html=True)
                
                piece_col1, piece_col2 = st.columns([1, 3])
                with piece_col1:
                    try:
                        # Try to load image, use placeholder if not available
                        st.image(f"assets/{piece_info['file']}", width=80)
                    except:
                        st.markdown(f"<div style='width:80px;height:80px;background:#f0f0f0;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:40px;'>{piece_name.split()[1]}</div>", unsafe_allow_html=True)
                
                with piece_col2:
                    st.markdown(f"**{piece_name}**")
                    st.markdown(f"*Value: {piece_info['points']} points*")
                    st.markdown(f"**Movement:** {piece_info['movement']}")
                    st.markdown(piece_info['description'])
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("♟ Black Army") 
        for piece_name, piece_info in piece_data["black"].items():
            with st.container():
                st.markdown('<div class="piece-card">', unsafe_allow_html=True)
                
                piece_col1, piece_col2 = st.columns([1, 3])
                with piece_col1:
                    try:
                        st.image(f"assets/{piece_info['file']}", width=80)
                    except:
                        st.markdown(f"<div style='width:80px;height:80px;background:#f0f0f0;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:40px;'>{piece_name.split()[1]}</div>", unsafe_allow_html=True)
                
                with piece_col2:
                    st.markdown(f"**{piece_name}**")
                    st.markdown(f"*Value: {piece_info['points']} points*")
                    st.markdown(f"**Movement:** {piece_info['movement']}")
                    st.markdown(piece_info['description'])
                
                st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_mode == 'quiz':
    # === QUIZ MODE ===
    st.title("🧩 Chess Piece Quiz")
    st.markdown("### Test your knowledge! Can you identify each piece?")
    
    # Generate new question if needed
    if st.session_state.current_piece is None:
        all_pieces = []
        for color in piece_data:
            for piece in piece_data[color]:
                all_pieces.append((color, piece, piece_data[color][piece]))
        st.session_state.current_piece = random.choice(all_pieces)
        st.session_state.show_answer = False
    
    color, piece_name, piece_info = st.session_state.current_piece
    
    # Quiz container
    st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### What piece is this?")
        
        try:
            st.image(f"assets/{piece_info['file']}", width=120)
        except:
            st.markdown(f"<div style='width:120px;height:120px;background:#f0f0f0;border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:60px;margin:auto;'>{piece_name.split()[1]}</div>", unsafe_allow_html=True)
        
        # Answer options
        all_piece_names = list(piece_data["white"].keys()) + list(piece_data["black"].keys())
        # Remove duplicates while preserving order
        unique_pieces = []
        seen = set()
        for p in all_piece_names:
            base_name = p.split()[0]
            if base_name not in seen:
                unique_pieces.append(base_name)
                seen.add(base_name)
        
        correct_answer = piece_name.split()[0]
        
        # Create answer buttons
        st.markdown("### Choose your answer:")
        
        button_cols = st.columns(3)
        for i, piece_type in enumerate(unique_pieces):
            col_index = i % 3
            with button_cols[col_index]:
                if st.button(f"{piece_type}", key=f"answer_{piece_type}"):
                    st.session_state.quiz_total += 1
                    if piece_type == correct_answer:
                        st.session_state.quiz_score += 1
                        st.success(f"🎉 Correct! This is a {color} {piece_name}")
                        st.balloons()
                    else:
                        st.error(f"❌ Wrong! This is a {color} {piece_name}")
                    
                    st.session_state.show_answer = True
                    time.sleep(1)
        
        if st.session_state.show_answer:
            st.markdown("---")
            st.info(f"**{piece_name}:** {piece_info['description']}")
            
            if st.button("🔄 Next Question"):
                st.session_state.current_piece = None
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Score display
    if st.session_state.quiz_total > 0:
        score_percentage = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
        st.markdown(f"### 📊 Score: {st.session_state.quiz_score}/{st.session_state.quiz_total} ({score_percentage:.1f}%)")
        
        # Progress bar
        progress_html = f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {score_percentage}%"></div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)

else:
    # === PROGRESS MODE ===
    st.title("📊 Your Chess Learning Progress")
    
    if st.session_state.quiz_total > 0:
        score_percentage = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Questions Answered", st.session_state.quiz_total)
        with col2:
            st.metric("Correct Answers", st.session_state.quiz_score)
        with col3:
            st.metric("Success Rate", f"{score_percentage:.1f}%")
        with col4:
            if score_percentage >= 80:
                st.metric("Level Status", "🏆 Mastered!")
            elif score_percentage >= 60:
                st.metric("Level Status", "🎯 Good Progress")
            else:
                st.metric("Level Status", "📚 Keep Learning")
        
        # Progress visualization
        st.markdown("### Learning Progress")
        progress_html = f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {score_percentage}%"></div>
        </div>
        <p style="text-align: center; margin-top: 10px;">
            {score_percentage:.1f}% - {st.session_state.quiz_score} out of {st.session_state.quiz_total} correct
        </p>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        if score_percentage >= 90:
            st.success("🎉 Excellent work! You've mastered piece identification. Ready for Level 2!")
        elif score_percentage >= 70:
            st.info("👍 Good job! A few more practice rounds and you'll master this level.")
        else:
            st.warning("📖 Keep practicing! Review the learning mode and try more quiz questions.")
            
    else:
        st.info("🎯 No quiz data yet! Try the Quiz Mode to start tracking your progress.")
        st.markdown("### Getting Started")
        st.markdown("""
        1. 📚 **Start with Learn Mode** - Study all the pieces
        2. 🧩 **Try Quiz Mode** - Test your knowledge  
        3. 📊 **Track Progress** - Monitor improvement
        4. 🏆 **Master Level 1** - Achieve 90%+ accuracy
        """)
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Reset Progress", type="secondary"):
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = 0
        st.session_state.current_piece = None
        st.success("Progress reset! Start fresh with your learning journey.")
        time.sleep(1)
        st.rerun()

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #026670; font-style: italic;">
    🎓 Master chess piece identification to unlock Level 2: Basic Moves & Captures!
</div>
""", unsafe_allow_html=True)