import pygame

class PlayerInstance:
    def __init__(self, color):
        self.x = 0
        self.y = 0
        self.xy = (0, 0)
        self.message = ''
        self.color = color

    def set_position(self, tup):
        self.x = tup[0]
        self.y = tup[1]
        self.xy = (tup[0], tup[1])
    
    def get_position(self):
        return self.xy

    def set_message(self, message):
        self.message = message
    
    def get_message(self):
        return self.message
    
    def set_color(self, color):
        self.color = color
    
    def get_color(self):
        return self.color

class TextBox:
    def __init__(self, font, color, font_color):
        self.color = color
        self.font_color = font_color
        self.font = font
        self.message = ''
        self.active = False
        self.padding = 8
        self.corner_radius = 2

        # Display time
        self.display_cooldown = 3000
        self.last_time = 0

    def display_message(self, screen, values):
        if self.active and len(self.message) > 0:
            m = 24
            text_surface = self.font.render(self.message, True, self.font_color)
            text_width = text_surface.get_width() + m
            text_height = text_surface.get_height() + m

            player_w, player_h = values[2], values[3]
            box_x = (values[0] - (text_width - player_w)/2)
            box_y = (values[1] - text_height - m/2)

            text_box = pygame.Rect((box_x, box_y), (text_width, text_height))
            pygame.draw.rect(screen, self.color, text_box, 0, self.corner_radius)

            text_x = box_x + (text_box.width - text_surface.get_width())/2
            text_y = box_y + (text_box.width - text_surface.get_width())/2
            screen.blit(text_surface, (text_x, text_y))

            self.update_display_time()
        
    def update_display_time(self):
        self.running_time = pygame.time.get_ticks()
        if self.running_time - self.last_time >= self.display_cooldown:
            self.set_inactive()

    def set_active(self):
        self.last_time = pygame.time.get_ticks()
        self.active = True

    def set_inactive(self):
        self.message = ''
        self.active = False
    
    def set_message(self, message):
        if len(message) > 0:
            self.message = message
            self.set_active()

class Player:
    def __init__(self, x, y, width, height, color, font, textbox_color, font_color):
        self.x = x
        self.y = y
        self.xy = (x, y)
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x, y, width, height)
        self.vel = 2
        self.text_box = TextBox(font, textbox_color, font_color)

    def set_position(self, tup):
        self.x = tup[0]
        self.y = tup[1]
        self.xy = (tup[0], tup[1])
        self.rect = (self.x, self.y, self.width, self.height)

    def get_position(self):
        return self.xy

    def move(self, screen_w, screen_h):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if self.x > 0:
                self.x -= self.vel
        if keys[pygame.K_RIGHT]:
            if self.x < screen_w - self.width:
                self.x += self.vel
        if keys[pygame.K_UP]:
            if self.y > 0:
                self.y -= self.vel
        if keys[pygame.K_DOWN]:
            if self.y < screen_h - self.height:
                self.y += self.vel
                
        self.xy = (self.x, self.y)
        self.rect = (self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def get_values(self):
        return (self.x, self.y, self.width, self.height)

    def set_message(self, message):
        self.text_box.set_message(message)
    
    def get_message(self):
        return self.text_box.message
    
    def display_message(self, screen, values):
        self.text_box.display_message(screen, values)
    
    def set_color(self, color):
        self.color = color
    
    def get_color(self):
        return self.color

class InputField:
    def __init__(self, x, y, width, height, font, message):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (255, 255, 255)
        self.active_color = (225, 225, 225)
        self.font = font
        self.font_color = (225, 225, 225)
        self.font_active_color = (0, 0, 0)
        self.default_message = message
        self.active_message = ''
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False
        self.padding = 8

    def draw(self, screen):
        if self.active:
            rect_color = self.active_color
            font_color = self.font_active_color
        else:
            rect_color = self.color
            font_color = self.font_color

        pygame.draw.rect(screen, rect_color, self.rect)

        message = self.default_message 
        if len(self.active_message) > 0:
            message = self.active_message

        text_surface = self.font.render(message, True, font_color)
        screen.blit(text_surface, (self.x + self.padding, self.y + self.padding))
    
    def set_active(self):
        self.active = True
    
    def set_inactive(self):
        self.active = False
    
    def add_character(self, character):
        if self.active:
            self.active_message += character

    def remove_last_character(self):
        if self.active:
            self.active_message = self.active_message[:-1]
    
    def clear_input_field(self):
        self.active_message = ''


class Button:
    def __init__(self, x, y, width, height, font, message):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (255, 255, 255)
        self.active_color = (225, 225, 225)
        self.font = font
        self.font_color = (0, 0, 0)
        self.message = message
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False
        
        text_surface = self.font.render(self.message, True, self.font_color)

        self.text_x = x + (width - text_surface.get_width())/2
        self.text_y = y + (height - text_surface.get_height())/2


    def draw(self, screen):
        if self.active:
            rect_color = self.active_color
        else: rect_color = self.color
            
        pygame.draw.rect(screen, rect_color, self.rect)

        text_surface = self.font.render(self.message, True, self.font_color)
        screen.blit(text_surface, (self.text_x, self.text_y))
    
    def set_active(self):
        self.active = True
    
    def set_inactive(self):
        self.active = False
    
class Alert:
    def __init__(self, screen_w, y_level, color, font, message):
        self.color = color
        self.font = font
        self.message = message
        self.active = False

        # Text coordinates
        text_surface = font.render(message, True, color)
        self.text_x = (screen_w - text_surface.get_width())/2
        self.text_y = y_level 

        # Display time
        self.display_cooldown = 3000
        self.last_time = 0
    
    def draw(self, screen):
        if self.active and len(self.message) > 0:
            text_surface = self.font.render(self.message, True, self.color)
            screen.blit(text_surface, (self.text_x, self.text_y))
        
            self.update_display_time()
        
    def update_display_time(self):
        self.running_time = pygame.time.get_ticks()
        if self.running_time - self.last_time >= self.display_cooldown:
            self.set_inactive()

    def set_active(self):
        self.last_time = pygame.time.get_ticks()
        print('active')
        self.active = True

    def set_inactive(self):
        print('inactive')
        self.active = False
