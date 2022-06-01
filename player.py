import math
import random
import numpy
import pygame
from pygame.constants import *

from wall import Wall
from utility import point_angle_degrees, rotate_point_origin_angle

pygame.font.init()
name_font = pygame.font.Font(None, 20)


class Player:
	def __init__(self, player_id, x=0, y=0, name=""):
		self.spawn_lock = False
		self.player_id = player_id
		self.x = x
		self.y = y
		self.name = name
		self.speed = 0.4
		self.radius = 32
		self.angle = 0
		self.cooldown = 0
		self.health = 5
		self.kills = 0
		self.deaths = 0
		self.color = (random.random() * 200, random.random() * 200, random.random() * 200)
		self.body = pygame.Rect(x, y, 0, 0).inflate(math.sqrt(2) * self.radius, math.sqrt(2) * self.radius)

	def update(self, delta, server, entities, camera, window, map_width, map_height):
		# get pressed keys and movement direction
		pressed_keys = pygame.key.get_pressed()
		horizontal = pressed_keys[K_d] - pressed_keys[K_a]
		vertical = pressed_keys[K_s] - pressed_keys[K_w]

		# update position of self and body
		self.body.centerx += horizontal * self.speed * delta
		for entity in entities:
			if type(entity) == Wall:
				if self.body.colliderect(entity.body):
					if self.body.left < entity.body.right and horizontal == -1:
						self.body.left = entity.body.right
					elif self.body.right > entity.body.left and horizontal == 1:
						self.body.right = entity.body.left
		self.body.centery += vertical * self.speed * delta
		for entity in entities:
			if type(entity) == Wall:
				if self.body.colliderect(entity.body):
					if self.body.top < entity.body.bottom and vertical == -1:
						self.body.top = entity.body.bottom
					elif self.body.bottom > entity.body.top and vertical == 1:
						self.body.bottom = entity.body.top
		self.body.centerx = numpy.clip(self.body.centerx, -8, map_width - 56)
		self.body.centery = numpy.clip(self.body.centery, -8, map_height - 56)
		self.update_position_body()

		# update own angle
		projected_x, projected_y = camera.project(self, window)
		mouse_x, mouse_y = pygame.mouse.get_pos()
		self.angle = point_angle_degrees(projected_x, projected_y, mouse_x, mouse_y)

		# shooting
		if self.cooldown > 0:
			self.cooldown -= delta
		if pygame.mouse.get_pressed(3)[0]:
			if self.cooldown <= 0:
				self.cooldown = 200
				server.send("create_bullet")

	def draw(self, window, camera):
		projected_x, projected_y = camera.project(self, window)

		# set up and draw barrel
		barrel = pygame.Surface((64, 16))
		barrel.set_colorkey((0, 0, 0))
		barrel.fill((100, 100, 100))
		barrel = pygame.transform.rotate(barrel, self.angle)
		barrel_rect = barrel.get_rect()
		barrel_x, barrel_y = rotate_point_origin_angle(projected_x, projected_y, projected_x + 32, projected_y, self.angle)
		barrel_rect.center = barrel_x, barrel_y
		window.blit(barrel, barrel_rect)

		# draw player
		pygame.draw.circle(window, self.color, (projected_x, projected_y), self.radius)
		name_display = name_font.render(self.name, True, (255, 255, 255))
		window.blit(name_display, (projected_x - name_display.get_width() / 2,
								   projected_y - name_display.get_height() / 2))
		health_display = name_font.render("["+str(self.health)+"]", True, (255, 255, 255))
		window.blit(health_display, (projected_x - health_display.get_width() / 2,
									 projected_y - health_display.get_height() / 2 - 16))
		killdeath_string = str(self.kills) + ' / ' + str(self.deaths)
		killdeath_display = name_font.render(killdeath_string, True, (255, 255, 255))
		window.blit(killdeath_display, (projected_x - killdeath_display.get_width() / 2,
									    projected_y - killdeath_display.get_height() / 2 + 16))

	def update_position_body(self):
		self.x = self.body.centerx
		self.y = self.body.centery
