#!/usr/bin/env python3
# Snake game for the terminal
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
import time
import random


class Snake:
	FPS = 12
	FIELD_SIZE = 25
	
	UP = 1
	LEFT = 2
	DOWN = 3
	RIGHT = 4

	def __init__(self):
		self.window = None
		self.board = None
		self.frame_count = 0
		self.current_fps = 0
		self.start_fps_frame = 0
		self.start_fps_time = 0

		# Game State
		self.lives = 3
		self.points = 0
		self.body = []
		self.appleCord = None
		self.direction = None

	def __call__(self, window):
		self.window = window
		self.wbar = curses.newwin(1, self.FIELD_SIZE, 0, 0)
		self.wboard = curses.newwin(self.FIELD_SIZE + 2, self.FIELD_SIZE * 2 + 6, 1, 0)
		self.winfo = curses.newwin(1, self.FIELD_SIZE * 2, self.FIELD_SIZE + 4, 0)

		self.window.clear()
		self.window.refresh()

		# Help text
		self.winfo.addstr(0, 0, "UP = K; DOWN = J; LEFT = H; RIGHT = L")

		self.winfo.refresh()

		# Hide virtual screen cursor
		curses.curs_set(0)
		self.window.nodelay(True)

		# init colors
		curses.init_pair(1, curses.COLOR_RED, 0)
		curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_YELLOW)
		curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)
		curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_WHITE)

		self.reset(True)
		self.loop()

	def reset(self, full=False):
		self.lives -= 1

		if self.lives < 1 or full:
			if full:
				self.lives = 3
			
			self.render_bar() # remove last heart
			self.wboard.clear()

			if not full:
				self.wboard.addstr(1,2, "Your final score is {}.".format(self.points))
			self.wboard.addstr(3,2, "Press a key to start!")
			self.wboard.refresh()

			self.window.nodelay(False)
			self.window.getkey()
			self.window.nodelay(True)

			self.lives = 3
			self.points = 0 

		self.direction = self.UP
		self.body = [
			[int(self.FIELD_SIZE / 2), int(self.FIELD_SIZE / 2)],
			[int(self.FIELD_SIZE / 2 - 1), int(self.FIELD_SIZE / 2)],
			[int(self.FIELD_SIZE / 2 - 2), int(self.FIELD_SIZE / 2)],
			[int(self.FIELD_SIZE / 2 - 3), int(self.FIELD_SIZE / 2)],
		]

		self.appleCord = [int(self.FIELD_SIZE / 3), int(self.FIELD_SIZE / 3)]


	def loop(self):
		while True:
			# Game FPS
			time.sleep(1 / self.FPS)
			self.frame_count += 1

			try:
				key = str(self.window.getkey()).upper()
				if (key == 'KEY_UP' or key == 'K') and self.direction != self.DOWN:
					self.direction = self.UP
				elif (key == 'KEY_RIGHT' or key == 'L') and self.direction != self.LEFT:
					self.direction = self.RIGHT
				elif (key == 'KEY_DOWN' or key == 'J') and self.direction != self.UP:
					self.direction = self.DOWN
				elif (key == 'KEY_LEFT' or key == 'H') and self.direction != self.RIGHT:
					self.direction = self.LEFT
				elif key == 'q':
					sys.exit()
			except curses.error:
				pass

			head_row, head_col = self.body[-1]
			if self.direction == self.UP:
				self.body.append([head_row - 1, head_col])
			elif self.direction == self.RIGHT:
				self.body.append([head_row, head_col + 1])
			elif self.direction == self.DOWN:
				self.body.append([head_row + 1, head_col])
			elif self.direction == self.LEFT:
				self.body.append([head_row, head_col - 1])

			head = self.body[-1]

			
			if head != self.appleCord:
				self.body = self.body[1:]
			else:
				self.points += 1
				newApple = [int(random.random() * (self.FIELD_SIZE - 2)) + 1, int(random.random() * (self.FIELD_SIZE - 2)) + 1]
				while newApple in self.body:
					newApple = [int(random.random() * (self.FIELD_SIZE - 2)) + 1, int(random.random() * (self.FIELD_SIZE - 2)) + 1]
				self.appleCord = newApple

			# Check if hit wall or own body
			if head[0] <= 0 or head[0] > self.FIELD_SIZE or head[1] <= 0 or head[1] > self.FIELD_SIZE or head in self.body[:-1]:
				self.reset()


			self.render_bar()
			self.render_board()

		

	def render_bar(self):
		self.wbar.clear()

		# Render FPS
		if time.time() - self.start_fps_time > 1:
			self.current_fps = self.frame_count - self.start_fps_frame
			self.start_fps_frame = self.frame_count
			self.start_fps_time = time.time()
		self.wbar.addstr(0, 0, 'Points: {}'.format(self.points))

		# Render Lives
		self.wbar.addstr(0, self.FIELD_SIZE - 14, 'Lives:')
		self.wbar.addstr(0, self.FIELD_SIZE - 7, '\u2764 ' * self.lives, curses.color_pair(1))

		self.wbar.refresh()

	def render_board(self):
		self.wboard.clear()

		# Border corners 
		self.wboard.addstr(0, 0, '+')
		self.wboard.addstr(0, self.FIELD_SIZE + 1, '+')
		self.wboard.addstr(self.FIELD_SIZE + 1, 0, '+')
		self.wboard.addstr(self.FIELD_SIZE + 1, self.FIELD_SIZE + 1, '+')

		
		for x in range(0, self.FIELD_SIZE + 2):
			# Up and bottom border
			self.wboard.addstr(0, x * 2, '  ', curses.color_pair(4))
			self.wboard.addstr(self.FIELD_SIZE + 1, x * 2, '  ', curses.color_pair(4))

			# Left en right border
			self.wboard.addstr(x, 0, '  ', curses.color_pair(4))
			self.wboard.addstr(x, self.FIELD_SIZE * 2 + 2, '  ', curses.color_pair(4))

		# Snake
		for part_col, part_row in self.body:
			self.wboard.addstr(part_col, part_row * 2, '  ', curses.color_pair(3))

		# Apple
		self.wboard.addstr(self.appleCord[0], self.appleCord[1] * 2, '  ', curses.color_pair(2))		
		
		self.wboard.refresh()


snake = Snake()
try:
	curses.wrapper(snake)
except KeyboardInterrupt:
	sys.exit(0)