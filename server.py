import socket
import pickle, select
from _thread import *
from random import randint
from data_structures import *

player_map = {}

server_socket = socket.socket()
server_host = socket.gethostname()
server_ip = socket.gethostbyname(server_host)
 
port = 8080
BUFFERSIZE = 2048
max_clients = 3
 
server_socket.bind((server_host, port))
print("Binding successful!")
print("This is your IP: ", server_ip)

server_socket.listen(max_clients)

def threaded_client(conn, player_id):
    while True:
        ins, _, _ = select.select([conn], [], [], 0)
        try:
            for inm in ins:
                gameEvent = pickle.loads(inm.recv(BUFFERSIZE))
                if gameEvent:
                    if gameEvent[0] == 'update_player':
                        player_map[player_id].set_position(gameEvent[1])
                        player_map[player_id].set_message(gameEvent[2])
                        conn.sendall(pickle.dumps(['update_players', player_map]))

                else:
                    print("Broke out of no gameEvent")
                    break
        except:
            break
    
    print("Lost connection to: ", player_id)
    color_index = sprites.index(player_map[player_id].get_color())
    taken_sprites.remove(color_index)

    try:
        del player_map[player_id]
        print("Closing Game of: ", player_id)
    except:
        pass
    
    conn.close()

black_color = (0, 0, 0)
white_color = (255, 255, 255)
gray_color = (225, 225, 225)
red_color = (255, 0, 0)
green_color = (0, 255, 0)
blue_color = (0, 0, 255)

sprites = [red_color, green_color, blue_color]
sprites = sprites[:max_clients]
taken_sprites = []
not_taken = 0

while True:
    conn, add = server_socket.accept()

    player_id = randint(10000, 1000000)
    conn.sendall(pickle.dumps(['id_update', player_id]))
    print("Just sent a new id: ", player_id)

    for i in range(len(sprites)):
        if i not in taken_sprites:
            not_taken = i
            taken_sprites.append(i)
            break

    player_map[player_id] = PlayerInstance(sprites[not_taken])

    start_new_thread(threaded_client, (conn, player_id))