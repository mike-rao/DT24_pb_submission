import random
import math
from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES

class MinimaxAgent:
    def __init__(self, player=PLAYER1, max_depth=3):
        self.player = player
        self.max_depth = max_depth
        self.transposition_table = {}  # Transposition table to store evaluated states

    def get_possible_moves(self, game):
        """Returns list of all possible moves in the current game state."""
        moves = []
        current_pieces = game.p1_pieces if game.current_player == PLAYER1 else game.p2_pieces
        
        if current_pieces < NUM_PIECES:
            # Placement moves (2 elements)
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if game.board[r][c] == EMPTY:
                        moves.append((r, c))  # Placement move (row, col)
        else:
            # Movement moves (4 elements)
            for r0 in range(BOARD_SIZE):
                for c0 in range(BOARD_SIZE):
                    if game.board[r0][c0] == game.current_player:
                        for r1 in range(BOARD_SIZE):
                            for c1 in range(BOARD_SIZE):
                                if game.board[r1][c1] == EMPTY:
                                    moves.append((r0, c0, r1, c1))  # Movement move (start_row, start_col, end_row, end_col)
        return moves

    def get_best_move(self, game):
        """Returns the best move based on the current game state using Minimax."""
        # Dynamic depth adjustment based on game stage
        if game.p1_pieces < NUM_PIECES // 2:
            self.max_depth = 3  # Shallower depth during early placement
        else:
            self.max_depth = 4  # Deeper search in the later game stages

        possible_moves = self.get_possible_moves(game)
        ordered_moves = self.order_moves(game, possible_moves)  # Move ordering to optimize Minimax

        best_move = None
        best_value = -math.inf

        # Manually create a copy of the game state
        game_copy = self.copy_game_state(game)

        for move in ordered_moves:
            # Handle placement phase (2-element move)
            if len(move) == 2:  # Placement move
                r, c = move
                self.place_piece(game_copy, r, c)

            # Handle movement phase (4-element move)
            elif len(move) == 4:  # Movement move
                r0, c0, r1, c1 = move
                self.move_piece(game_copy, r0, c0, r1, c1)

            # Evaluate the game state with minimax
            move_value = self.minimax(game_copy, self.max_depth, -math.inf, math.inf, False)
            
            # Track the best move
            if move_value > best_value:
                best_value = move_value
                best_move = move
        
        return best_move if best_move else random.choice(possible_moves)

    def minimax(self, game, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with Alpha-Beta pruning and transposition table."""
        state_hash = self.hash_game_state(game)
        if state_hash in self.transposition_table:
            return self.transposition_table[state_hash]  # Return cached value

        if depth == 0 or self.check_game_over(game):
            eval = self.evaluate_game(game)
            self.transposition_table[state_hash] = eval  # Cache the evaluated state
            return eval

        if maximizing_player:
            max_eval = -math.inf
            possible_moves = self.get_possible_moves(game)
            for move in possible_moves:
                game_copy = self.copy_game_state(game)
                
                # Apply the move depending on its type
                if len(move) == 2:  # Placement move
                    r, c = move
                    self.place_piece(game_copy, r, c)
                elif len(move) == 4:  # Movement move
                    r0, c0, r1, c1 = move
                    self.move_piece(game_copy, r0, c0, r1, c1)

                eval = self.minimax(game_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            self.transposition_table[state_hash] = max_eval  # Cache the evaluated state
            return max_eval
        else:
            min_eval = math.inf
            possible_moves = self.get_possible_moves(game)
            for move in possible_moves:
                game_copy = self.copy_game_state(game)
                
                # Apply the move depending on its type
                if len(move) == 2:  # Placement move
                    r, c = move
                    self.place_piece(game_copy, r, c)
                elif len(move) == 4:  # Movement move
                    r0, c0, r1, c1 = move
                    self.move_piece(game_copy, r0, c0, r1, c1)

                eval = self.minimax(game_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            self.transposition_table[state_hash] = min_eval  # Cache the evaluated state
            return min_eval

    def evaluate_line(self, game, r, c, dr, dc):
        """Evaluate a line starting at (r, c) in the direction (dr, dc) for two consecutive pieces."""
        player_count = 0
        opponent_count = 0
        empty_count = 0
        line_length = 3  # Length of the diagonal line to evaluate

        # Check 3 cells in the line (including the starting point)
        for i in range(line_length):
            nr = r + i * dr
            nc = c + i * dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if game.board[nr][nc] == self.player:
                    player_count += 1
                elif game.board[nr][nc] == (PLAYER2 if self.player == PLAYER1 else PLAYER1):
                    opponent_count += 1
                else:
                    empty_count += 1

        # For diagonals: Encourage creating 2-in-a-row with one empty space
        if player_count == 2 and empty_count == 1:
            return 10  # Positive score for good diagonal potential
        if opponent_count == 2 and empty_count == 1:
            return -10  # Negative score for opponent’s diagonal threat

        return 0  # Neutral if the line is not a potential diagonal

    def evaluate_game(self, game):
        score = 0

        # Horizontal lines
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE - 2):
                score += self.evaluate_line(game, r, c, 0, 1)  # Horizontal

        # Vertical lines
        for r in range(BOARD_SIZE - 2):
            for c in range(BOARD_SIZE):
                score += self.evaluate_line(game, r, c, 1, 0)  # Vertical

        # Ascending Diagonals (top-left to bottom-right)
        for r in range(BOARD_SIZE - 2):
            for c in range(BOARD_SIZE - 2):
                score += self.evaluate_line(game, r, c, 1, 1)  # Ascending diagonal

        # Descending Diagonals (top-right to bottom-left)
        for r in range(BOARD_SIZE - 2):
            for c in range(2, BOARD_SIZE):
                score += self.evaluate_line(game, r, c, 1, -1)  # Descending diagonal

        # Block opponent threats
        score += self.block_opponent_threats(game)

        return score

    def block_opponent_threats(self, game):
        """Check for opponent's potential winning move and return a high penalty if a move is needed to block it."""
        block_score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if game.board[r][c] == (PLAYER2 if self.player == PLAYER1 else PLAYER1):
                    # Check horizontal, vertical, and diagonal for opponent's threat of 2 in a row with an empty space
                    block_score += self.check_opponent_line(game, r, c, 1, 0)  # Horizontal
                    block_score += self.check_opponent_line(game, r, c, 0, 1)  # Vertical
                    block_score += self.check_opponent_line(game, r, c, 1, 1)  # Diagonal top-left to bottom-right
                    block_score += self.check_opponent_line(game, r, c, 1, -1)  # Diagonal top-right to bottom-left
        return block_score

    def check_opponent_line(self, game, r, c, dr, dc):
        """Checks if there is a threat of two consecutive opponent pieces in a line."""
        opponent_count = 0
        empty_count = 0
        for i in range(3):
            nr = r + i * dr
            nc = c + i * dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if game.board[nr][nc] == (PLAYER2 if self.player == PLAYER1 else PLAYER1):
                    opponent_count += 1
                elif game.board[nr][nc] == EMPTY:
                    empty_count += 1
        if opponent_count == 2 and empty_count == 1:
            return 50  # High penalty for blocking a potential win
        return 0

    def order_moves(self, game, moves):
        """Sort moves to prioritize center and corners for strategic advantage."""
        # Example ordering strategy: prioritize center first, then corners
        center = (BOARD_SIZE // 2, BOARD_SIZE // 2)
        corners = [(0, 0), (0, BOARD_SIZE - 1), (BOARD_SIZE - 1, 0), (BOARD_SIZE - 1, BOARD_SIZE - 1)]
        return sorted(moves, key=lambda move: (
            move == center,  # Prioritize center
            move in corners,  # Prioritize corners
        ), reverse=True)

    def copy_game_state(self, game):
        """Return a deep copy of the game state."""
        game_copy = Game()
        game_copy.board = [row[:] for row in game.board]  # Deep copy of the board
        game_copy.current_player = game.current_player
        game_copy.p1_pieces = game.p1_pieces
        game_copy.p2_pieces = game.p2_pieces
        return game_copy

    def place_piece(self, game, r, c):
        """Place a piece for the current player at the specified position (r, c)."""
        game.board[r][c] = game.current_player
        if game.current_player == PLAYER1:
            game.p1_pieces += 1
        else:
            game.p2_pieces += 1

        # Manually switch the current player
        if game.current_player == PLAYER1:
            game.current_player = PLAYER2
        else:
            game.current_player = PLAYER1

    def move_piece(self, game, r0, c0, r1, c1):
        """Move a piece for the current player from (r0, c0) to (r1, c1)."""
        game.board[r1][c1] = game.board[r0][c0]
        game.board[r0][c0] = EMPTY

        # Manually switch the current player
        if game.current_player == PLAYER1:
            game.current_player = PLAYER2
        else:
            game.current_player = PLAYER1

    def check_game_over(self, game):
        """Check if the game is over based on the current game state."""
        # Implement game-over logic if applicable (e.g., winner, draw, etc.)
        return False

    def hash_game_state(self, game):
        """Generate a unique hash for the game state."""
        return str(game.board)
