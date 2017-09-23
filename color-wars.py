#!/usr/bin/env python3
# Terminal game ColorWar
# Copyright (C) 2017 Maikel Martens

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import curses
import random
import math
from collections import defaultdict

curses.COLOR_BLUE
curses.COLOR_CYAN
curses.COLOR_GREEN
curses.COLOR_MAGENTA
curses.COLOR_RED
curses.COLOR_YELLOW


class Colors:
	BLUE = 1
	CYAN = 2
	GREEN = 3
	MAGENTA = 4
	RED = 5
	YELLOW = 6

	COLORS = [BLUE, CYAN, GREEN, MAGENTA, RED, YELLOW]


class Player:
	def __init__(self, number, color, field_size):
		self.number = number
		self.color = color
		self.cells = [[ False for col in range(field_size)] for row in range(field_size)]
		self.cell_count = 0

	def has_cell(self, row, coll):
		try:
			return self.cells[row][coll]
		except:
			return False

	def add_cell(self, row, coll):
		if not self.cells[row][coll]:
			self.cells[row][coll] = True
			self.cell_count += 1

	def qonquer_cells(self, field, other_player):
		field_size = len(field)
		cell_taken = False

		for row in range(field_size):
			for coll in range(field_size):
				if self.has_cell(row, coll):
					for n_row, n_coll in self.neighbor_fields(len(field), row, coll):
						if field[n_row][n_coll] == self.color and not self.has_cell(n_row, n_coll) and not other_player.has_cell(n_row, n_coll):
							self.add_cell(n_row, n_coll)
							cell_taken = True

		if cell_taken:
			self.qonquer_cells(field, other_player)


	def neighbor_fields(self, field_size, row, coll):
		if row - 1 >= 0:
			yield row - 1, coll
		if coll + 1 < field_size:
			yield row, coll + 1
		if row + 1 < field_size:
			yield row + 1, coll
		if coll -1 >= 0:
			yield row, coll - 1

	def pick_color(self, state, window):
		return int(window.getkey())


class BotPlayer(Player):

	def __init__(self, number, color, cells, cell_count):
		self.number = number
		self.color = color
		self.cells = cells
		self.cell_count = cell_count


	@classmethod
	def create_bot(self, player):
		return BotPlayer(
			player.number,
			player.color,
			player.cells,
			player.cell_count
		)


	def pick_color(self, state, window):
		# Create map
		fieldMap = [[0 for coll in range(state.field_size)] for row in range(state.field_size)]

		for row in range(state.field_size):
			for coll in range(state.field_size):
				if not self.cells[row][coll]:
					continue
				for n_row, n_coll in self.neighbor_fields(state.field_size, row, coll):
					if state.cell_free(n_row, n_coll):
						fieldMap[n_row][n_coll] = state.field[n_row][n_coll]


		self.find_same_neighbor_colors(state, fieldMap)

		colorCount = defaultdict(int)
		for row in range(state.field_size):
			for coll in range(state.field_size):
				colorCount[fieldMap[row][coll]] += 1

		if 0 in colorCount:
			del colorCount[0]

		colors = sorted(colorCount, key=lambda x: colorCount[x], reverse=True)
		for color in colors:
			if state.color_free(color):
				return color

		while True:
			color = state.generate_random_color()
			if state.color_free(color):
				return color

	def find_same_neighbor_colors(self, state, colorField):
		field_size = len(state.field)
		cell_taken = False

		for row in range(field_size):
			for coll in range(field_size):
				if not colorField[row][coll]:
					continue
				color = colorField[row][coll]
				
				for n_row, n_coll in self.neighbor_fields(field_size, row, coll):
					if state.cell_free(n_row, n_coll) and state.field[n_row][n_coll] == color and not colorField[n_row][n_coll]:
						colorField[n_row][n_coll] = color
						cell_taken = True

		if cell_taken:
			self.find_same_neighbor_colors(state, colorField)

		return colorField


class GameState:
	def __init__(self, field_size):
		self.field_size = field_size
		self.current_player = None
		self.other_player = None
		self.field = None

		self.reset()

	def reset(self):
		self.current_player = self.generate_player(1, [])
		self.other_player = BotPlayer.create_bot(self.generate_player(2, [self.current_player.color]))

		self.field = defaultdict(dict)
		for row in range(self.field_size):
			for col in range(self.field_size):
				self.field[row][col] = self.generate_random_color()

		# Set start color other player
		self.field[0][self.field_size - 1] = self.other_player.color
		self.other_player.add_cell(0, self.field_size - 1)

		# Set start color current player
		self.field[self.field_size - 1][0] = self.current_player.color
		self.current_player.add_cell(self.field_size - 1, 0)

		# check if also has nearby fields
		self.current_player.qonquer_cells(self.field, self.other_player)
		self.other_player.qonquer_cells(self.field, self.current_player)

	def qonquer_cells(self):
		self.current_player.qonquer_cells(self.field, self.other_player)

	def game_won(self):
		max_cells = self.field_size * self.field_size
		
		if self.current_player.cell_count + self.other_player.cell_count >= max_cells:
			return True

		if self.current_player.cell_count + self.other_player.cell_count >= (max_cells * 0.9):
			if self.current_player.cell_count > (max_cells / 2):
				return True
			if self.other_player.cell_count > (max_cells / 2):
				return True
			pass

		return False

	def player_won(self):
		max_cells = self.field_size * self.field_size
		
		if self.current_player.cell_count > (max_cells / 2):
				return self.current_player
		if self.other_player.cell_count > (max_cells / 2):
			return self.other_player

		return None

	def cell_free(self, row, coll):
		return not self.current_player.has_cell(row, coll) and not self.other_player.has_cell(row, coll)

	def color_free(self, color):
		return not (self.current_player.color == color or color == self.other_player.color)

	def switch_players(self):
		self.current_player, self.other_player = self.other_player, self.current_player

	def generate_player(self, number, colors_taken):
		while True:
			player = Player(number, self.generate_random_color(), self.field_size)
			if player.color not in colors_taken:
				break
		return player

	def generate_random_color(self):
		return random.choice(Colors.COLORS) 


