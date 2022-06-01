import pickle
import pygame
from pygame.constants import *

from network import Network
from utility import Camera

# constants
WINDOW_WIDTH, WINDOW_HEIGHT = 0, 0
MAP_WIDTH, MAP_HEIGHT = 0, 0
FRAME_RATE = 60

# dynamic variables
players = {}
entities = []
camera = Camera()


# functions
def redraw_window():
	"""
	draws each frame
	:return: None
	"""
	WINDOW.fill((30, 30, 30))  # fill screen white, to clear old frames
	pygame.draw.rect(WINDOW, (255, 255, 255), (0 - camera.x + WINDOW.get_width() / 2 - 32,
											   0 - camera.y + WINDOW.get_height() / 2 - 32,
											   MAP_WIDTH-1, MAP_HEIGHT-1))

	# draw all entities
	for entity in entities:
		entity.draw(WINDOW, camera)

	# draw each player in the list
	for player_key in players.keys():
		player = players[player_key]
		player.draw(WINDOW, camera)


def run_client():
	"""
	function for running the game,
	includes the main loop of the game
	:return: None
	"""
	global players, entities, name, MAP_WIDTH, MAP_HEIGHT, WINDOW, WINDOW_WIDTH, WINDOW_HEIGHT

	# variables and connecting to the server
	pygame.init()
	server = Network()
	print("[CLIENT] Trying to find server and connect")
	while True:
		try:
			current_id = server.connect(name)
			break
		except:
			pass
	print("[CLIENT] Server found, connected")
	map_dimensions = server.send("map_dimensions").decode().split(" ")
	MAP_WIDTH, MAP_HEIGHT = int(map_dimensions[0]), int(map_dimensions[1])
	clock = pygame.time.Clock()
	run = True

	# setup pygame window
	WINDOW = pygame.display.set_mode()
	WINDOW_WIDTH = WINDOW.get_width()
	WINDOW_HEIGHT = WINDOW.get_height()
	pygame.display.set_caption("TankPy.IO")

	while run:
		delta = clock.tick(FRAME_RATE)
		entities, players = server.send("get")
		player = players[current_id]
		player.update(delta, server, entities, camera, WINDOW, MAP_WIDTH, MAP_HEIGHT)
		camera.update(player)
		server.send("update " + str(pickle.dumps(player), encoding='latin1'))

		for event in pygame.event.get():
			if event.type == QUIT:
				run = False
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					run = False

		# redraw window then update the frame
		redraw_window()
		pygame.display.flip()

	server.disconnect()
	pygame.quit()
	print("[CLIENT] Offline")
	quit()


# get users name
name = ""
while True:
	name = input("[CLIENT] Enter your name: ")
	if 0 < len(name) <= 10:
		break
	else:
		print("[CLIENT] This name is not allowed (must be between 1 and 10 characters")

# start game
run_client()
