import pygame



class inputBox(object):
    input_box = None
    text_input_box = 'Ask something'
    text_input_box_font = None
    input_box_active = False
    color_active_input_box = None
    color_inactive_input_box = None



    """docstring for inputBox"""
    def __init__(self, x, y, width, height, text, font_size):
        super(inputBox, self).__init__()
        self.input_box = pygame.Rect(x, y, width, height)
        self.input_box_active = False
        self.color_active_input_box = pygame.Color(32, 185, 255, 255)
        self.color_inactive_input_box = pygame.Color(0, 41, 63, 255)
        self.color_input_box = self.color_inactive_input_box
        self.text_input_box_font = pygame.font.Font(None, font_size)
        self.text_input_box = self.text_input_box_font.render(text, True, (184 ,184, 180))
        self.history = ''
        self.user_entry = ''

    # Listen to the events related to the input box
    def event_listener(self):
        for event in pygame.event.get():
            print("get the events")
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Debug
                print("mousePosition = ", pygame.mouse.get_pos(), "\tcollidepoint = ", self.input_box.collidepoint(pygame.mouse.get_pos()))   

                #if user click on the box
                if self.input_box.collidepoint(pygame.mouse.get_pos()): ############## <----- can't get the mouse position
                    print("input_box active\n")
                    self.input_box_active = True
                    self.color_input_box = self.color_active_input_box
                else:
                    print("input_box inactive\n")
                    self.color_input_box = self.color_inactive_input_box
            if event.type == pygame.KEYDOWN:
                print("text = ", event.unicode)

                print("kEY PRESSED\n\n\n")
                if self.input_box_active:
                    print("Hello\t the box is active")
                    # If we press 'enter', we save 
                    if event.key == pygame.K_RETURN:
                        self.history += "\n" + str(user_entry)
                        print(self.history)        
                        self.user_entry = ''
                        self.text_input_box = self.text_input_box_font.render(self.user_entry, True, (31 ,184, 251))
                        self.input_box_active = False
                    # If we press the key '\b' (backspace), we delete a caracter
                    elif event.key == pygame.K_BACKSPACE:
                        self.user_entry = self.user_entry[:-1]
                        self.text_input_box = self.text_input_box_font.render(self.user_entry, True, (31 ,184, 251))    
                    else:
                        print("user_entry = ", self.user_entry)
                        self.user_entry += event.unicode
                        self.text_input_box = self.text_input_box_font.render(self.user_entry, True, (31 ,184, 251))

    def collide(self, x, y):
        print("I'm in the collide function\n")
        return self.input_box.collidepoint(x, y)

    # draw the input box
    def draw(self, screen):
        #self.event_listener()
        """
        for event in pygame.event.get():
            print("get the events")
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("MOUSEBUTTONDOWN")
                #Debug
                print("mousePosition = ", event.pos, "\tcollidepoint = ", self.input_box.collidepoint(event.pos))   
        """
        screen.blit(self.text_input_box, (self.input_box.x + 10, self.input_box.y + 10))
        pygame.draw.rect(screen, self.color_input_box, self.input_box, 2)
