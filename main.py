from poormishaengine.poorengine import *
from poormishaengine.enginetypes import *
import pyray as rl
from poormishaengine import poorengine

class Cube:
    def __init__(self, position: Vector2):
        self.position = position
        self.velocity = Vector2(0, 0)
        self.rotation_degrees = 90.0
        self.scale_x = 20
        self.scale_y = 20
        self.visual_scale_x = self.scale_x
        self.visual_scale_y = self.scale_y
        self.bounce_factor = 0.5
        self.gravity = 0.5
        self.take_control = False
        
    def get_rect(self) -> rl.Rectangle:
        return rl.Rectangle(self.position.x, self.position.y, self.scale_x, self.scale_y)
        
    def update(self, actions_input, platforms, dragging: bool, mouse_delta: Vector2):

        self.visual_scale_x = self.scale_x
        self.visual_scale_y = lerp(self.visual_scale_y, self.scale_y, 0.4)
        
        if dragging:
            self.velocity = mouse_delta
            self.position = rl.get_mouse_position()
        else:

            self.velocity.y += self.gravity
            

            if actions_input.is_action_pressed("left"):
                self.velocity.x = -4
            elif actions_input.is_action_pressed("right"):
                self.velocity.x = 4
            elif actions_input.is_action_pressed("jump") and self.is_on_floor(platforms):
                self.velocity.y = -10
                

            self.velocity.x = lerp(self.velocity.x, 0, 0.1)
            

            if not self.is_on_floor(platforms):
                self.rotation_degrees += self.velocity.x
            else:
                self.rotation_degrees = lerp(self.rotation_degrees, snap(self.rotation_degrees, 90), 0.5)
                

            self.position.x += self.velocity.x
            self.check_collisions_x(platforms)
            

            self.position.y += self.velocity.y
            self.check_collisions_y(platforms)
    
    def check_collisions_x(self, platforms):
        player_rect = self.get_rect()
        for platform in platforms:
            if rect_vs_rect(player_rect, platform):
                if self.velocity.x > 0:
                    self.position.x = platform.x - self.scale_x
                    if abs(self.velocity.x) > 1:
                        self.velocity.x = -self.velocity.x * self.bounce_factor
                    else:
                        self.velocity.x = 0
                elif self.velocity.x < 0:
                    self.position.x = platform.x + platform.width
                    if abs(self.velocity.x) > 1:
                        self.velocity.x = -self.velocity.x * self.bounce_factor
                    else:
                        self.velocity.x = 0
                break
    
    def check_collisions_y(self, platforms):
        player_rect = self.get_rect()
        for platform in platforms:
            if rect_vs_rect(player_rect, platform):
                if self.velocity.y > 0:
                    self.position.y = platform.y - self.scale_y
                elif self.velocity.y < 0:
                    self.position.y = platform.y + platform.height

                if abs(self.velocity.y) > 1:
                    self.visual_scale_y = 10
                    self.velocity.y = -self.velocity.y * self.bounce_factor
                else:
                    self.velocity.y = 0
                break
    
    def is_on_floor(self, platforms) -> bool:
        if self.is_on_wall(platforms):
            return False
            
        player_rect = self.get_rect()
        for platform in platforms:
            if (player_rect.y + player_rect.height >= platform.y and
                player_rect.y + player_rect.height <= platform.y + 5 and
                player_rect.x + player_rect.width > platform.x and
                player_rect.x < platform.x + platform.width):
                return True
        return False
    
    def is_on_wall(self, platforms) -> bool:
        player_rect = self.get_rect()
        for platform in platforms:
            touching_left = (player_rect.x <= platform.x + platform.width and
                           player_rect.x >= platform.x + platform.width - 5)
            touching_right = (player_rect.x + player_rect.width >= platform.x and
                            player_rect.x + player_rect.width <= platform.x + 5)
            vertical_overlap = (player_rect.y + player_rect.height > platform.y and
                              player_rect.y < platform.y + platform.height)
            if vertical_overlap and (touching_left or touching_right):
                return True
        return False
    
    def draw(self, rendering_engine):
        origin = Vector2(self.visual_scale_x / 2, self.visual_scale_y / 2)
        draw_pos = Vector2(self.position.x + origin.x, self.position.y + origin.y)
        player_rect = rl.Rectangle(draw_pos.x, draw_pos.y, self.visual_scale_x, self.visual_scale_y)
        rendering_engine.draw_rect_pro(player_rect, rl.GRAY, origin, self.rotation_degrees)

def rect_vs_rect(a: rl.Rectangle, b: rl.Rectangle):
    return (a.x < b.x + b.width and
            a.x + a.width > b.x and
            a.y < b.y + b.height and
            a.y + a.height > b.y)

def lerp(a, b, t):
    return a + (b - a) * t

def snap(value, step):
    return round(value / step) * step


engine = poorengine.PoorEngine(800, 600, "PoorMishaEngine")
actions_input = poorengine.InputActions()

actions_input.bind_action("drag", [rl.KeyboardKey.KEY_SPACE])
actions_input.bind_action("left", [rl.KeyboardKey.KEY_LEFT])
actions_input.bind_action("right", [rl.KeyboardKey.KEY_RIGHT])
actions_input.bind_action("jump", [rl.KeyboardKey.KEY_UP])


platforms = [
    rl.Rectangle(0, 240, 1000, 500),
    rl.Rectangle(500, 140, 1000, 500),
    rl.Rectangle(100, 10, 300, 200),
]


cube = Cube(Vector2(100, 0))
last_mouse_pos = rl.get_mouse_position()

@engine.process("phyc")
def phyc():
    global last_mouse_pos
    

    engine.rendering_engine.draw_text(
        f"{cube.velocity.x:.2f} і {cube.velocity.y:.2f} \n rotation {cube.rotation_degrees}",
        Vector2(0, 0), 30, rl.RED)
    

    mouse_pos = rl.get_mouse_position()
    mouse_delta = Vector2(mouse_pos.x - last_mouse_pos.x, mouse_pos.y - last_mouse_pos.y)
    last_mouse_pos = mouse_pos
    
    dragging = actions_input.is_action_pressed("drag")
    cube.update(actions_input, platforms, dragging, mouse_delta)
    

    cube.draw(engine.rendering_engine)
    

    for platform in platforms:
        engine.rendering_engine.draw_rect(platform, rl.BLACK)

engine.run()