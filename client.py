import socket
import pickle, select
import pygame, sys
from pygame.locals import *
from data_structures import *
from random import randint

BUFFERSIZE = 2048

black_color = (0, 0, 0)
white_color = (255, 255, 255)
gray_color = (225, 225, 225)
red_color = (255, 0, 0)
green_color = (0, 255, 0)
blue_color = (0, 0, 255)
yellow_color = (235, 200, 40)

screen_w, screen_h = 400, 400
player_w, player_h = 30, 30
init_x, init_y = 50, 50

isConnected = False

player_map = {}
my_id = 0
server_socket = None
server_host = None
input_field = None

pygame.init()
pygame.display.set_caption("Multiplayer")
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_w, screen_h))
font = pygame.font.SysFont(None, 22)
bigger_font = pygame.font.SysFont(None, 34)
smaller_font = pygame.font.SysFont(None, 16)

def draw_game(screen, bg_color):
    screen.fill(bg_color)

    # draw order player message > other messages > myself > other players
    # draw other players body first
    for key in player_map:
        if key != my_id: 
            player_map[key].draw(screen)

    # then draw myself
    player_map[my_id].draw(screen)

    # then draw other players messages
    for key in player_map:
        if key != my_id: 
            player_map[key].display_message(screen, player_map[key].get_values())

    # draw my message
    player_map[my_id].display_message(screen, player_map[my_id].get_values())
    

    # draw message input box
    input_field.draw(screen)

    pygame.display.flip()

def connect(ip, port):

    global my_id, server_socket, server_host, isConnected

    server_socket = socket.socket()
    server_host = socket.gethostname()

    server_port = int(port)
    server_socket.connect((ip, server_port))

    print("This is your host: ", server_host)
    gameEvent = pickle.loads(server_socket.recv(BUFFERSIZE))

    if gameEvent[0] == 'id_update':
        my_id = gameEvent[1]

    print("My new id: ", my_id)

    isConnected = True 

def title():
    
    input_x1, input_y1 = 20, 240
    input_x2, input_y2 = 20, 300
    input_w, input_h = 220, 30

    btn_x1, btn_y1 = 270, 240
    btn_w, btn_h = 110, 90
    padding = 8

    ip_input = InputField(input_x1, input_y1, input_w, input_h, font, 'Game IP...')
    port_input = InputField(input_x2, input_y2, input_w, input_h, font, 'Game Port...')
    connect_btn = Button(btn_x1, btn_y1, btn_w, btn_h, font, 'Join Game')

    fail_alert = Alert(screen_w, 345, red_color, bigger_font, 'Server not found. Try again.')
    author_name = smaller_font.render('Angelo Leite © 2021', True, (55, 55, 55))

    title_img = pygame.image.load("title.png")
    imagerect = title_img.get_rect()
    image_x = (screen_w - imagerect.width)/2

    while not isConnected:

        for event in pygame.event.get():       
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # Select message input box 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ip_input.rect.collidepoint(event.pos):
                    ip_input.set_active()
                    port_input.set_inactive()
                
                elif port_input.rect.collidepoint(event.pos):
                    port_input.set_active()
                    ip_input.set_inactive()
                
                elif connect_btn.rect.collidepoint(event.pos):
                    
                    try:
                        connect(ip_input.active_message, port_input.active_message)
                    except: fail_alert.set_active()
                    
                    ip_input.set_inactive()
                    port_input.set_inactive()

                else: 

                    ip_input.clear_input_field()
                    port_input.clear_input_field()

                    ip_input.set_inactive()
                    port_input.set_inactive()

            # Handling text in the input field
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:

                    if ip_input.active:
                        ip_input.remove_last_character()
                    if port_input.active:
                        port_input.remove_last_character()

                elif event.key == pygame.K_TAB:

                    if ip_input.active:
                        ip_input.set_inactive()
                        port_input.set_active()
                    elif port_input.active:
                        ip_input.set_active()
                        port_input.set_inactive()
                
                elif event.key == pygame.K_RETURN:

                        try:
                            connect(ip_input.active_message, port_input.active_message)
                        except: fail_alert.set_active()
 
                        ip_input.set_inactive()
                        port_input.set_inactive()

                else:

                    if ip_input.active:
                        ip_input.add_character(event.unicode)
                    if port_input.active:
                        port_input.add_character(event.unicode)
            
            if connect_btn.rect.collidepoint(pygame.mouse.get_pos()):
                connect_btn.set_active()
            else: connect_btn.set_inactive()
   
        screen.fill(yellow_color)

        ip_input.draw(screen)
        port_input.draw(screen)
        connect_btn.draw(screen)
        fail_alert.draw(screen)

        # Title image
        screen.blit(title_img, (image_x, 18))

        # Copyright
        screen.blit(author_name, (screen_w - author_name.get_width() - padding, screen_h - author_name.get_height() - padding))

        pygame.display.flip()

        clock.tick(120)

def update():

    global player_map

    player_map[my_id].move(screen_w, screen_h)
    update = ['update_player', player_map[my_id].xy, player_map[my_id].get_message()]
    server_socket.sendall(pickle.dumps(update))

    ins, _, _ = select.select([server_socket], [], [], 0)
    for inm in ins:
        gameEvent = pickle.loads(inm.recv(BUFFERSIZE))

        if gameEvent[0] == 'update_players':
            players = gameEvent[1]
            
            # update and add new players
            for key in players:
                if key != my_id:
                    if key in player_map:
                        current = player_map[key]
                        instance = players[key]

                        # position
                        current.set_position(instance.get_position())

                        # message
                        if len(current.get_message()) == 0:
                            current.set_message(instance.get_message())

                    else: 
                        player_map[key] = Player(init_x, init_y, player_w, player_h, players[key].get_color(), font, gray_color, black_color)
                else:
                    player_map[my_id].set_color(players[key].get_color())

            # remove leaving players
            for my_key in list(player_map):
                key_list = list(players)
                if my_key not in key_list:
                    try:
                        del player_map[my_key]
                        print("Player disconnected: ", my_key)
                    except:
                        pass

def game():

    global player_map, input_field

    input_field = InputField(5, screen_h - 35, screen_w - 10, 30, font, 'Please enter a message...')
    player_map[my_id] = Player(init_x, init_y, player_w, player_h, black_color, font, gray_color, black_color)

    while True:
        for event in pygame.event.get():       
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Select message input box 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_field.rect.collidepoint(event.pos):
                    input_field.set_active()
                else: input_field.set_inactive()

            # Handling text in the input field
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_field.remove_last_character()

                elif event.key == pygame.K_RETURN:
                    if not input_field.active:
                        input_field.set_active()
                    else:
                        player_map[my_id].set_message(input_field.active_message)
                        input_field.clear_input_field()
                        input_field.set_inactive()
                else: 
                    input_field.add_character(event.unicode)
                            
        update()
        draw_game(screen, white_color)

        clock.tick(120)

title()
game()
