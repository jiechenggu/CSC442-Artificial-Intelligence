from math import floor, ceil
from random import choice
from copy import deepcopy


class Player(object):
    def __init__(self, index, algorithm, maximum_depth = float("inf"), depth = 0):
       # Initialize a player 
       # index = 1 or 2 -> player1 or player2
       # algorithm = 'random', 'human', 'minimax'or 'alphabeta'        
        self.index = index
        self.opp_index = 3 - self.index  # the index of the opponent, 1 or 2
        self.algorithm = algorithm
        self.maximum_depth = maximum_depth        
        self.depth = depth

    def reset(self):
        # reset the player
        self.depth = 0

    def get_move(self, game):
        # get the move of the active player
        algos_dict = {
            'human': self.human_player,
            'random': self.random_player,
            'minimax': self.minimax_player,
            'alphabeta': self.alphabeta_player
        }
        # call the function of human_player, random_player, minimax_player, alphabeta_player
        return algos_dict[self.algorithm](game)
    
    def human_player(self, game):
        """human player"""
        move = self.ask_human_move(game)
        while not game.check_illegal_move(self, move):
            move = self.ask_human_move(game)
        return move

    def random_player(self, game):
        """random player"""
        filtered_actions = game.filter_actions(self)
        move = choice(filtered_actions) # choose a random legal move
        # print(f'\tRandom choice: {move}')
        return move
    
    def minimax_player(self, game):
        """minimax player"""
        move = self.max_value(game)[1]
        # print(f'\t minimax choice: {move}')
        return move

    def alphabeta_player(self, game):
        """alphabeta minimax player"""
        move = self.max_value(game, True)[1]
        # print(f'\t Alphabeta choice: {move}')
        return move

    def ask_human_move(self, game):
        # for a humam player, enter an input move 
        request_str = ""  
        
        # print the current board state for the player to choose a move
        if self.index == 1:
            request_str += f"\t{'-' * 25}Player1{'-' * 25}\n"
            request_str += (f"\tLocation:   " +
                            " ||   ".join(map(str, range(0, game.numPit))) +
                            f" | -    \n")
            request_str += (f"\tNum pits:   " +
                            " ||   ".join(map(str, game.p1_pits())) +
                            f" | -   {game.p1_store()}\n")
        else:
            request_str += (f"\tLocation: -    |   " +
                            " ||   ".join(map(str, range(game.numPit - 1, -1, -1))) +
                            f"\n")
            request_str += (f"\tNum pits: -   {game.p2_store()}|   " +
                            " ||   ".join(map(str, game.p2_pits()[::-1])) +
                            f"\n")
            request_str += f"\t{'-' * 25}Player2{'-' * 25}\n"
        print(request_str)

        try:
            move = int(input('\tPlease enter your target pit:'))
        except:
            move = int(input('\tWrong input. Please try again:'))            
        return move

    def max_value(self, game, ab_flag = False, alpha = float("-inf"), beta = float("inf")):
        """Find the max value of the move"""
        if game.check_end_game() or self.reach_max_depth():
            return self.score(game), None
        
        value = float("-inf")
        move = -1
        for action in game.filter_actions(self):
            opp_player = Player(self.opp_index, self.algorithm, self.maximum_depth, self.depth + 1)
            next_game = deepcopy(game)
            next_game.turn_taking(self, action)
            value2, move2 = opp_player.min_value(next_game, ab_flag, alpha, beta)
            if value2 > value:
                value = value2
                move = action
                alpha = max(alpha, value)                
            if ab_flag and value >= beta: # alpha-bate pruning
                return value, move
        return value, move

    def min_value(self, game, ab_flag = False, alpha = float("-inf"), beta = float("inf")):
        """Find the min value of the move"""
        if game.check_end_game() or self.reach_max_depth():
            return self.score(game), None
        
        value = float("inf")
        move = -1
        for action in game.filter_actions(self):
            opp_player = Player(self.opp_index, self.algorithm, self.maximum_depth, self.depth + 1)
            next_game = deepcopy(game)
            next_game.turn_taking(self, action)
            value2, move2 = opp_player.max_value(next_game, ab_flag, alpha, beta)
            if value2 < value:
                value = value2
                move = action
                beta = min(beta, value)
            if ab_flag and value <= alpha: # alpha-bate pruning
                return value, move
        return value, move
    
    def reach_max_depth(self):
        """check whether it reaches the maximun depth"""
        return self.depth >= self.maximum_depth
    
    def score(self, game, h_choice = 0):
        """calculate the current score of self player"""
        win_index, p1_score, p2_score = game.find_winner_scores()
        if game.check_end_game():
            if h_choice == 0:
                if win_index == self.index:
                    return 50
                elif win_index == self.opp_index:
                    return -50
                else:
                    return 0
            elif h_choice == 1:  # depth consider
                if win_index == self.index:
                    return 50 - self.depth
                elif win_index == self.opp_index:
                    return self.depth - 50
                else:
                    return 0
                pass
            elif h_choice == 2:  # diff consider
                if win_index == self.index:
                    return abs(p1_score - p2_score)
                elif win_index == self.opp_index:
                    return -abs(p1_score - p2_score)
                else:
                    return 0
            elif h_choice == 3:  # all consider
                if win_index == self.index:
                    return abs(p1_score - p2_score) - self.depth
                elif win_index == self.opp_index:
                    return -abs(p1_score - p2_score) + self.depth
                else:
                    return 0
            else:
                pass
        if win_index == self.index:
            return abs(p1_score - p2_score)
        elif win_index == self.opp_index:
            return -abs(p1_score - p2_score)
        else:
            return 0


