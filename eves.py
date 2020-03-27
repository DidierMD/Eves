import sys
import random
import sdl2
import sdl2.ext
import time
import copy

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

    def __truediv__(s, der):
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

    def truncate(s, der):
        if s.X*s.X > der.X*der.X:
            if s.X < 0:
                s.X = -der.X
            else:
                s.X = der.X
        if s.Y*s.Y > der.Y*der.Y:
            if s.Y < 0:
                s.Y = -der.Y
            else:
                s.Y = der.Y

    def clockwise_perpendicular(s):
        return Vec2(s.Y, -s.X)

def mean(vec_lst):
    sum_vec = Vec2(0,0)
    for v in vec_lst:
        sum_vec += v
    return sum_vec / len(vec_lst)

def normSquare(vec):
    return vec.X * vec.X + vec.Y * vec.Y

def dot(izq, der):
    return izq.X*der.X + izq.Y*der.Y

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
# 1315001703 Promesa de bonificación 
class EvesEngine:
    Eves = None
    InteractionRadius = None

    def __init__(s, num_of_eves, ini_pos_range, ini_vel_range, inter_radius):
        s.Eves = [Eve( pos = Vec2(random.uniform(*ini_pos_range[0]), random.uniform(*ini_pos_range[1])), 
                     vel = Vec2(random.uniform(*ini_vel_range[0]), random.uniform(*ini_vel_range[1]))
                     ) for i in range(num_of_eves)]
        s.InteractionRadius = inter_radius

    def paint(s, canvas):
        for eve in s.Eves:
            eve.selfPaint(canvas)

    def moveEves(s, dt, physic_scene):
        for eve in s.Eves:
            eve.move(dt)
            physic_scene.solve_collision(eve)

    def _searchInteractions(s, eve, physic_scene):
        res = list()
        for e in s.Eves:
            distance2 = normSquare(e.Pos - eve.Pos)
            if distance2 < s.InteractionRadius * s.InteractionRadius and e != eve:
                res.append((e, distance2))
            else: # Check with physic_scene
                
        return [i[0] for i in sorted(res, key = lambda x: x[1])]
            
    def processEvesInteraction(s, dt, funs):
        new_eves = list()
        for eve in s.Eves:
            inters = s._searchInteractions(eve) # Requires the original eve
            accel = Vec2(0,0)
            for fun, kwargs in funs:
                accel += fun(eve, inters, **kwargs)
            if len(funs) > 0:
                accel = accel / len(funs)
            new_eve = copy.deepcopy(eve)
            new_eve.accelerate(dt, accel)
            new_eves.append(new_eve)
        s.Eves = new_eves
        return

    def getTotalKineticEnergy(s):
        tot_v2 = 0
        for eve in s.Eves:
            tot_v2 += normSquare(eve.Vel)
        return tot_v2 / 2

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

##### Interaction Functions

def separation_simple(eve, inters, maxacc):
    acc = Vec2(0,0)
    # Calculate 
    for e in inters:
        aux = eve.Pos - e.Pos
        aux.truncate(maxacc)
        acc += aux
    return acc

def separation_magnetic(eve, inters, mag_constant):
    acc = Vec2(0,0)
    for e in inters:
        # Get 'radius'
        r = eve.Pos - e.Pos
        r_mag2 = normSquare(r)
        new_cte = mag_constant / r_mag2
        acc += r / new_cte
    return acc

def separation_magnetic_steer(eve, inters, mag_constant):
    acc = Vec2(0,0)
    for e in inters:
        # Get 'radius'
        r = eve.Pos - e.Pos
        r_mag2 = normSquare(r)
        new_cte = mag_constant / r_mag2
        acc += r / new_cte
    v_perp = eve.Vel.clockwise_perpendicular()
    acc_influence = dot(v_perp, acc)
    return v_perp * acc_influence

##### Other functions

########### MAIN

def main(win_x, win_y, eves_num):
    # Init setup
    win = DrawEngine("Eves", (win_x, win_y))
    MyEves = EvesEngine(eves_num, ((0, win_x - 1), (0, win_y -1)), ((-50, 50), (-50, 50)), 40)
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
        if int(new_time) % 5 == 0:
            print(MyEves.getTotalKineticEnergy())
        MyEves.moveEves(new_time - current_time, physic_scene)
        #MyEves.processEvesInteraction(new_time - current_time, [(separation_simple, {'maxacc':Vec2(100,100)})])
        #MyEves.processEvesInteraction(new_time - current_time, [(separation_magnetic, {'mag_constant':10000})]) 
        MyEves.processEvesInteraction(new_time-current_time, [(separation_magnetic_steer,{'mag_constant':1000000})]) 
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
