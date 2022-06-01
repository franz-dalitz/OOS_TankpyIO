"""
main server script for running TankPyIO server for a local network
"""
import socket
from _thread import *
import _pickle as pickle
import time

import pygame.event

from bullet import Bullet
from player import *
from maps import maps
from wall import Wall
from utility import *

# constants
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
PORT = 5555
HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

TILE_SIZE = 64
while True:
	try:
		MAP_NAME = input('[SERVER] Enter map name: ')
		MAP = maps[MAP_NAME]
		break
	except:
		print('[SERVER] Map with given name could not be found')
MAP_WIDTH, MAP_HEIGHT = len(MAP[0]) * TILE_SIZE, len(MAP) * TILE_SIZE
PLAYER_SPAWNS = []

FRAME_RATE = 60

# try to connect to server
try:
	SERVER_SOCKET.bind((SERVER_IP, PORT))
except socket.error as error:
	print(str(error))
	print("[SERVER] Server could not start")
	quit()

# listen for connections
SERVER_SOCKET.listen()
print(f"[SERVER] Server started with local ip: {SERVER_IP}")

# dynamic variables
players = {}
entities = []
junkyard = []
id_counter = 0


# functions
def get_start_position():
	"""
	picks a start location for a player based on other player
	locations. It will ensure it does not spawn inside another player
	:return: tuple (x,y)
	"""
	spawn_copy = PLAYER_SPAWNS.copy()
	while True:
		stop = True
		if len(spawn_copy) > 0:
			spawn_index = random.randint(0, len(spawn_copy) - 1)
			spawn_x, spawn_y = spawn_copy[spawn_index]
			for player_key in players:
				player = players[player_key]
				distance = math.sqrt(pow(player.x - spawn_x, 2) + pow(player.y - spawn_y, 2))
				if distance < TILE_SIZE * 2:
					stop = False
					del spawn_copy[spawn_index]
					break
		else:
			spawn_x, spawn_y = random.choice(PLAYER_SPAWNS)
		if stop:
			break
	return spawn_x, spawn_y


def threaded_client(connection, client_id):
	"""
	runs in a new thread for each player connected to the server
	:param connection: ip address of connection
	:param client_id: id of the client
	:return: None
	"""
	global players, entities
	current_id = client_id

	# receive a name from the client and setup the new player
	name = connection.recv(16).decode("utf-8")
	print("[SERVER]", name, client_id, "connected to the server")
	player_x, player_y = get_start_position()
	players[current_id] = Player(current_id, player_x, player_y, name)
	connection.send(str.encode(str(current_id)))

	# server will receive basic commands from client
	# it will send back all of the other clients info
	while True:
		try:
			# receive data from client
			data = connection.recv(2048 * 16)
			if not data:
				break
			data = data.decode("utf-8")

			# look for specific commands from received data
			if data.split(" ")[0] == "update":
				player = pickle.loads(bytes(data[7:], 'latin1'))
				player.kills = players[current_id].kills
				player.deaths = players[current_id].deaths
				player.health = players[current_id].health
				if players[current_id].spawn_lock:
					player.spawn_lock = False
					player.body.centerx = players[current_id].body.centerx
					player.body.centery = players[current_id].body.centery
				players[current_id] = player
				send_data = pickle.dumps((entities, players))
			elif data.split(" ")[0] == "id":
				send_data = str.encode(str(current_id))
			elif data.split(" ")[0] == "map_dimensions":
				send_data = str.encode(str(MAP_WIDTH) + ' ' + str(MAP_HEIGHT))
			elif data.split(" ")[0] == "create_bullet":
				bullet_x, bullet_y = rotate_point_origin_angle(players[current_id].x, players[current_id].y,
															   players[current_id].x + 56, players[current_id].y,
															   players[current_id].angle)
				new_bullet = Bullet(current_id, bullet_x, bullet_y, players[current_id].angle, players[current_id].color)
				entities.append(new_bullet)
			else:
				# any other command just fetches all information, main use is "get" command
				send_data = pickle.dumps((entities, players))

			# send data back to clients
			connection.send(send_data)

		except Exception as error:
			print(error)
			break  # if an exception has been reached disconnect client

		time.sleep(0.001)

	# When user disconnects
	print("[SERVER]", name, client_id, "has disconnected from the server")
	del players[current_id]  # remove client information from players list
	connection.close()  # close connection


def threaded_game_server_side():
	server_clock = pygame.time.Clock()
	while True:
		delta = server_clock.tick(FRAME_RATE)
		for entity in entities:
			if type(entity) == Bullet:
				player_hit = entity.update(delta, players, entities, junkyard, MAP_WIDTH, MAP_HEIGHT)
				if player_hit is not None:
					players[player_hit].health -= 1
					if players[player_hit].health == 0:
						players[entity.player_id].kills += 1
						players[player_hit].deaths += 1
						players[player_hit].health = 5
						players[player_hit].body.centerx, players[player_hit].body.centery = get_start_position()
						players[player_hit].spawn_lock = True
		for junk in junkyard:
			if junk in entities:
				entities.remove(junk)
				del junk
		junkyard.clear()


# on startup
print("[SERVER] Loading game map")
tile_x = tile_y = 0
for row in MAP:
	for tile in row:
		if tile == 'X':
			entities.append(Wall(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE))
		elif tile == ' ':
			PLAYER_SPAWNS.append((tile_x * TILE_SIZE, tile_y * TILE_SIZE))
		tile_x += 1
	tile_y += 1
	tile_x = 0
print("[SERVER] Waiting for connections")
start_new_thread(threaded_game_server_side, ())

# keep looping to accept new connections
while True:
	host, address = SERVER_SOCKET.accept()
	start_new_thread(threaded_client, (host, id_counter))
	id_counter += 1
