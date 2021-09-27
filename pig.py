#!/usr/bin/env python3

"""A dice game modeled after the traditional game Pig"""
import time
import random
import sys

class Player:
    """Player Class for the game"""
    def __init__(self, name, player_id=0):
        self._name = name
        self._roll_order = 0
        self._pid = player_id
        self._score = 0
        self._tempscore = 0
        self._number_rolls = 0
    def __str__(self):
        return self._name
    def __roll_order(self):
        return self._roll_order
    def score(self):
        """returns total score"""
        return self._score
    def number_rolls(self):
        """returns number of rolls"""
        return self._number_rolls
    def roll_order(self, roll):
        """returns the roll order number"""
        self._roll_order = roll
    def will_roll(self):
        """Prompts Player if they want to roll or cash in dice points"""
        print('Would you like to start to roll or continue rolling?')
        print('Please enter "y" for yes or "n" for hold your turn.')
        answer = (input('>') == 'y')
        print()
        if answer:
            self.dice_roll()
        elif not answer and self._number_rolls > 0:
            print(self._name + " holding their turn....")
            self._score += self._tempscore
            self._tempscore = 0
            self._number_rolls = 0
            print("Current score: ", self._score)
        else:
            print("Cannot hold your turn at the before you have rolled at least once.")
            print("Please choose again.")
            print()
            self.will_roll()
    def dice_roll(self):
        """Presents the amount before you roll your dice and also rolls the dice"""
        answer = 0
        print("************************")
        print("Total Score: ", self._score)
        print("Turn Score: ", self._tempscore)
        print("Times Rolled: ", self._number_rolls)
        print()
        time.sleep(.5)
        print("Rolling the dices...")
        answer = random.randint(1, 6)
        print("The values is ", answer)
        print()
        self._number_rolls += 1
        if answer == 1:
            print("Your score will be emptied, turn ends")
            print("Total score: ", self._score)
            time.sleep(2)
            self._tempscore = 0
            self._number_rolls = 0
            print()
        else:
            self._tempscore += answer
            self.will_roll()


class AIPlayer(Player):
    """AI Class for the game, inherits Player class"""
    def __init__(self):
        super().__init__('Sup_Bot', 42)
        self._firstroll = 0
    def will_roll(self):
        time.sleep(2)
        print('Would you like to start to roll or continue rolling?')
        print('Please enter "y" for yes or "n" for hold your turn.')
        if self._firstroll == 0:
            print(">y")
            print()
            time.sleep(1)
            self._number_rolls += 1
            self._firstroll = 1
            self.dice_roll()
        else:
            random_choice = random.randint(1, 10)
            if 1 <= random_choice <= 5:
                if self._tempscore <= 3:
                    print(">y")
                    print()
                    time.sleep(1)
                    self._number_rolls += 1
                    self.dice_roll()
                elif self._tempscore >= 3 and self._number_rolls > 0:
                    print(">n")
                    print()
                    time.sleep(1)
                    print(self._name + " holding their turn....")
                    self._score += self._tempscore
                    self._tempscore = 0
                    self._number_rolls = 0
                    print("Total score: ", self._score)
                    self._firstroll = 0
            elif 6 <= random_choice <= 10:
                if self._tempscore <= 30:
                    print(">y")
                    print()
                    time.sleep(1)
                    self._number_rolls += 1
                    self.dice_roll()
                elif self._tempscore >= 30 and self._number_rolls > 0:
                    print(">n")
                    print()
                    time.sleep(1)
                    print(self._name + " holding their turn....")
                    self._score += self._tempscore
                    self._tempscore = 0
                    self._number_rolls = 0
                    print("Total score: ", self._score)
                    self._firstroll = 0
    def dice_roll(self):
        """Presents the amount before you roll your dice and also rolls the dice for the AI"""
        answer = 0
        print("************************")
        print("Total Score: ", self._score)
        print("Turn Score: ", self._tempscore)
        print("Times Rolled: ", self._number_rolls)
        print()
        time.sleep(.5)
        print("Rolling the dices...")
        answer = random.randint(1, 6)
        print("The values is ", answer)
        print()
        self._number_rolls += 1
        if answer == 1:
            print("Your score will be emptied, turn ends")
            print("Total score: ", self._score)
            time.sleep(2)
            self._firstroll = 0
            self._tempscore = 0
            self._number_rolls = 0
            print()
        else:
            self._tempscore += answer
            self.will_roll()
class PlayerQueue:
    """Player Queue for the Rounds"""
    def __init__(self, player_list):
        self._players = player_list
        self._counter = 0
        self._should_stop = False
    def __iter__(self):
        return self
    def __next__(self):
        if self._should_stop:
            raise StopIteration
        if self._counter >= len(self._players):
            self._counter = 0
        player = self._players[self._counter]
        self._counter = self._counter + 1
        return (self._counter, player)

def main():
    """main function for game"""
    print('Please enter a number between 2-4 for players/AI you would like to play.')
    playernum = int(input('>'))
    if not 2 <= playernum <= 4:
        print("Did not select the amount that is to play... now exiting")
        sys.exit(1)

    start_num = 1
    player_list = []
    print('It is time to decide whether the amount playing is a player or AI.')
    while playernum >= start_num:
        print('Please enter a "p" for player or anything else for AI')
        is_player = (input('>') == 'p')
        if is_player:
            print("Please enter the name for the player")
            player_name = input('>')
            player_list.append(Player(player_name))
            start_num += 1
        else:
            print("You have chosen AI computing.")
            player_list.append(AIPlayer())
            time.sleep(1)
            start_num += 1
    print()
    print("Rolling for order.")
    for player in player_list:
        player.roll_order(random.randint(1, 6))
    player_list.sort(reverse=True, key=lambda x: x._roll_order)
    print("First up:", player_list[0].__str__())
    player_queue = PlayerQueue(player_list)
    is_game_over = False
    while not is_game_over:
        for index, player in player_queue:
            print("---------------------------------------------------------------------")
            print("It is " + player.__str__() + "'s turn!")
            print()
            player.will_roll()
            if player.score() >= 100:
                print()
                print("The player " + player.__str__() + " has won!")
                is_game_over = True
                break

if __name__ == '__main__':
    main()
