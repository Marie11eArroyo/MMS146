import random
import os
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

    def reveal(self):
        return self.symbol if self.is_matched else "*"
    
    def tempreveal(self): #edited by Justine. Renamed from hide(self) because it was unused anyway. Converted it to a second reveal method that just temporarily reveals the symbol of a card.
        #return "*" if not self.is_matched else self.symbol
        return self.symbol

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

    def display(self):                      #Added by Kevin. This is to show the current state of the board.
        for row in self._grid_of_cards:
            print(" ".join(card.reveal() for card in row))

class MemoryGame:
    def __init__(self, player_name):
        self.game_board = GameBoard()
        self.hint_system = Hint(self.game_board)              #Added by Kevin. A hint system.
        self.moves_counter = 0
        self.matched_pairs = [ ]
        self.player_name = player_name
        self.scores_file = "./scores.text"

    def flip_card(self, row, col): #edited by Manuel. Switched it over to Justine's implementation.
        card = self.game_board._grid_of_cards[row-1] [col-1] #edited by Justine. Added a "-1" for both row and column values. Without this decrement, the first row and column will be numbered ZERO, which is confusing for the player.
        if row==0 or col==0: raise ValueError #introduced by Justine. Row/column values cannot be zero because they are numbered 1 to 6.
        print(f"Card at ({row}, {col}) : {card.tempreveal()}") #edited by Manuel. Switched it over to Justine's implementation.
        return card

    def check_match(self, first_card, second_card):
        if first_card.symbol == second_card.symbol:
            first_card.is_matched = True
            second_card.is_matched = True
            self.matched_pairs.append((first_card, second_card))
            return True
        return False

    def update_board(self):
        self.game_board.display()

    def display_end_game_message(self):
        print(f"Congratulations!, {self.player_name} Completed the game in {self.moves_counter} moves.")
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
        while len(self.matched_pairs) < (self.game_board._board_size * self.game_board._board_size) // 2:
            self.update_board()
            # Added by Kevin from adding HintySystem class.
            hint = input("Would you like a hint? (yes/no): ").strip().lower()
            if hint == 'yes':
                self.hint_system.provide_hint()

            try:
                row1, col1 = map(int, input("Enter the first card (row col): ").split())
                first_card = self.flip_card(row1, col1)
                row2, col2 = map(int, input("Enter the second card (row col): ").split())	
                second_card = self.flip_card(row2, col2)
                self.moves_counter +=1
                if not self.check_match(first_card, second_card):
                    print("No match. Try again.")
                else:
                    print("Match!")
            except (ValueError, IndexError):
                print("Invalid input. Please enter valid row and column numbers.")

        self.dislay_end_game_message()
        self.display_hall_of_fame()
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

# Start the game

player_name = input("Enter your name: ")
game = MemoryGame(player_name)
''' Test with this for base game funct.
game.play()
'''
''' Test with this for save score funct.
game.display_end_game_message()
game.display_end_game_message()
game.display_end_game_message()
game.display_hall_of_fame()
'''
