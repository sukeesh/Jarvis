import pygame


class inputBox(object):
    text_input_box = 'Ask something'
    input_box_active = False

    """docstring for inputBox"""

    def __init__(
            self,
            x,
            y,
            width,
            height,
            text,
            font_size,
            color_active,
            color_inactive,
            font_color):
        super(inputBox, self).__init__()
        self.font_color = font_color
        self.input_box = pygame.Rect(x, y, width, height)
        self.input_box_active = False
        self.color_active_input_box = color_active
        self.color_inactive_input_box = color_inactive
        self.color_input_box = self.color_inactive_input_box
        self.text_input_box_font = pygame.font.Font(None, font_size)
        self.text_input_box = self.text_input_box_font.render(
            text, True, font_color)
        self.history = []
        self.user_entry = ''
        self.index_h = -1   # the index concerning the history
        self.index_c = 0   # the index of the cursor
        self.coords_input = [x, y, width, height]
        self.answers = [text]

    # check if there's collision
    def collide(self, x, y):
        return self.input_box.collidepoint(x, y)

    # check if the text entered by the user is within the input box
    def check_text_within_box(self):
        return (
            self.text_input_box.get_width() +
            60) < (
            self.input_box.w +
            self.input_box.x)

    # Get the old commands typed before
    def back_to_commands(self, up):
        if up and (self.index_h + 1) < len(self.history):
            self.index_h += 1
        elif not up and (self.index_h - 1) >= 0:
            self.index_h -= 1

        if self.index_h >= 0:
            self.user_entry = self.history[self.index_h]
            self.text_input_box = self.text_input_box_font.render(
                self.user_entry, True, self.font_color)

    # Method to insert a character 'char'
    # at a certain 'position' in a 'text'

    def insert_char(self, text, char, position):
        return text[:position] + char + text[position:]

    # This method will allow the user to move a cursor
    # (represented by ' | ') by left or right
    # in order to write where he wants

    def move_cursor(self, screen, right):
        length = len(self.user_entry)
        # When moving to the right
        if right and (
            self.index_c +
            1 <= length) and w < (
            self.input_box.w +
                self.input_box.x):
            self.index_c += 1
        # When moving to the left
        elif not right and (self.index_c - 1) >= 0:
            self.index_c -= 1

        self.user_entry = self.user_entry.replace('|', '')
        self.user_entry = self.insert_char(self.user_entry, '|', self.index_c)
        self.text_input_box = self.text_input_box_font.render(
            self.user_entry, True, self.font_color)
        screen.blit(
            self.text_input_box,
            (self.input_box.x + 10,
             self.input_box.y + 10))

    # Method that makes the cursor visible (renders it)
    def render_cursor(self, screen):
        self.user_entry = self.user_entry.replace('|', '')
        self.user_entry = self.insert_char(self.user_entry, '|', self.index_c)
        self.text_input_box = self.text_input_box_font.render(
            self.user_entry, True, self.font_color)
        screen.blit(
            self.text_input_box,
            (self.input_box.x + 10,
             self.input_box.y + 10))

    # Method that ameliorates the text
    # so the special characters '\n' and '\t'
    # won't be visible (ex: '\n' will be replaced with
    # an equivalent of spaces ' ')

    def ameliorate_text(self, text, icon_width):
        max_length = self.coords_input[2] // 7 - icon_width // 8
        new_text = ''
        old_l = ''
        for l in text:
            if l == '\n' and old_l == '\n':
                continue
            if l == '\n':
                n = max_length - (len(new_text) % max_length)
                new_text += n * ' '
            elif l == '\t':
                new_text += 4 * ' '
            else:
                new_text += l
            old_l = l
        return new_text

    # Method that returns the number of lines of a given 'text'
    def get_nb_lines(self, text, icon_width):
        max_length = self.coords_input[2] // 7 - icon_width // 8
        return len(text) // max_length + (1 if len(text) %
                                          max_length > 0 else 0) - 1

    # Method to check if a new window is needed or not
    def open_win(self, screen, nb_lines):
        return self.input_box.y - (nb_lines + 1) * 15 < screen.get_width() / 3

    # Method that resizes the input box
    # according to the length of its content 'text'
    # (In our case, it is used for the answer box)
    def resize_box(self, screen, text, icon_width, empty_win):

        text = self.ameliorate_text(text, icon_width)
        max_length = self.coords_input[2] // 7 - icon_width // 8
        nb_lines = self.get_nb_lines(text, icon_width)
        index = 0
        if empty_win:
            self.input_box.y = screen.get_height() - 10
        if nb_lines + 1 > 1:
            old_y = self.input_box.y  # save the value of 'y' to restore it after if needed
            old_yh = self.input_box.y + self.input_box.h
            self.input_box.y = self.input_box.y - \
                (nb_lines + 1) * 15  # self.coords_input[3] / 4
            self.input_box.h *= (nb_lines + 1) / 2
            self.input_box.h += self.input_box.h / 2

            if self.input_box.y < screen.get_width() / 3:
                if empty_win and self.input_box.y < old_y:
                    self.input_box.y = old_y
                else:  # --> new window
                    self.input_box.y = screen.get_width() / 3

            new_yh = self.input_box.y + self.input_box.h

            # Check if with the new height we do not
            # exceed the old position of the input box
            # (if the new 'y + h' >/< the old 'y + h')
            if new_yh > old_yh or new_yh < old_yh:
                self.input_box.h += old_yh - new_yh

        y = self.input_box.y
        for i in range(nb_lines + 1):
            answer = text[index: index + max_length]
            index += max_length
            self.answers.append(answer)

    # Method to render the input box in the 'screen'
    def draw(self, screen, answers, resize, rect):
        # If there is a rectangle around the text
        if rect:
            pygame.draw.rect(screen, self.color_input_box, self.input_box, 2)
        # If the box needs to be resized (The Bot's box)
        if resize:
            if not rect:  # displays in a new window
                y = 10
            else:
                y = self.input_box.y + 10
            for answer in answers:
                self.text_input_box = self.text_input_box_font.render(
                    answer, True, self.font_color)
                screen.blit(self.text_input_box, (self.input_box.x + 10, y))
                y += 15  # represents the space let between each two lines

        else:  # User
            screen.blit(
                self.text_input_box,
                (self.input_box.x + 10,
                 self.input_box.y + 10))
