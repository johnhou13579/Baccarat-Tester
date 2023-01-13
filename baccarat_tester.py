from math import atanh
from multiprocessing.dummy import current_process
import random
import sys

# initialize variables
bankroll = 1000  # starting bankroll
goal = bankroll + 500   # goal is +500 of bankroll
bet = 25  # starting bet
losing_arr = [25, 50, 100, 200]   # bet for martingale

def simulate_round(player_win_prob, banker_win_prob, tie_prob):
  # generate random number between 0 and 1
  r = random.random()
  log_info(str(r))
  # determine outcome based on probabilities
  if r < player_win_prob:
    return 1  # player win
  elif r < player_win_prob + banker_win_prob:
    return 0  # banker win
  else:
    return 2  # tie

def print_round_outcome(i, outcome):
    log_info("====> ROUND " + str(i) + " <==== OUTCOME:", end=" ")
    log_info(str(outcome), end=" IS ")
    if outcome == 0:
        log_info("BANKER")
    elif outcome == 1:
        log_info("PLAYER")
    else:
        log_info("TIE")

def print_gambler_bet(previous_winner):
    if previous_winner == 0:
        log_info("PLAYED^ Banker ", end="")
    elif previous_winner == 1:
        log_info("PLAYED^ Player ", end="")
    else:
        log_info("PLAYED^ TIE ", end="")

def backtesting(rounds, bankroll, bet):
    ath = -sys.maxsize - 1
    atl = sys.maxsize
    previous_winner = None
    winning_streak = 0  # number of consecutive wins
    losing_streak = 0  # number of consecutive losses
    current_bet_position = 0
    just_won = False

    for i in range(0, rounds):
        # simulate round outcome: 1 for player, 0 for banker
        outcome = simulate_round(0.446247, 0.458598, 0.095156)

        # print outcome of round (toggle with LOG_INFO)
        print_round_outcome(i, outcome)

        if bankroll <= 0 or bet > bankroll:
            # exit if no more bankroll or cannot afford bet
            log_info("BANKRUPT ROUND " + str(i))
            return bankroll, ath, atl
        elif bankroll >= goal:
            # exit if goal is met
            log_info("SUCCESS $500 GOAL ROUND " + str(i))
            return bankroll, ath, atl
        elif i < 3:
            # skip first three hands, keep track of previous_winner
            if outcome == 2:
                log_info("SKIPPING")
                i-=1
                continue
            previous_winner = outcome
            continue
        elif outcome == 2:
            # skip if tie
            log_info("SKIPPING")
            continue
        elif losing_streak == 4:
            # if martingale 4 times ($375 loss), skip turn, reset bet
            log_info("SKIPPING")
            losing_streak = 0
            bet = 0
            previous_winner = outcome
            continue
        elif losing_streak == 3:
            # if martingale 3 times, means chop chop 3x, bet next chop instead of previous_winner
            log_info("CHOP CHOP 3X")
            bet = losing_arr[losing_streak]
        elif just_won:
            # if won, skip a turn, keep track of new winner
            log_info("NO BET. WAITING A TURN")
            just_won = False
            previous_winner = outcome
            continue
        else:
            current_bet_position = previous_winner
            if losing_streak > 0:
                bet = losing_arr[losing_streak]
            else:
                bet = 25
        log_info("Bet " + str(bet) + " on previous winner ", end = "")

        # log what the gambler bet on
        print_gambler_bet(previous_winner)

        # update winning/losing streak
        if outcome == previous_winner:
            log_info("WON. STREAK", end=" ")
            winning_streak += 1
            losing_streak = 0
            log_info(str(winning_streak))
        else:
            log_info("LOST. STREAK", end=" ")
            winning_streak = 0
            losing_streak += 1
            log_info(str(losing_streak))

        # update bankroll based on outcome
        if outcome == current_bet_position:
            bankroll += bet
            just_won = True
            bet = 25
        else:
            bankroll -= bet

        # update ath and atl
        if(bankroll > ath):
            ath = bankroll
        if(bankroll < atl):
            atl = bankroll

        # update previous winner
        if losing_streak < 3:
            previous_winner = outcome
        
        log_info("================ CURRENT BALANCE: " + str(bankroll) + "================")
        log_info()
    return bankroll, ath, atl

def log_info(msg="", *args, end='\n'):
  if LOG_INFO:
    print(msg.format(*args), end=end)

def log_day_summary(msg="", *args, end='\n'):
  if LOG_DAY_SUMMARY:
    print(msg.format(*args), end=end)

def log_end(msg="", *args, end='\n'):
  if LOG_END:
    print(msg.format(*args), end=end)

total_end = []
total_different = []
total_backtest_play = 1000
total_days = 5000
LOG_INFO = False
LOG_DAY_SUMMARY = False
LOG_END = True

pos_days = 0
neg_days = 0
goal_hit = 0
lost_all = 0


# run backtesting for total_backtest_play rounds
for i in range(0, total_days):
    result, ath, atl = backtesting(total_backtest_play, bankroll, bet)
    log_day_summary("END: " + str(result))
    log_day_summary("P/L: " + str(int(result)-1000))
    log_day_summary("ATH: " + str(ath))
    log_day_summary("ATL: " + str(atl))   
    log_day_summary("===============================")

    if result <=0:
        total_end.append(0)
    else:
        total_end.append(result)
   
    total_different.append(result - 1000)
    
    if result <1000:
        neg_days+=1
        if result <= 0:
            lost_all+=1
    else:
        pos_days+=1
        if result >= 1500:
            goal_hit+=1

average_end = sum(total_end) / len(total_end)
average_different = sum(total_different) / len(total_different)

print("The average of END each day is " + str(average_end))
print("The average of P/L each day is " + str(average_different))
print("The total positive (+) days: " + str(pos_days))
print("The total days goal met: " + str(goal_hit))
print("The total negative (-) days: " + str(neg_days))
print("The total days lost all: " + str(lost_all))

total_different_sum = sum(total_different)

print("The sum of P/L is " + str(total_different_sum) + " after " + str(len(total_different)) + " days @ " + str(total_backtest_play) + " hands each")
