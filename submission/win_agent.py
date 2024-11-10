from PushBattle import Game, PLAYER1, PLAYER2, EMPTY, BOARD_SIZE, NUM_PIECES

class WinAgent:
    def __init__(self):
        # The three moves to attempt to win
        self.win_moves = [
            (0, 7),  # top-right corner
            (7, 0),  # bottom-left corner
            (1, 7),  # adjacent corner to the top-right
        ]
        self.moves_made = []

    def get_best_move(self, game):
        possible_moves = self.get_possible_moves(game)
        # Check if all the planned moves can be made
        for move in self.win_moves:
            if move in possible_moves:
                # Make the move
                self.moves_made.append(move)
                return move  # Return the move to make
        return None  # If no move can be made, return None

    def reset(self):
        # Reset the agent's state after a game
        self.moves_made = []

    def get_possible_moves(self, game):
        """Returns list of all possible moves in current state."""
        moves = []
        current_pieces = game.p1_pieces if game.current_player == PLAYER1 else game.p2_pieces
        
        if current_pieces < NUM_PIECES:
            # placement moves
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if game.board[r][c] == EMPTY:
                        moves.append((r, c))
        else:
            # movement moves
            for r0 in range(BOARD_SIZE):
                for c0 in range(BOARD_SIZE):
                    if game.board[r0][c0] == game.current_player:
                        for r1 in range(BOARD_SIZE):
                            for c1 in range(BOARD_SIZE):
                                if game.board[r1][c1] == EMPTY:
                                    moves.append((r0, c0, r1, c1))
        return moves