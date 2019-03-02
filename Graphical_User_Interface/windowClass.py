
import pygame
from pygame.locals import *
import math
import ptext

from inputBoxClass import inputBox

#Some constants
launch_info_window = 1
nothing = 0

class JarvisWindow():
    """docstring for """
    width = -1
    height = -1
    screen = -1
    screen_title = "Jarvis"
    screen_background_color = (14, 14, 24)
    quit_screen = False
    quit_info_window = False
    title_opening = None
    title_opening_font = None
    opening_image = None
    short_info_description = None
    long_info_description = None
    info_description_font = None
    info_logo = None
    info_logo_coords = None
    Jarvis_logo = None
    Jarvis_title_main_window = None
    Jarvis_title_main_window_font = None


    def __init__(self):
        super(JarvisWindow, self).__init__()
        short_description = "A Personal Assistant for Linux and MacOS" 
        self.long_description = '''Jarvis is a simple personal assistant for Linux and MacOS
 which works on the terminal. He can talk to you if you enable his voice.
 He can tell you the weather, he can find restaurants and other places near you.
 He can do some great stuff for you.
 Stay updated about new functionalities.'''
        pygame.init()
        #get the screen's resolution
        screen_resolution = pygame.display.Info()
        self.width = math.floor(screen_resolution.current_w * 4 / 7)
        self.height = math.floor(screen_resolution.current_h * 3 / 4)

        #set the screen to the appropriate size
        self.screen = pygame.display.set_mode((self.width, self.height))
        #set the title of the screen
        pygame.display.set_caption(self.screen_title)

        #configure the coordinates of the info's logo
        self.info_logo_coords = [self.width - 30, 5, 25, 25]
        #load different images (opening, logo and info)
        self.opening_image = pygame.image.load("images/opening.png").convert()
        self.Jarvis_logo = pygame.image.load("images/JarvisLogo.png").convert()
        self.info_logo = pygame.image.load("images/infoIcon.png").convert()
        #configure fonts for different titles and descriptions
        self.info_description_font = pygame.font.SysFont("monospace", 20, bold = False)
        self.title_opening_font = pygame.font.SysFont("monospace", 30, bold = False)
        self.Jarvis_title_main_window_font = pygame.font.SysFont("monospace", 50, bold = True)
        #rendering the different titles and descriptions
        self.short_info_description= self.info_description_font.render(short_description, True, (184 ,184, 180))
        self.Jarvis_title_main_window = self.Jarvis_title_main_window_font.render("Jarvis", True, (31 ,184, 251))
        self.title_opening = self.title_opening_font.render("Jarvis", True, (31 ,184, 251))
        #Create un input box for the interaction with user
        self.user_input_box = inputBox(10, self.height - 50, self.width - 20, 40, 'Ask something...', 20)
        self.answer_input_box = inputBox(10, self.height - 100, self.width - 20, 40, 'Hi what can i do for you ?', 20) 


    # Get if the mouse is on the info button
    def click_on_info(self, mouse_x, mouse_y):
        if mouse_x >= self.info_logo_coords[0] and mouse_x <= (self.info_logo_coords[0] + self.info_logo_coords[2]):
            return mouse_y >= self.info_logo_coords[1] and mouse_y <= (self.info_logo_coords[1] + self.info_logo_coords[3])
    #        
    def event_listener(self, main_screen):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                if main_screen:
                    self.quit_screen = True      
                else:
                    #go back to the main window 
                    self.quit_info_window = True
                    #reset the resolution
                    self.screen = pygame.display.set_mode((self.width, self.height))
                    #reset the title 
                    pygame.display.set_caption("Jarvis")

            # events related to the input box
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.click_on_info(mouse_x, mouse_y):
                        self.quit_info_window = False
                        return launch_info_window

                position = pygame.mouse.get_pos()
                print("position = ", position[0], position[1])             
                if self.user_input_box.collide(position[0], position[1]): ############## <----- can't get the mouse position
                    print("input_box active\n")
                    self.user_input_box.input_box_active = True
                    self.user_input_box.color_input_box = self.user_input_box.color_active_input_box
                else:
                    print("input_box inactive\n")
                    self.user_input_box.color_input_box = self.user_input_box.color_inactive_input_box
            
            if event.type == pygame.KEYDOWN:
                print("text = ", event.unicode)

                print("kEY PRESSED\n\n\n")
                if self.user_input_box.input_box_active:
                    print("Hello\t the box is active")
                    # If we press 'enter', we save 
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_RETURN]: #event.key == pygame.K_RETURN:
                        self.user_input_box.history += "\n" + str(self.user_input_box.user_entry)
                        print(self.user_input_box.history)        
                        self.user_input_box.user_entry = ''
                        self.user_input_box.text_input_box = self.user_input_box.text_input_box_font.render(self.user_input_box.user_entry, True, (31 ,184, 251))
                        self.user_input_box.input_box_active = False
                    # If we press the key '\b' (backspace), we delete a caracter
                    elif event.key == pygame.K_BACKSPACE:
                        self.user_input_box.user_entry = self.user_input_box.user_entry[:-1]
                        self.user_input_box.text_input_box = self.user_input_box.text_input_box_font.render(self.user_input_box.user_entry, True, (31 ,184, 251))    
                    else:
                        print("user_entry = ", self.user_input_box.user_entry)
                        self.user_input_box.user_entry += event.unicode
                        self.user_input_box.text_input_box = self.user_input_box.text_input_box_font.render(self.user_input_box.user_entry, True, (31 ,184, 251))
    
                        
        return nothing               



    def execute(self):
        print("Starting\n")
        t0 = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        clock_tick_rate = 20
        while not self.quit_screen:
            #show an opening image for 4 seconds   
            if (pygame.time.get_ticks() - t0) < 2000: #4000: 
                self.screen.blit(self.opening_image, [0, 0])
                self.screen.blit(self.title_opening, (self.width / 2 - 55, self.height / 2 - 35))
            else:
                action = self.event_listener(True)
                if action == launch_info_window:
                    self.screen = pygame.display.set_mode((self.width, math.floor(self.height / 3)))
                    pygame.display.set_caption("Info")
                    while not self.quit_info_window:
                        #display the description
                        self.screen.fill(self.screen_background_color)                             
                        ptext.draw(self.long_description, (20, 20), fontsize=30, color="gray",align="left",bold = False)
                        pygame.display.update()
                        clock.tick(clock_tick_rate)
                        #listen events related to the info window
                        self.event_listener(False)
                else: #if action == nothing
                    self.screen.fill(self.screen_background_color) 
                    self.screen.blit(self.Jarvis_logo, [0, 0])
                    self.screen.blit(self.Jarvis_title_main_window, [self.width / 2 - 105, self.height / 10])
                    self.screen.blit(self.short_info_description, [self.width / 2 - 105 , self.height / 10 + 50])
                    self.screen.blit(self.info_logo, [self.info_logo_coords[0], self.info_logo_coords[1]])
                    self.user_input_box.draw(self.screen)
                    self.answer_input_box.draw(self.screen)

            pygame.display.update()
            clock.tick(clock_tick_rate)
                    
