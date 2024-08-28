import random
import os
import time #Anne imported time to add the Timer class
from abc import ABC, abstractmethod

# abstract base class
class Game(ABC):
	@abstractmethod
	def play(self):
		pass

class Card:
    def __init__(self, symbol):
        self.symbol = symbol
        self.is_matched = False
        self.is_shown = False #Added by Lanz. Used to temporarily reveal symbols.

    def reveal(self):
        return self.symbol if self.is_matched or self.is_shown else "*"
    
    def tempreveal(self): #Renamed from hide(self) by Justine. Edited by Lanz. Used to temporarily reveal symbols.
    	self.is_shown = True

    def temphide(self):
        self.is_shown = False

class GameBoard:
    def __init__(self, board_size=6):
        self._board_size = board_size
        self._grid_of_cards = self._setup_board()

    def _setup_board(self): 
            symbols = [chr(i) for i in range(65, 65 + (self._board_size * self._board_size) // 2)]
            symbols *= 2
            random.shuffle(symbols)
            
            board = [ ]
            for i in range(self._board_size):
                row = [ ]
                for j in range(self._board_size):
                    row.append(Card(symbols.pop()))
                board.append(row)
            return board

    def display(self):#Added by Kevin, Modified by Lanz. This is to show the current state of the board.
        i=0
        j=0
        for row in self._grid_of_cards:
            j+=1
        for card in row:
            i+=1
        for row,l in zip(self._grid_of_cards,range(i)):
            print(' '.join(f'+{l+1},{k+1}+' for k in range(j)))
            print(' '.join(f'| {card.reveal()} |' for card in row))
            print(' '.join(f'+---+' for card in row))

    def hide(self):
        for row in self._grid_of_cards:
            for card in row:
                card.temphide()

class MemoryGame:
    def __init__(self, player_name):
        self.game_board = GameBoard()
        self.hint_system = LimitedHints(self.game_board, max_hints=3)              #Added by Kevin. A hint system.	#Arianna added Limited hints to introduce a controlled, more challenging hint system for the players.
        self.moves_counter = 0
        self.matched_pairs = [ ]
        self.player_name = player_name
        self.scores_file = "./scores.text"
        self.timer = Timer() #Anne added Timer class
        self.flipped_rows_cols = [ ] #added by Justine to keep track of row and column numbers of cards that were already matched

    def start_game(self):
        self.timer.start() #Anne added this to run Timer class. Begins counting time when player starts.

    def flip_card(self, row, col): #edited by Manuel. Switched it over to Justine's implementation.
        card = self.game_board._grid_of_cards[row-1] [col-1] #edited by Justine. Added a "-1" for both row and column values. Without this decrement, the first row and column will be numbered ZERO, which is confusing for the player.
        if row==0 or col==0:
            raise ValueError("Ensure that row and columns fit the board size properly.") #introduced by Justine. Row/column values cannot be zero because they are numbered 1 to 6.
            #Anne added an error message after ValueError.
        if (row, col) in self.flipped_rows_cols: #added by Justine. Now checks whether the selected card has already been flipped or not. If flipped, the move is considered invalid.
            raise ValueError("Please pick an unmatched card!")
        card.tempreveal() #edited by Manuel. Switched it over to Justine's implementation.
        return card

    def check_match(self, first_card, second_card):
        if first_card.symbol == second_card.symbol:
            first_card.is_matched = True
            second_card.is_matched = True
            self.matched_pairs.append((first_card.symbol, second_card.symbol)) #edited by Justine. Now appends the cards' symbols onto the list instead of the objects themselves (thus making the list printable).
            return True
        return False

    def end_game(self):
        self.timer.stop() #Anne added this to run Timer class. Stops counting time when player stops.
        '''
        Anne moved the two instances from the bottom to here under the end_game method.
        '''
        self.display_end_game_message() #Anne changed the typo from 'dislay' to 'display' to prevent errors from running.
        self.display_hall_of_fame()

    def update_board(self):
        self.game_board.display()

    def display_end_game_message(self):
        elapsed_time = self.timer.elapsed() #Anne added this to show how much time the player took to complete the game>
        print(f"Congratulations! {self.player_name} completed the game in {self.moves_counter} moves!") #edited by Justine to fix minor capitalization/punctuation issues.
        self.save_score(self.moves_counter)

    def save_score(self, score):
        with open(self.scores_file, "a") as file:
            file.write(f"{self.player_name},{score}\n")

    def display_hall_of_fame(self):
        if not os.path.exists(self.scores_file):
            print("Your scores could not be retrieved.")
            return
        else: # introduced by Manuel. Made it read out the scores of the player from the file. Persists beyond new iterations as long as record isnt lost.
            print("---« HALL OF FAME »---")
            scores = open(self.scores_file, 'r')
            print(scores.read())
            scores.close()

    def play(self):
        self.start_game() #Anne added this to begin counting time as player starts.
        while len(self.matched_pairs) < (self.game_board._board_size * self.game_board._board_size) // 2:
            self.update_board()
            self.game_board.hide()

            if self.hint_system.hintlimitreached() is False: #added by Justine to check whether all hints have been used up. If they have, the program no longer asks if the player wants a hint.
                # Added by Kevin from adding HintySystem class.
                hint = input("Would you like a hint? (y/n): ").strip().lower() #edited by Justine to simplify the input required to ask for a hint
                if hint == 'yes' or hint == 'y': #edited by Justine to simplify the input required to ask for a hint
                    self.hint_system.provide_hint()
                os.system('cls')
                print(f'Moves: {self.moves_counter}')
                self.update_board()

            try:
                row1, col1 = map(int, input("Enter the first card (row col): ").split())
                first_card = self.flip_card(row1, col1)
                os.system('cls')
                print(f'Moves: {self.moves_counter}')
                self.update_board()
                row2, col2 = map(int, input("Enter the second card (row col): ").split())	
                second_card = self.flip_card(row2, col2)
                os.system('cls')
                self.moves_counter +=1
                if row1==row2 and col1==col2: #re-introduced by Justine. Prevents cases where a player picks the same card twice and causes it to match by itself.
                    print("You chose the same card twice! Try again.")
                elif not self.check_match(first_card, second_card): #edited by Justine
                    print("No match. Try again.")
                else:
                    print("Match!")
                    self.flipped_rows_cols.append((row1, col1)) #added by Justine. Keeps track of row and column combinations that have already been matched successfully.
                    self.flipped_rows_cols.append((row2, col2)) #added by Justine. Keeps track of row and column combinations that have already been matched successfully.
            except (ValueError, IndexError):
                os.system('cls')
                print("Invalid input. Please enter valid row and column numbers.")
        self.end_game() #Anne added this to stop counting time as player starts.

    def restart_game (self): 
        self.timer.stop()
        restart = input ("start new game? (yes/no): ")
        if restart == 'yes':
            self.game_board._setup_board()
            self.start_game()
            print ("Game has restarted.")
        elif restart == 'no':
            self.timer.elapsed()


class Hint:      #Added by Kevin. 
    def __init__(self, game_board):
        self.game_board = game_board

    def find_unmatched_pair(self):
        # Collect all unmatched cards
        unmatched_cards = []
        for i, row in enumerate(self.game_board._grid_of_cards):
            for j, card in enumerate(row):
                if not card.is_matched:
                    unmatched_cards.append((i, j, card))

        # Try to find a matching pair among unmatched cards
        for idx1, (row1, col1, card1) in enumerate(unmatched_cards):
            for row2, col2, card2 in unmatched_cards[idx1 + 1:]:
                if card1.symbol == card2.symbol:
                    return (row1 + 1, col1 + 1), (row2 + 1, col2 + 1)
        
        return None  # No unmatched pair found

    def provide_hint(self):
        hint = self.find_unmatched_pair()
        if hint:
            (row1, col1), (row2, col2) = hint
            print(f"Hint: Try flipping cards at ({row1}, {col1}) and ({row2}, {col2}).")
        else:
            print("No hints available.")

#Arianna added class LimitedHints to maintain the challenge and balance of the game.
class LimitedHints(Hint): 
    def __init__(self, game_board, max_hints=3):
        super().__init__(game_board)
        self.hints_used = 0
        self.max_hints = max_hints

    def provide_hint(self):
        if self.hints_used < self.max_hints:
            super().provide_hint()
            self.hints_used += 1
            print(f"Hints used: {self.hints_used}/{self.max_hints}")
        else:
            print("No more hints available.")

    def hintlimitreached(self): #added by Justine to check whether all hints have been used up already.
	    if self.hints_used >= self.max_hints:
		    return True
	    else:
		    return False
	
class Timer: #Anne added class Timer to keep track of how long a player takes to complete the game.
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
    
    def start(self):
        self.start_time = time.time()
    
    def stop(self):
        self.end_time = time.time()
    
    def elapsed(self):
        if self.start_time !=0 and self.end_time !=0:
            return self.end_time - self.start_time
        return 0

def PlayGame(): # Start the game, Modified by Manuel
    player_name = input("Enter your name: ")
    game = MemoryGame(player_name)
    '''game.play()'''


# Creates a loop for repetative gameplay, by Manuel
if __name__ == "__main__":
    loopActive = True

    while loopActive == True:
        PlayGame()
        if input("Play again? Yes/No\n") == "No":
            loopActive = False
