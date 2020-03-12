import sys
import random
import sdl2
import sdl2.ext
import time

########## CLASSES

###

class Vec2:
    X = None
    Y = None

    def __init__(s, x, y):
        s.X = x
        s.Y = y

    def __mul__(s, der):
        """ der: scalar """
        return Vec2(s.X * der, s.Y * der)

    def __div__(s, der):
        """ der: scalar """
        return Vec2(s.X / der, s.Y / der)

    def __add__(s, der):
        return Vec2(s.X + der.X, s.Y + der.Y)

    def __sub__(s, der):
        return Vec2(s.X - der.X, s.Y - der.Y)

    def __iadd__(s, der):
        s.X += der.X
        s.Y += der.Y
        return s

def mean(vec_lst):
    sum_vec = Vec2(0,0)
    for v in vec_lst:
        sum_vec += v
    return sum_vec / len(vec_lst)

###

class Eve:
    Pos = None
    Vel = None

    def __init__(s, pos, vel):
        s.Pos = pos
        s.Vel = vel

    def move(s, dt):
        s.Pos += s.Vel * dt
        
    def accelerate(s, dt, acceleration):
        s.Vel += acceleration * dt

    def selfPaint(s, canvas):
        sdl2.ext.line(canvas, sdl2.ext.Color(0,0,255), (s.Pos.X, s.Pos.Y, s.Pos.X + s.Vel.X, s.Pos.Y + s.Vel.Y))

###

class PhysicScene:
    Height = None
    Width = None

    def __init__(s, width, height):
        s.Height = height
        s.Width = width

    def solve_collision(s, eve):
        if eve.Pos.X >= s.Width:
            eve.Pos.X -= s.Width
        if eve.Pos.Y >= s.Height:
            eve.Pos.Y -= s.Height
        if eve.Pos.X < 0:
            eve.Pos.X += s.Width
        if eve.Pos.Y < 0:
            eve.Pos.Y += s.Height

###

class EvesEngine:
    Eves = None

    def __init__(s, num_of_eves, ini_pos_range, ini_vel_range):
        s.Eves = [Eve( pos = Vec2(random.uniform(*ini_pos_range[0]), random.uniform(*ini_pos_range[1])), 
                     vel = Vec2(random.uniform(*ini_vel_range[0]), random.uniform(*ini_vel_range[1]))
                     ) for i in range(num_of_eves)]

    def paint(s, canvas):
        for eve in s.Eves:
            eve.selfPaint(canvas)

    def moveEves(s, dt, physic_scene):
        for eve in s.Eves:
            eve.move(dt)
            physic_scene.solve_collision(eve)
            
    def processEvesInteraction(s, dt):
        # TODO something
        return

###

class DrawEngine:
    Window = None 
    Canvas = None

    def __init__(s, title, win_size):
        """ title: string
            size: tuple Ex. (800,600)
        """
        sdl2.ext.init()
        s.Window = sdl2.ext.Window(title, size=win_size)
        s.Window.show()
        s.Canvas = s.Window.get_surface()

    def clear(s, color):
        sdl2.ext.fill(s.Canvas, color)

    def draw(s, obj_to_paint, *args, **kwargs):
        obj_to_paint.paint(s.Canvas, *args, **kwargs)

    def refresh(s):
        s.Window.refresh()

########### MAIN

def main(win_x, win_y, eves_num):
    # Init setup
    win = DrawEngine("Eves", (win_x, win_y))
    MyEves = EvesEngine(eves_num, ((0, win_x - 1), (0, win_y -1)), ((-100, 100), (-100, 100)))
    physic_scene = PhysicScene(win_x - 1, win_y - 1)
    current_time = time.time()
    # Paint first screen
    win.clear(sdl2.ext.Color(0,0,0))
    win.draw(MyEves)
    current_time = time.time() # Update time
    # Loop
    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        # Update state
        new_time = time.time()
        MyEves.moveEves(new_time - current_time, physic_scene)
        MyEves.processEvesInteraction(new_time - current_time) # Acceleration is done here
        current_time = new_time
        # Paint
        win.clear(sdl2.ext.Color(0,0,0))
        win.draw(MyEves)
        win.refresh()
    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    # Process command line arguments
    if len(sys.argv) < 4:
        print("Usage:\n python eves.py win_x win_y eves_qty")
        quit()
    win_x = int(sys.argv[1])
    win_y = int(sys.argv[2])
    eves_num = int(sys.argv[3])
    sys.exit(main(win_x, win_y, eves_num))
