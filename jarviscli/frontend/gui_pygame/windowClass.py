
import pygame
from pygame.locals import *
import math
import sys
import io
import re
import os

from frontend.gui_pygame.inputBoxClass import inputBox
from frontend.gui_pygame import ptext


# Some constants
launch_info_window = 1
launch_empty_window = 2
nothing = 0

IMAGE_PREFIX = 'jarviscli/frontend/gui_pygame/images'


class JarvisWindow():

    screen_title = "Jarvis"
    screen_background_color = (14, 14, 24)
    quit_screen = False
    quit_info_window = False
    quit_empty_window = False
    enable_voice = False

    def __init__(self, jarvis):
        super(JarvisWindow, self).__init__()
        self.jarvis = jarvis
        short_description = "A Personal Assistant for Linux and MacOS"
        self.long_description = '''
All about Jarvis:
=================

Jarvis is a simple personal assistant for Linux and MacOS.
He can talk to you if you enable his voice.
He can tell you the weather, he can find restaurants and other places near you.
He can do some great stuff for you.
Stay updated about new functionalities.


Documented commands (type help <topic>):
========================================\n
battery\tcurrencyconv\texit\t\t\t increase\tos\t\t\tsay\t\t\t  tempconv
bye      \tcurve        \t\t factor  \t\tip       \t\tpinpoint  screen     \ttime
calc     \tcurvesketch  \tfile          \tlimit   \t\tplay     \tshow      \t todo
calculate decrease       \tgmail          lyrics         plot    \t  shutdown    translate
cancel     dictionary     \tgoodbye      match        solve       umbrella
check      directions      \thackathon   movie       quit      \tspeedtest    update
chuck      disable              health          music       quote       status          weather
clear       display          \thelp             mute     \treboot      stopwatch    wiki
clock       enable           \thibernate    near          remind     suspend
coin\t\tequations     \t hybridsleep news\t     roll       \tsysteminfo
cricket\tevaluate            imgur            open         run          tell      '''

        pygame.init()
        # get the screen's resolution
        screen_resolution = pygame.display.Info()
        self.width = math.floor(800)
        self.height = math.floor(600)

        # set the screen to the appropriate size
        self.screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the screen
        pygame.display.set_caption(self.screen_title)

        # configure the coordinates of the info's logo
        self.info_logo_coords = [self.width - 30, 5, 25, 25]
        # configure the coordinates of the speaker's logo
        self.speaker_logo_coords = [self.width - 45, self.height - 95, 30, 30]
        # load different images (opening, logo and info)
        self.delete_logo_coords = [self.width - 45, self.height - 45, 30, 30]

        def load(filename):
            return pygame.image.load(os.path.join(IMAGE_PREFIX, filename)).convert()

        self.opening_image = load('opening.png')
        self.Jarvis_logo = load('JarvisLogo.png')
        self.Jarvis_logo2 = load('JarvisLogo2.png')
        self.info_logo = load("infoIcon.png")
        self.delete_logo = load("delete.png")
        self.speaker_logo_activated = load("speakerOn.png")
        self.speaker_logo_disactivated = load("speakerOff.png")
        self.speaker_logo = self.speaker_logo_disactivated
        # configure fonts for different titles and descriptions
        self.info_description_font = pygame.font.SysFont(
            "monospace", 20, bold=False)
        self.title_opening_font = pygame.font.SysFont(
            "monospace", 30, bold=False)
        self.Jarvis_title_main_window_font = pygame.font.SysFont(
            "monospace", 50, bold=True)
        # rendering the different titles and descriptions
        self.short_info_description = self.info_description_font.render(
            short_description, True, (184, 184, 180))
        self.Jarvis_title_main_window = self.Jarvis_title_main_window_font.render(
            self.screen_title, True, (31, 184, 251))
        self.title_opening = self.title_opening_font.render(
            self.screen_title, True, (31, 184, 251))
        # Create un input box for the interaction with the user
        color_active = pygame.Color(32, 185, 255, 255)
        color_inactive = pygame.Color(0, 41, 63, 255)
        self.font_color = (31, 184, 251)
        self.user_input_box = inputBox(
            10,
            self.height - 50,
            self.width - 20,
            40,
            'Ask something...',
            20,
            color_active,
            color_inactive,
            self.font_color)
        self.answer_input_box = inputBox(
            10,
            self.height - 100,
            self.width - 20,
            40,
            'Hi what can i do for you ?',
            20,
            color_active,
            color_inactive,
            self.font_color)

        self.events_list = [
            pygame.K_CLEAR,
            pygame.K_PAUSE,
            pygame.K_F1,
            pygame.K_F2,
            pygame.K_F3,
            pygame.K_F4,
            pygame.K_F5,
            pygame.K_F6,
            pygame.K_F7,
            pygame.K_F8,
            pygame.K_F9,
            pygame.K_F10,
            pygame.K_F11,
            pygame.K_F12,
            pygame.K_NUMLOCK,
            pygame.K_CAPSLOCK,
            pygame.K_SCROLLOCK,
            pygame.K_RSHIFT,
            pygame.K_LSHIFT,
            pygame.K_RCTRL,
            pygame.K_LCTRL,
            pygame.K_RALT,
            pygame.K_LALT,
            pygame.K_RMETA,
            pygame.K_LMETA,
            pygame.K_RSUPER,
            pygame.K_MODE,
            pygame.K_HELP,
            pygame.K_INSERT,
            pygame.K_PAGEUP,
            pygame.K_PAGEDOWN,
            pygame.K_QUOTE,
            pygame.K_PRINT,
            pygame.K_SYSREQ,
            pygame.K_BREAK,
            pygame.K_MENU,
            pygame.K_POWER,
            pygame.K_EURO]

        self.actions = self.jarvis.plugins.keys()
        self.in_new_win = False
        self.max_nb_lines = self.width // 21
        self.index_answer = 0  # will help for the scrolling
        self.cur_answers = []

    # Get if the mouse is on the info button
    def click_on_info(self, mouse_x, mouse_y):
        if mouse_x >= self.info_logo_coords[0] and mouse_x <= (
                self.info_logo_coords[0] + self.info_logo_coords[2]):
            return mouse_y >= self.info_logo_coords[1] and mouse_y <= (
                self.info_logo_coords[1] + self.info_logo_coords[3])

    # Get if the mouse is on the speaker button
    def click_on_speaker(self, mouse_x, mouse_y):
        if mouse_x >= self.speaker_logo_coords[0] and mouse_x <= (
                self.speaker_logo_coords[0] + self.speaker_logo_coords[2]):
            return mouse_y >= self.speaker_logo_coords[1] and mouse_y <= (
                self.speaker_logo_coords[1] + self.speaker_logo_coords[3])

    # Get if the mouse is on the delete button
    def click_on_delete(self, mouse_x, mouse_y):
        if mouse_x >= self.delete_logo_coords[0] and mouse_x <= (
                self.delete_logo_coords[0] + self.delete_logo_coords[2]):
            return mouse_y >= self.delete_logo_coords[1] and mouse_y <= (
                self.delete_logo_coords[1] + self.delete_logo_coords[3])

    # Check for events related to the screen and input boxes
    def event_listener(self, main_screen):
        for event in pygame.event.get():
            if event.type == QUIT or (
                    event.type == KEYDOWN and event.key == K_ESCAPE):
                if main_screen:
                    self.quit_screen = True
                    self.answer_input_box.answers = ["Goodbye, see you later!"]
                else:
                    # go back to the main window
                    self.quit_info_window = True
                    self.quit_empty_window = True
                    self.in_new_win = False
                    # to reset the index of the first element from
                    # 'self.answer_input_box.answers'
                    self.index_answer = 0
                    # reset the resolution
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height))
                    # reset the title
                    pygame.display.set_caption(self.screen_title)

            # events related to the input box
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.click_on_info(mouse_x, mouse_y):
                        self.quit_info_window = False
                        return launch_info_window

                    if self.click_on_delete(mouse_x, mouse_y):
                        self.user_input_box.index_c = 0
                        self.user_input_box.user_entry = ''
                        self.user_input_box.text_input_box = self.user_input_box.text_input_box_font.render(
                            self.user_input_box.user_entry, True, self.font_color)

                    if self.click_on_speaker(mouse_x, mouse_y):
                        self.jarvis.enable_voice = not self.jarvis.enable_voice
                    if self.jarvis.enable_voice:
                        self.speaker_logo = self.speaker_logo_activated
                    else:
                        self.speaker_logo = self.speaker_logo_disactivated

                position = pygame.mouse.get_pos()
                if self.user_input_box.collide(position[0], position[1]):
                    self.user_input_box.input_box_active = True
                    self.user_input_box.color_input_box = self.user_input_box.color_active_input_box
                else:
                    self.user_input_box.color_input_box = self.user_input_box.color_inactive_input_box

            if event.type == pygame.KEYDOWN:
                if self.user_input_box.input_box_active:
                    if event.key == pygame.K_RETURN:
                        self.user_input_box.index_h = -1
                        self.user_input_box.index_c = 0
                        self.user_input_box.user_entry = self.user_input_box.user_entry.replace(
                            '|', '')
                        if len(self.user_input_box.user_entry.split()):
                            self.user_input_box.history.insert(
                                0, self.user_input_box.user_entry)
                        self.user_input_box.color_input_box = self.user_input_box.color_inactive_input_box
                        del self.answer_input_box.answers[:]
                        self.answer_input_box.input_box.y = self.answer_input_box.coords_input[1]
                        self.answer_input_box.input_box.h = self.answer_input_box.coords_input[3]
                        cmd = self.user_input_box.user_entry
                        self.user_input_box.user_entry = ''
                        self.user_input_box.text_input_box = self.user_input_box.text_input_box_font.render(
                            self.user_input_box.user_entry, True, self.answer_input_box.font_color)
                        self.user_input_box.input_box_active = False
                        if cmd:
                            ret = io.StringIO()
                            stdout_bak = sys.stdout
                            sys.stdout = ret
                            self.jarvis.onecmd(cmd)
                            sys.stdout = stdout_bak
                            # A regex for special characters
                            ansi_escape = re.compile(
                                r'\x1B\[[0-?]*[ -/]*[@-~]')
                            text = ansi_escape.sub('', ret.getvalue())
                            nb_lines = self.get_nb_lines(text)

                            if cmd == 'help':
                                self.quit_info_window = False
                                return launch_info_window

                            elif cmd == 'enable sound':
                                self.speaker_logo = self.speaker_logo_activated

                            elif cmd == 'disable sound':
                                self.speaker_logo = self.speaker_logo_disactivated
                            # check whether we need to display in a new window
                            # (when the answer takes too much space)
                            elif self.answer_input_box.open_win(self.screen, nb_lines):
                                self.quit_empty_window = False
                                self.in_new_win = True
                                self.answer_input_box.resize_box(
                                    self.screen, text[:-1], self.speaker_logo_coords[2], True)
                                ret.close()
                                return launch_empty_window

                            self.answer_input_box.resize_box(
                                self.screen, text[:-1], self.speaker_logo_coords[2], False)
                            ret.close()
                        else:
                            del self.answer_input_box.answers[:]
                            answer = "What can i do for you ?"
                            self.answer_input_box.input_box.y = self.answer_input_box.coords_input[
                                1]
                            self.answer_input_box.input_box.h = self.answer_input_box.coords_input[
                                3]
                            self.answer_input_box.resize_box(
                                self.screen, answer, self.speaker_logo_coords[2], False)

                    # If we press the key '\b' (backspace), we delete a
                    # caracter
                    elif event.key == pygame.K_BACKSPACE:
                        ind = self.user_input_box.index_c
                        self.user_input_box.index_c -= 1 if (
                            self.user_input_box.index_c - 1) >= 0 else 0
                        if ind > 0:
                            new_text = self.user_input_box.user_entry[:ind - 1] + \
                                '|' + self.user_input_box.user_entry[ind + 1:]
                            # self.user_input_box.user_entry[:-1]
                            self.user_input_box.user_entry = new_text
                        self.user_input_box.text_input_box = self.user_input_box.text_input_box_font.render(
                            self.user_input_box.user_entry, True, self.font_color)
                    # If we press on delete, we delete the
                    # character posionned after the cursor '|'
                    elif event.key == pygame.K_DELETE:
                        ind = self.user_input_box.index_c
                        new_text = self.user_input_box.user_entry[:ind +
                                                                  1] + self.user_input_box.user_entry[ind + 2:]
                        self.user_input_box.user_entry = new_text
                        self.user_input_box.text_input_box = self.user_input_box.text_input_box_font.render(
                            self.user_input_box.user_entry, True, self.font_color)
                    # When press on tab, we display the possible
                    # completions (works only on commands)
                    elif event.key == pygame.K_TAB:
                        commands = self.completion(
                            self.user_input_box.user_entry)
                        text = "   ".join(commands)
                        del self.answer_input_box.answers[:]
                        self.answer_input_box.resize_box(
                            self.screen, text, self.speaker_logo_coords[2], False)

                        if len(commands) == 1:
                            self.user_input_box.user_entry = self.user_input_box.user_entry.replace(
                                '|', '')
                            self.user_input_box.user_entry = commands[0] + '|'
                            self.user_input_box.index_c = len(commands[0])
                            self.user_input_box.text_input_box = self.user_input_box.text_input_box_font.render(
                                self.user_input_box.user_entry, True, self.font_color)
                    # We postion the cursor at the begining
                    elif event.key == pygame.K_HOME:
                        self.user_input_box.index_c = 0
                        self.user_input_box.render_cursor(self.screen)
                    # We position the cursor at the end
                    elif event.key == pygame.K_END:
                        self.user_input_box.index_c = len(
                            self.user_input_box.user_entry) - 1  # the length without the cursor
                        self.user_input_box.render_cursor(self.screen)
                    # If we are in the window without the Jarvis logo,
                    # we scroll up else we display the old
                    # commands entered from the history
                    elif event.key == pygame.K_UP:
                        if self.in_new_win:
                            self.scroll_up(True)
                        else:
                            self.user_input_box.back_to_commands(True)
                    # If we are in the window without the Jarvis logo,
                    # we scroll down else we display the recent
                    # commands entered from the history
                    elif event.key == pygame.K_DOWN:
                        if self.in_new_win:
                            self.scroll_up(False)
                        else:
                            self.user_input_box.back_to_commands(False)
                    # We move the cursor to the right
                    elif event.key == pygame.K_RIGHT:
                        self.user_input_box.move_cursor(self.screen, True)
                    # We move the cursor to the left
                    elif event.key == pygame.K_LEFT:
                        self.user_input_box.move_cursor(self.screen, False)
                    # We display the text entered by the user
                    elif self.user_input_box.check_text_within_box() and event.key not in self.events_list:
                        ind = self.user_input_box.index_c
                        self.user_input_box.index_c += 1
                        text = self.user_input_box.user_entry
                        text = self.user_input_box.insert_char(
                            text, event.unicode, ind)
                        self.user_input_box.user_entry = text
                        self.user_input_box.render_cursor(self.screen)

        return nothing

    # Method that returns the number
    # of lines of a given text

    def get_nb_lines(self, text):
        text = self.answer_input_box.ameliorate_text(
            text, self.speaker_logo_coords[2])
        return self.answer_input_box.get_nb_lines(
            text, self.speaker_logo_coords[2])

    # Method that will help to display the text scrolled
    # if we are in the new window (without the Jarvis logo)
    def text_scrolled(self):
        begin = self.index_answer
        end = self.index_answer + self.max_nb_lines
        return self.answer_input_box.answers[begin: end]

    # Method that is used to update 'self.index_answer'
    # which represents the index of the first element to
    # show from the list 'self.answer_input_box.answers'
    def scroll_up(self, up):
        if up and (self.index_answer - 1) >= 0:
            self.index_answer -= 1
        elif not up:
            limit = len(self.answer_input_box.answers) - \
                (self.max_nb_lines + self.index_answer + 1)
            if limit and len(
                    self.answer_input_box.answers) > self.max_nb_lines:
                self.index_answer += 1

    # Method inspired from
    # the file CmdInterpreter.py
    def completion(self, text):
        text = text.replace('|', '')
        return [i for i in self.actions if i.startswith(text)]

    # Main method to run the program
    def execute(self):
        t0 = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        clock_tick_rate = 20
        pygame.key.set_repeat(500, 10)
        while not self.quit_screen:
            # show an opening image for 4 seconds
            if (pygame.time.get_ticks() - t0) < 2000:  # 4000:
                self.screen.blit(self.opening_image, [0, 0])
                self.screen.blit(
                    self.title_opening,
                    (self.width / 2 - 55,
                     self.height / 2 - 35))
            else:
                action = self.event_listener(True)
                self.cur_answers = self.answer_input_box.answers
                if action == launch_info_window:
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height))
                    pygame.display.set_caption("Info")
                    while not self.quit_info_window:
                        # display the description
                        self.screen.fill(self.screen_background_color)
                        ptext.draw(
                            self.long_description,
                            (20,
                             20),
                            fontsize=30,
                            color="gray",
                            align="left",
                            bold=False)
                        pygame.display.update()
                        clock.tick(clock_tick_rate)
                        # listen events related to the info window
                        self.event_listener(False)
                elif action == launch_empty_window:
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height))
                    pygame.display.set_caption(self.screen_title)
                    while not self.quit_empty_window:
                        self.user_input_box.input_box_active = True
                        self.event_listener(False)
                        # to get only the text that can be displayed in the
                        # screen
                        self.cur_answers = self.text_scrolled()
                        self.screen.fill(self.screen_background_color)
                        self.answer_input_box.draw(
                            self.screen, self.cur_answers, True, False)
                        pygame.display.update()
                        clock.tick(clock_tick_rate)

                    self.user_input_box.input_box_active = False
                    del self.answer_input_box.answers[:]
                    self.answer_input_box.input_box.y = self.answer_input_box.coords_input[1]
                    self.answer_input_box.input_box.h = self.answer_input_box.coords_input[3]
                    self.answer_input_box.resize_box(
                        self.screen, "What can I do for you", self.speaker_logo_coords[2], False)
                    self.answer_input_box.draw(
                        self.screen, self.cur_answers, True, True)

                else:  # if action == nothing
                    self.screen.fill(self.screen_background_color)
                    self.screen.blit(self.Jarvis_logo, [0, 0])
                    self.screen.blit(
                        self.Jarvis_logo2, [
                            self.width / 2, self.height / 2 - 70])
                    self.screen.blit(
                        self.Jarvis_title_main_window, [
                            self.width / 2 - 160, self.height / 10])
                    self.screen.blit(
                        self.short_info_description, [
                            self.width / 2 - 160, self.height / 10 + 50])
                    self.screen.blit(
                        self.info_logo, [
                            self.info_logo_coords[0], self.info_logo_coords[1]])
                    self.screen.blit(
                        self.delete_logo, [
                            self.delete_logo_coords[0], self.delete_logo_coords[1]])
                    self.screen.blit(
                        self.speaker_logo, [
                            self.speaker_logo_coords[0], self.speaker_logo_coords[1]])
                    self.user_input_box.draw(self.screen, [], False, True)
                    self.answer_input_box.draw(
                        self.screen, self.cur_answers, True, True)

            pygame.display.update()
            clock.tick(clock_tick_rate)
