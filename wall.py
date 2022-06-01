import pygame


class Wall:
	def __init__(self, x, y, size=64, color=(0, 0, 0)):
		self.x = x
		self.y = y
		self.color = color
		self.body = pygame.Rect(x, y, 0, 0).inflate(size, size)

	def update(self, delta, players, entities, junkyard, map_width, map_height):
		pass

	def draw(self, window, camera):
		projected_x, projected_y = camera.project(self, window)
		projected_body = self.body.copy()
		projected_body.center = (projected_x, projected_y)
		pygame.draw.rect(window, self.color, projected_body)
