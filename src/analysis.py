import glob
import yaml
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import chess.pgn

def parse_args() -> dict:
    parser = argparse.ArgumentParser(
                        prog='Chess Analyzer',
                        description='Analyze Game Results'
                        )
    parser.add_argument("--read", help="Which directory to read")

    args = parser.parse_args()
    return {**vars(args)}

    with open("config.yaml") as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return {**conf, **vars(args)}

def pgn_analysis(time, dir="out"):
    # Initialize counters for analysis
    piece_moves = {}
    special_moves = {
        "check": 0,
        "castle": 0,
        "en_passant": 0,
        "promotion": 0
    }
    
    games = glob.glob(f"{dir}/{time}/*/*.pgn")
    for f in games:
        with open(f, "r") as pgn_file:
            game = chess.pgn.read_game(pgn_file)
            
        board = game.board()  # Create a board from the initial position
        
        for move in game.mainline_moves():
            piece = board.piece_at(move.from_square)  # Get the moving piece
            if piece:
                piece_type = piece.symbol().upper()
                piece_moves[piece_type] = piece_moves.get(piece_type, 0) + 1
            
            # Check if the move is special
            if board.is_check():
                special_moves["check"] += 1
            if board.is_castling(move):
                special_moves["castle"] += 1
            if board.is_en_passant(move):
                special_moves["en_passant"] += 1
            if move.promotion:
                special_moves["promotion"] += 1
            
            board.push(move)

    return piece_moves, special_moves


def read_simulations(time, dir="out"):
    games = []
    summaries = glob.glob(f"{dir}/{time}/*/summary.yaml")
    for f in summaries:
        with open(f) as stream:
            try:
                conf = yaml.safe_load(stream)
                games.append(dict(conf))
            except yaml.YAMLError as exc:
                print(exc)
    return pd.DataFrame(games)

def create_plots(games, piece_moves, special_moves):
    sns.set_theme(style="ticks")
    f, ax = plt.subplots(figsize=(10, 6))
    sns.despine(f)

    sns.histplot(
        data=df,
        x="moves", hue="termination",
        multiple="stack",
        palette="light:m_r",
        edgecolor=".3",
        linewidth=.5,
    )
    ax.set_title("Histogram of Game Terminations by Moves")
    ax.set_xlabel("Moves")
    ax.set_ylabel("Count")

    plt.show()

    sns.set_theme(style="whitegrid")

    # Pie chart for piece moves
    plt.figure(figsize=(8, 8))
    plt.pie(piece_moves.values(), labels=piece_moves.keys(), autopct='%1.1f%%', startangle=140)
    plt.title("Piece Moves Distribution")
    plt.show()

    # Pie chart for special moves
    plt.figure(figsize=(8, 8))
    plt.pie(special_moves.values(), labels=special_moves.keys(), autopct='%1.1f%%', startangle=140)
    plt.title("Special Moves Distribution")
    plt.show()

if __name__ == '__main__':
    args = parse_args()
    df = read_simulations(args.read)
    piece_moves, special_moves = pgn_analysis(args.read, dir=args.output)
    create_plots(df, piece_moves, special_moves)
