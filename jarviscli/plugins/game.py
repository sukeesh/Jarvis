import random
import curses

s = curses.initscr()
curses.curs_set(0)
sh, sw = s.getmaxyx()
w = curses.newwwin(sh, sw, 0, 0)
w.keypad(1)
w.timeout(100)

snk_x = sw/ #length of screen
snk_y = sh/2 #width of screen
snake = [
[snk_y, snk_x],
[snk_y, snk_x-1],
[snk_y, snk_x-2],
]

food = [sh/2, sw/2] #center of the screen
w.addch(food[0], food[1], curses.ACS_PI)

key = curses.KEY_RIGHT

while True: #creates while loop for every movement of the snake
  next_key = w.getch()
  key = key if next_key == -1 else next_key
  
if snake[0][0] in [0, sh] or snake[0][1] in [0, sw] or snake[0] in [1:]:
curses.endwin()
quit()

new_head = [snake[0][0], snake[0][1]]

if key == curses.KEY_DOWN:
new_head[0] += 1
if key == curses.KEY_UP:
new_head[0] -= 1
if key == curses.KEY_LEFT:
new_head[1] -= 1
if key == curses.KEY_RIGHT:
new_head[1] += 1

snake.insert(0, new_head)

if snake[0] == food: #if snake eats food
  food = None
  while food is None:
  nf = [
    random.randint(1, sh-1),
    random.randinit(1, sw-1)
    ]
    food = nf if nf not in snake else None
    w.addch(food[0], food[1], curses.ACS_PI)
 else: 
    tail = snake.pop()
    w.addch(tail)[0], tail[1], ' ')
    
w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
