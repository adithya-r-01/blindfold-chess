import chess
import analysis
import os
import chess.engine
import chess.pgn
import random
import argparse
from collections import Counter
from dataclasses import dataclass, field
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime

class ValidationError(Exception):
    pass

class ValidationError(Exception):
    pass

@dataclass
class Configuration:
    verbosity: bool = False
    simulations: int = 100
    opponent: str = "Random"
    engine: str = None
    threads: int = 1
    output: str = "out"

    def __post_init__(self):
        self.simulations = self.simulations if self.simulations is not None else 100
        self.threads = self.threads if self.threads is not None else 1
        self.opponent = (self.opponent if self.opponent else "Random").title()
        self.output = self.output if self.output else "out"
        
        self.simulations = self._validate_int(self.simulations, min_=0)
        self.threads = self._validate_int(self.threads, min_=1)
        self._validate_args()

    @staticmethod
    def _validate_int(value, min_=None):
        if not isinstance(value, int) or (min_ is not None and value < min_):
            raise ValidationError(f"Value must be an integer >= {min_}")
        return value

    def _validate_args(self):
        if self.opponent not in {'Engine', 'Random'}:
            raise ValidationError("Opponent must be 'Engine' or 'Random'")
        if self.opponent == "Engine" and (not self.engine or not path.exists(self.engine)):
            raise ValidationError("Engine path does not exist")
        if  not os.path.exists(self.output):
            raise ValidationError("Output path does not exist")


class GameRecord:

    def  __init__(self, simulation: int, players: tuple) -> None:
        self.id = f'Game_{simulation}_{players[0]}_{players[1]}'
        self.movelist = []
        self.players = players
        self.turn = 0
        self.winner = None
        self.termination = None

    def next_turn(self) -> str:
        self.turn = (self.turn + 1) % 2

    def add_move(self, board, move: str):
        self.movelist.append(str(board.san(move)))

    def return_results(self) -> tuple:
        now = datetime.now()
        result_map = {0: "1-0", 1: "0-1", None: "1/2-1/2"}
        color_map = {0: "White", 1: "Black", None: "Draw"}
        pgn = [
            '[Event "Simulation"]',
            '[Site "?"]',
            f'[Date "{now.strftime("%Y.%m.%d")}"]',
            f'[Round "{self.id.split("_")[1]}"]',
            f'[White "{self.players[0]}"]',
            f'[Black "{self.players[1]}"]',
            f'[Result "{result_map.get(self.winner)}"]'
        ]
        for i, m in enumerate([self.movelist[i:i + 2] for i in range(0, len(self.movelist), 2)]):
            pgn.append(f'{i+1}. {m[0]} {m[1]}' if len(m) > 1 else f'{i+1}. {m[0]}')
        return pgn, self.termination, self.winner, len(self.movelist)

        

def parse_args() -> dict:
    parser = argparse.ArgumentParser(
                        prog='Chess Simulator',
                        description='Simulate Random Chess Games or Against an Engine'
                        )
    parser.add_argument("--verbosity", help="Increase output verbosity - default is False", action="store_true")
    parser.add_argument("--simulations", help="Number of games - default is 100")
    parser.add_argument("--opponent", help="Accepts 'Random' or 'Engine' - default is Random")
    
    args = parser.parse_args()

    with open("config.yaml") as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return {**conf, **vars(args)}

def simulate(game: GameRecord, config: Configuration, lock: Lock) -> None:
    if config.opponent == "Engine": engine = chess.engine.SimpleEngine.popen_uci(config.engine)
    board = chess.Board()

    while (not board.is_game_over()):
        player = game.players[game.turn]

        if player == "Random":
            moves = list(board.legal_moves)
            random.shuffle(moves)
            move = moves[0]
        if player == "Engine":
            move = engine.play(board, chess.engine.Limit(time=0.1)).move
        
        game.add_move(board, move)
        board.push(move)
        game.next_turn()

    if config.opponent == "Engine": engine.quit()

    termination = board.outcome().termination
    winner = None if board.outcome().winner is None else 0 if board.outcome().winner else 1
    game.termination = board.outcome().termination
    game.winner = None if board.outcome().winner is None else 0 if board.outcome().winner else 1
    
    if config.verbosity:
        with lock:
            print(f"{game.id} - {game.players[0]} (White) vs. {game.players[1]} (Black)")
            print(f"Outcome: {termination}")
            print(f"Winner: {'None' if winner == None else ('White', 'Black')[winner]}", end="\n\n")

if __name__ == '__main__':

    sim_config = Configuration(**parse_args())

    games = [GameRecord(i, ('Random', sim_config.opponent)) for i in range(sim_config.simulations)]
    for i in random.sample(range(len(games)), len(games) // 2):
        games[i] = GameRecord(games[i].id.split("_")[1], tuple(reversed(games[i].players)))

    lock = Lock()
    with ThreadPoolExecutor(max_workers=sim_config.threads) as executor:
        future_to_game = {executor.submit(simulate, game, sim_config, lock): game for game in games}
    

    for i, future in enumerate(as_completed(future_to_game)):
        game = future_to_game[future]
        try:
            future.result()
        except Exception as e:
            print(f"Game {game.id} generated an exception: {e}")
    
    now = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    os.mkdir(f'{sim_config.output}/{now}')
    for g in games:
        pgn, termination, winner, moves = g.return_results()
        os.mkdir(f'{sim_config.output}/{now}/{g.id}')
        f = open(f'{sim_config.output}/{now}/{g.id}/game.pgn', "w")
        f.writelines("\n".join(pgn))
        f.close()
        f = open(f'{sim_config.output}/{now}/{g.id}/summary.yaml', "w")
        f.writelines([
            f'termination: {termination}\n',
            f'winner: {winner}\n',
            f'moves: {moves}\n'
        ])

