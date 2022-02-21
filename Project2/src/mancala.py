class Mancala(object):
    
    def __init__(self, m = 6, k = 4, state = None):
        self.numPit = m # number of pits on each side -> 6
        self.stonesInPit = k # initial number of stones in a pit -> 4
        self.ready_player = 1
        if state:
            self.state = state # a list of 14 elements
        else:
            self.state = self.generate_init_state()
    
    def generate_init_state(self):
        # generate the initial state
        return [self.stonesInPit] * self.numPit + [0] + [self.stonesInPit] * self.numPit + [0] # list

    def reset(self):
        # reset the environment
        self.ready_player = 1
        self.state = self.generate_init_state()

    def p1_pits(self):
        # get the number of stones in each pit for player1
        return self.state[0 : self.numPit]

    def p2_pits(self):
        # get the number of stones in each pit for player2
        return self.state[self.numPit+1 : -1]

    def p1_store(self):
        # get the number of stones in the store of player1
        return self.state[self.numPit]

    def p2_store(self):
        # get the number of stones in the store of player2
        return self.state[-1]

    def p_pits(self, index):
        # get the number of stones in each pit for the active player
        if index == 1:
            return self.p1_pits()
        else:
            return self.p2_pits()

    def p_store(self, index):
        # get the number of stones in the store of the active player
        if index == 1:
            return self.p1_store()
        else:
            return self.p2_store()

    def update_store(self, value, index):
        # update the number of stones in the store of the active player
        if index == 1:
            self.state[self.numPit] = value
        else:
            self.state[-1] = value

    def update_pit(self, value, pit_index, index):
        # update the number of stones in each pit for the active player
        if index == 1:
            self.state[pit_index] = value
        else:
            self.state[pit_index + self.numPit + 1] = value

    def filter_actions(self, player):
        # get only the legal actions -> list of indexes of pits that have stones
        pits = self.p_pits(player.index)
        actions = []
        for index, value in enumerate(pits):
            if value > 0:
                actions.append(index)            
        return actions

    def show_board(self):
        # print out the board state
        board_vis = "Hello"
        board_vis = f"\n{'*' * 22}  Board state  {'*' * 22}\n"
        str_p2_store = " " +str(self.p2_store()) if self.p2_store() < 10 else str(self.p2_store())
        # print the current state of player2
        board_vis += (f" {str_p2_store} - |   " +
                      " ||  ".join(
                          [i if len(i) == 2 else ' ' + i for i in list(map(str, self.p2_pits()[::-1]))]) + " |      \n")
        board_vis += f"{'-------' * 8}\n"
        # print the current state of player1
        board_vis += ("      |   " + " ||  ".join(
            [i if len(i) == 2 else ' ' + i for i in list(map(str, self.p1_pits()))]) +
                      f" | -   {self.p1_store()}\n")
        board_vis += f"{'*' * 59}\n"
        print(board_vis)

    def check_end_game(self):
        # there is no stone in the pits on either side
        if (any(self.p1_pits()) and any(self.p2_pits())):
            return False
        else:
            return True

    def find_scores(self):
        # get the scores of both players
        p1_score = self.p1_store()
        p2_score = self.p2_store()
        return p1_score, p2_score

    def find_winner_scores(self):
        # return the index of winner and the scores of two players
        p1_score, p2_score = self.find_scores()
        if p1_score > p2_score:
            winner = 1
        elif p1_score < p2_score:
            winner = 2
        else:
            winner = 0 # draw
        return winner, p1_score, p2_score

    def end_game(self, show_flag = True):
        # game over and print the results
        winner, p1_score, p2_score = self.find_winner_scores()
        if show_flag == True:
            print('final state:')
            self.show_board()
            go_str = "Game Over!\n"
            if winner == 1:
                go_str += f"{'#' * 25}\n##   Player 1 wins!   ##\n"
            elif winner == 2:
                go_str += f"{'#' * 25}\n##   Player 2 wins!   ##\n"
            else:
                go_str += f"{'#' * 25}\n##        Draw.       ##\n"
            go_str += f"## Player 1 score: {self.p1_store()} ##\n"
            go_str += f"## Player 2 score: {self.p2_store()} ##\n{'#' * 25}\n"
            print(go_str)
        return winner

    def check_illegal_move(self, player, action):
        # check if the move the active player chooses is legal or not
        filtered_actions = self.filter_actions(player)
        if action not in filtered_actions:
            print('Illegal move! Please choose another move!')
            return False
        return True

    def sowing(self, player, move):
        # update the board state with a new move
        
        init_pit = move
        stones = self.p_pits(player.index)[init_pit]
        curr_len = 2 * self.numPit + 1 # 13 available pits for each player

        if player.index == 1: # player1
            curr_state = self.state[:-1] 
        else: # player2
            curr_state = self.p2_pits() + [self.p2_store()] + self.p1_pits() 

        per_add = stones // curr_len # the number of complete circles where the active player can go through every available pit
        dis_pit = stones % curr_len # the distance between the chose pit and the pit where the last stone is
        curr_state[init_pit] = 0 # remove all the stones in the chosen pit
        last_pit = (init_pit + dis_pit) % curr_len # the index of the pit where the last stone is
        # update the board state
        new_state = [i + per_add for i in curr_state] 
        if last_pit > init_pit:
            for index, value in enumerate(new_state):
                if init_pit < index <= last_pit:
                    new_state[index] = value + 1  
        elif last_pit < init_pit:
            for index, value in enumerate(new_state):
                if init_pit < index or index <= last_pit:
                    new_state[index] = value + 1  
        else: # reach one or more complete circles
            pass 

        if player.index == 1: # player1
            return new_state + [self.p2_store()], last_pit
        else: # player2
            return new_state[-self.numPit:] + [self.p1_store()] + new_state[:-self.numPit], last_pit

    def turn_taking(self, player, move):        
        # return True if it is still the active player's turn; 
        # otherwise, return False to change the player

        self.state, last_pit = self.sowing(player, move)
        if last_pit == self.numPit:
            # if the last stone is sowed into the store,
            # the active player can take another turn
            return True
        if last_pit < self.numPit and self.p_pits(player.index)[last_pit] == 1:
            # if the last stone is sowed into an empty pits on the active player’s side, 
            # and there are some stones in the opposite pit,
            # the stones in these two pits will be captured in the active player’s store
            opp_last_pit = self.numPit - 1 - last_pit
            self.update_store(self.p_store(player.index) + 1
                              + self.p_pits(player.opp_index)[opp_last_pit], player.index)
            # empty two pits
            self.update_pit(0, last_pit, player.index)
            self.update_pit(0, opp_last_pit, player.opp_index)
        return False

    def play_game(self, player1, player2, show_flag = True):
        # main function -> start the game
        players = [player1, player2]
        player = players[self.ready_player - 1] # player1 starts the game

        if show_flag == True:
            print('initial state:')
            self.show_board()

        while True:          
            if self.check_end_game():  # check if the game reaches the final state
                return self.end_game(show_flag)
            if show_flag == True:
                print(f"Player {player.index}:")
                
            move = player.get_move(self)
            if show_flag == True:
                print(f'{player.algorithm} player choice: {move}')
            moves = [move]
            
            while self.turn_taking(player, move): # check if it is the time to change the active player
                if self.check_end_game():
                    return self.end_game(show_flag)
                move = player.get_move(self)
                if show_flag == True:
                    print(f'{player.algorithm} player choice: {move}')
                moves.append(move)                
            if show_flag == True:
                self.show_board()
            player = players[player.opp_index - 1] # change the active player
