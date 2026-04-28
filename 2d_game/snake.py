import pyglet
from pyglet import window, shapes
import sys
import os
import random

# DIPPID import path
sys.path.append(os.path.dirname(__file__))
from DIPPID import SensorUDP

# Constants
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 30

class SnakeGame:
    def __init__(self):
        self.window = window.Window(WIDTH, HEIGHT, "Snake Game")

        start_x = (self.window.width // 2) // CELL_SIZE * CELL_SIZE
        start_y = (self.window.height // 2) // CELL_SIZE * CELL_SIZE
        self.snake = [
            (start_x, start_y),
            (start_x - CELL_SIZE, start_y),
            (start_x - 2 * CELL_SIZE, start_y),
        ]
        self.direction = (CELL_SIZE, 0)
        self.grow = False

        self.food = self.spawn_food()
        self.score = 0
        self.score_label = pyglet.text.Label(
            f"Score: {self.score}", x=10, y=self.window.height - 30, color=(255, 255, 255, 255), font_size=24
        )

        self.tilt_x = 0
        self.tilt_y = 0
        self.tilt_z = 0
        self.dippid_enabled = False
        try:
            self.sensor = SensorUDP(5700)
            self.sensor.register_callback("accelerometer", self.on_tilt)
            self.sensor.register_callback("button_1", self.on_button)
            self.dippid_enabled = True
            print("DIPPID enabled: using accelerometer to change direction")
            print("Run DIPPID sender on localhost:5700 and then move the device.")
        except Exception as exc:
            self.dippid_enabled = False
            print("DIPPID not available, using keyboard only")
            print(f"DIPPID init error: {exc}")

        self.game_over = False
        self.window.event(self.on_draw)
        self.window.event(self.on_key_press)

    def spawn_food(self):
        while True:
            x = random.randint(0, (self.window.width - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            y = random.randint(0, (self.window.height - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            if (x, y) not in self.snake:
                return (x, y)

    def on_tilt(self, accelerometer_data):
        if not isinstance(accelerometer_data, dict):
            return

        self.tilt_x = accelerometer_data.get('x', 0)
        self.tilt_y = accelerometer_data.get('y', 0)
        self.tilt_z = accelerometer_data.get('z', 0)
        print(f"DIPPID tilt: x={self.tilt_x:.3f}, y={self.tilt_y:.3f}, z={self.tilt_z:.3f}")

    def on_button(self, button_state):
        if button_state == 1 and self.game_over:
            self.reset()

    def update(self, dt):
        if self.game_over:
            return

        if self.dippid_enabled:
            threshold = 0.5
            if abs(self.tilt_x) > abs(self.tilt_y):
                if self.tilt_x > threshold and self.direction != (CELL_SIZE, 0):
                    self.direction = (-CELL_SIZE, 0)  # left (x decrease)
                elif self.tilt_x < -threshold and self.direction != (-CELL_SIZE, 0):
                    self.direction = (CELL_SIZE, 0)  # right (x increase)
            else:
                if self.tilt_y > threshold and self.direction != (0, CELL_SIZE):
                    self.direction = (0, -CELL_SIZE)  # up (y decrease)
                elif self.tilt_y < -threshold and self.direction != (0, -CELL_SIZE):
                    self.direction = (0, CELL_SIZE)  # down (y increase)

        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        if new_head[0] < 0 or new_head[0] + CELL_SIZE > self.window.width or new_head[1] < 0 or new_head[1] + CELL_SIZE > self.window.height:
            self.game_over = True
            return

        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
            self.grow = True
        else:
            self.grow = False

        if not self.grow:
            self.snake.pop()

        self.score_label.text = f"Score: {self.score}"

    def on_draw(self):
        self.window.clear()
        shapes.Rectangle(0, 0, self.window.width, self.window.height, color=(20, 20, 60)).draw()
        shapes.Circle(self.food[0] + CELL_SIZE // 2, self.food[1] + CELL_SIZE // 2, CELL_SIZE // 2, color=(255, 0, 0)).draw()

        radius = CELL_SIZE // 2
        for index, (x, y) in enumerate(self.snake):
            center_x = x + radius
            center_y = y + radius
            if index == 0:
                shapes.Circle(center_x, center_y, radius, color=(0, 200, 0)).draw()

                # connect the head directly to the next body segment
                if len(self.snake) > 1:
                    next_x, next_y = self.snake[1]
                    dx = x - next_x
                    dy = y - next_y
                else:
                    dx = CELL_SIZE
                    dy = 0

                if dx > 0:
                    shapes.Rectangle(x, y, radius, CELL_SIZE, color=(0, 200, 0)).draw()
                elif dx < 0:
                    shapes.Rectangle(center_x, y, radius, CELL_SIZE, color=(0, 200, 0)).draw()
                elif dy > 0:
                    shapes.Rectangle(x, y, CELL_SIZE, radius, color=(0, 200, 0)).draw()
                else:
                    shapes.Rectangle(x, center_y, CELL_SIZE, radius, color=(0, 200, 0)).draw()

                # eyes further apart
                eye_radius = max(3, CELL_SIZE // 8)
                eye_offset = radius * 0.75
                if dx > 0:
                    shapes.Circle(center_x - eye_offset / 2, center_y + eye_offset / 3, eye_radius, color=(0, 0, 0)).draw()
                    shapes.Circle(center_x - eye_offset / 2, center_y - eye_offset / 3, eye_radius, color=(0, 0, 0)).draw()
                elif dx < 0:
                    shapes.Circle(center_x + eye_offset / 2, center_y + eye_offset / 3, eye_radius, color=(0, 0, 0)).draw()
                    shapes.Circle(center_x + eye_offset / 2, center_y - eye_offset / 3, eye_radius, color=(0, 0, 0)).draw()
                elif dy > 0:
                    shapes.Circle(center_x - eye_offset / 3, center_y - eye_offset / 2, eye_radius, color=(0, 0, 0)).draw()
                    shapes.Circle(center_x + eye_offset / 3, center_y - eye_offset / 2, eye_radius, color=(0, 0, 0)).draw()
                else:
                    shapes.Circle(center_x - eye_offset / 3, center_y + eye_offset / 2, eye_radius, color=(0, 0, 0)).draw()
                    shapes.Circle(center_x + eye_offset / 3, center_y + eye_offset / 2, eye_radius, color=(0, 0, 0)).draw()

                # tongue
                tl = CELL_SIZE // 4
                tw = CELL_SIZE // 6
                if dx > 0:
                    shapes.Triangle(center_x + radius, center_y, center_x + radius + tl, center_y + tw/2, center_x + radius + tl, center_y - tw/2, color=(255, 0, 0)).draw()
                elif dx < 0:
                    shapes.Triangle(center_x - radius, center_y, center_x - radius - tl, center_y + tw/2, center_x - radius - tl, center_y - tw/2, color=(255, 0, 0)).draw()
                elif dy > 0:
                    shapes.Triangle(center_x, center_y + radius, center_x + tw/2, center_y + radius + tl, center_x - tw/2, center_y + radius + tl, color=(255, 0, 0)).draw()
                else:
                    shapes.Triangle(center_x, center_y - radius, center_x + tw/2, center_y - radius - tl, center_x - tw/2, center_y - radius - tl, color=(255, 0, 0)).draw()
            elif index == len(self.snake) - 1:
                # Tail as triangle pointing in the direction of motion
                if len(self.snake) > 1:
                    tail_x, tail_y = self.snake[-1]
                    prev_x, prev_y = self.snake[-2]
                    dx = tail_x - prev_x
                    dy = tail_y - prev_y
                else:
                    dx = CELL_SIZE
                    dy = 0

                if dx > 0:  # tail pointing right
                    shapes.Triangle(x, y, x, y + CELL_SIZE, x + CELL_SIZE, center_y, color=(0, 255, 0)).draw()
                elif dx < 0:  # tail pointing left
                    shapes.Triangle(x + CELL_SIZE, y, x + CELL_SIZE, y + CELL_SIZE, x, center_y, color=(0, 255, 0)).draw()
                elif dy > 0:  # tail pointing up
                    shapes.Triangle(x, y, x + CELL_SIZE, y, center_x, y + CELL_SIZE, color=(0, 255, 0)).draw()
                else:  # tail pointing down
                    shapes.Triangle(x, y + CELL_SIZE, x + CELL_SIZE, y + CELL_SIZE, center_x, y, color=(0, 255, 0)).draw()
            else:
                shapes.Rectangle(x, y, CELL_SIZE, CELL_SIZE, color=(0, 255, 0)).draw()
                # black vertical stripe
                stripe_color = (0, 0, 0)
                stripe_width = 2
                shapes.Rectangle(x + CELL_SIZE//2 - stripe_width//2, y, stripe_width, CELL_SIZE, color=stripe_color).draw()

        self.score_label.draw()

        if self.game_over:
            pyglet.text.Label(
                "Game Over! Press R to restart",
                x=self.window.width // 2,
                y=self.window.height // 2,
                anchor_x='center',
                anchor_y='center',
                color=(255, 255, 255, 255),
                font_size=36
            ).draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.R and self.game_over:
            self.reset()
            return

        if self.game_over:
            return

        if symbol == pyglet.window.key.LEFT and self.direction != (CELL_SIZE, 0):
            self.direction = (-CELL_SIZE, 0)
        elif symbol == pyglet.window.key.RIGHT and self.direction != (-CELL_SIZE, 0):
            self.direction = (CELL_SIZE, 0)
        elif symbol == pyglet.window.key.UP and self.direction != (0, -CELL_SIZE):
            self.direction = (0, CELL_SIZE)
        elif symbol == pyglet.window.key.DOWN and self.direction != (0, CELL_SIZE):
            self.direction = (0, -CELL_SIZE)

    def reset(self):
        start_x = (self.window.width // 2) // CELL_SIZE * CELL_SIZE
        start_y = (self.window.height // 2) // CELL_SIZE * CELL_SIZE
        self.snake = [
            (start_x, start_y),
            (start_x - CELL_SIZE, start_y),
            (start_x - 2 * CELL_SIZE, start_y),
        ]
        self.direction = (CELL_SIZE, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.score_label.text = f"Score: {self.score}"

if __name__ == "__main__":
    game = SnakeGame()
    pyglet.clock.schedule_interval(game.update, 1/6)  # Slower update: 6 FPS instead of 10
    pyglet.app.run()