class GameEngine:
	FIELD_SIZE = 25

	def __init__(self):
		self.state = GameState(self.FIELD_SIZE)

	def __call__(self, window):
		self.window = window
		self.wfield = curses.newwin(self.FIELD_SIZE + 1, self.FIELD_SIZE * 2 + 2, 0, 0)
		self.waction = curses.newwin(1, 80, self.FIELD_SIZE + 1, 0)
		self.wcolors = curses.newwin(3, 80, self.FIELD_SIZE + 3, 0)

		self.window.clear()
		self.window.refresh()

		curses.curs_set(0)

		curses.init_pair(Colors.BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(Colors.CYAN, curses.COLOR_WHITE, curses.COLOR_CYAN)
		curses.init_pair(Colors.GREEN, curses.COLOR_WHITE, curses.COLOR_GREEN)
		curses.init_pair(Colors.MAGENTA, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
		curses.init_pair(Colors.RED, curses.COLOR_WHITE, curses.COLOR_RED)
		curses.init_pair(Colors.YELLOW, curses.COLOR_WHITE, curses.COLOR_YELLOW)

		self.loop()

	def loop(self):
		while True:
			self.render_field()
			self.render_action()
			self.render_colors()

			try:
				color = self.state.current_player.pick_color(self.state, self.window)
			except KeyboardInterrupt:
				sys.exit(1)
			except:
				continue

			if color not in Colors.COLORS or color == self.state.current_player.color or color == self.state.other_player.color:
				continue

			# change player color
			self.state.current_player.color = color

			# check cells
			self.state.qonquer_cells()
			self.state.switch_players()

			if self.state.game_won():
				player = self.state.player_won()
				percent = int(math.ceil((player.cell_count / float(self.FIELD_SIZE * self.FIELD_SIZE)) * 100))
				if player:
					self.render_action('Player {} has won with {}%, hit N to start new game!'.format(player.number, percent))
				else:
					self.render_action('Tie (50%), hit N to start new game!')

				self.render_field()

				while True:
					try:
						key = self.window.getkey()

						if str(key).lower() == 'n':
							break
					except KeyboardInterrupt:
						sys.exit(0)
				
				self.state.reset()


	# Render logic
	# -------------------------------------------------------------------------

	def render_field(self):
		self.wfield.clear()

		for row in range(self.FIELD_SIZE):
			for coll in range(self.FIELD_SIZE):
				color = self.state.field[row][coll]

				if self.state.current_player.has_cell(row, coll):
					color = self.state.current_player.color

				if self.state.other_player.has_cell(row, coll):
					color = self.state.other_player.color

				self.wfield.addstr(row, coll * 2, ' ', curses.color_pair(color))
				self.wfield.addstr(row, coll * 2 + 1, ' ', curses.color_pair(color))

		# render player number
		if self.state.current_player.number == 1:
			self.wfield.addstr(0, self.FIELD_SIZE * 2 - 1, '2', curses.color_pair(self.state.other_player.color))
			self.wfield.addstr(self.FIELD_SIZE - 1, 0, '1', curses.color_pair(self.state.current_player.color))
		else:
			self.wfield.addstr(0, self.FIELD_SIZE * 2 - 1, '2', curses.color_pair(self.state.current_player.color))
			self.wfield.addstr(self.FIELD_SIZE - 1, 0, '1', curses.color_pair(self.state.other_player.color))

		self.wfield.refresh()

	def render_action(self, won_message=None):
		self.waction.clear()
		
		message = 'Player {} choise your color!'.format(self.state.current_player.number)
		if won_message:
			message = won_message

		self.waction.addstr(0, 0, str(message))
		self.waction.refresh()

	def render_colors(self):
		self.wcolors.clear()

		for index, color in enumerate(Colors.COLORS):
			letter = ' ' if self.state.color_free(color) else '#'
			for row in range(3):
				for coll in range(3):
					self.wcolors.addstr(row, coll + (index * 8), letter, curses.color_pair(color))
					self.wcolors.addstr(row, coll + (index * 8) + 1, letter, curses.color_pair(color))
					self.wcolors.addstr(row, coll + (index * 8) + 2, letter, curses.color_pair(color))
			self.wcolors.addstr(1, coll + (index * 8), str(color), curses.color_pair(color))


		self.wcolors.refresh()

game = GameEngine()
try:
	curses.wrapper(game)
except KeyboardInterrupt:
	sys.exit(0)
