import math
import random

import pygame

from wall import Wall


class Bullet:
	def __init__(self, player_id, x, y, angle, color=(0, 0, 0)):
		self.player_id = player_id
		self.x = x
		self.y = y
		self.x_vel = -math.cos(math.radians(angle + 180))
		self.y_vel = math.sin(math.radians(angle + 180))
		self.radius = 8
		self.body = pygame.Rect(x, y, 0, 0).inflate(math.sqrt(2) * self.radius, math.sqrt(2) * self.radius)
		self.speed = .8
		self.color = color

	def update(self, delta, players, entities, junkyard, map_width, map_height):
		# update position
		self.x += self.x_vel * self.speed * delta
		self.y += self.y_vel * self.speed * delta
		self.body.center = (self.x, self.y)

		# delete if out of bounds
		if self.x < -32 or self.x > map_width - 32:
			junkyard.append(self)
		elif self.y < -32 or self.y > map_height - 32:
			junkyard.append(self)

		# delete on wall hit
		for entity in entities:
			if type(entity) == Wall:
				if self.body.colliderect(entity.body):
					junkyard.append(self)

		# trigger player collision
		for player_key in players:
			player = players[player_key]
			if player.body.colliderect(self.body):
				if player.player_id != self.player_id:
					junkyard.append(self)
					return player_key

		return None

	def draw(self, window, camera):
		projected_x, projected_y = camera.project(self, window)
		pygame.draw.circle(window, self.color, (projected_x, projected_y), self.radius)

	def destroy(self, game_instance):
		game_instance.junkyard.append(self)