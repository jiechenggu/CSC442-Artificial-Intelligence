from mancala import *
from player import *
import time

def p1_VS_p2(p1, p2, e_n = 1, depth1 = 6, depth2 = 6, show_flag = False):
    player1 = Player(1, p1, depth1)
    player2 = Player(2, p2, depth2)
    mgame = Mancala()
    records = {p1: 0, p2: 0, 'draw': 0} if p1 != p2 else {p1 + '_1': 0, p2 + '_2': 0, 'draw': 0}

    def update_records(records, p1, p2, winner):
        if p1 != p2:
            records[['draw', p1, p2][winner]] += 1 # winner = 0 -> draw, 1 -> p1, 2 -> p2
        else:
            records[['draw', p1 + '_1', p2 + '_2'][winner]] += 1

    start_time = time.time()
    for round in range(e_n):
        print(f"round {round}:")
        winner = mgame.play_game(player1, player2, show_flag)
        print("winner", winner)
        update_records(records, p1, p2, winner)
        player1.reset()
        player2.reset()
        mgame.reset()
    end_time = time.time()
    return records, (end_time - start_time)

mgame = Mancala()
mgame.p_pits()
# random VS random
# for 100 times
# e_n = 100
# records, ts = p1_VS_p2('random', 'random', e_n, 6, 6)
# print(records) # {'random_1': 43, 'random_2': 53, 'draw': 4}
# print(f"time consuming: {ts}")

# random VS minmax
# for 100 times
# e_n = 100
# records, ts = p1_VS_p2('random', 'minimax', e_n, 6, 6)
# print(records)  # {'random': 1, 'minmax': 99, 'draw': 0}
# print(f"time consuming: {ts}")


# minmax VS alpha-beta
# for 100 times + same depth
# the first player wins for the same tree
# e_n = 100
# records, ts = p1_VS_p2('minimax', 'alphabeta', e_n, 6, 6)
# print(records)
# print(f"time consuming: {ts}")

# for 100 times + different depth
# alpha beta wins for deeper depth
e_n = 100
records, ts = p1_VS_p2('minimax', 'alphabeta', e_n, 6, 8)
print(records)
print(f"time consuming: {ts}")


# human VS
# for only one time
# e_n = 1
# 
# # VS random
# records = p1_VS_p2('human', 'random', e_n, 6, 6)
# 
# # VS minmax
# records = p1_VS_p2('human', 'minimax', e_n, 6, 6)
# 
# # VS alphabeta
# records = p1_VS_p2('human', 'alphabeta', e_n, 6, 8)
