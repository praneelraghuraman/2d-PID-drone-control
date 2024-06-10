import numpy as np
import random
import pygame
import pygame.freetype
from pygame.math import Vector2
from .drone import Drone
from .wind import Wind
from typing import Optional
import pathlib
from . import helpers


class Environment:
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 60,
        "video.frames_per_second": 60,
    }

    def __init__(
        self,
        render_mode: Optional[str] = None,
        render_path=True,
        screen_width=800,
        screen_height=800,
        ui_width=0,
        rand_dynamics_seed=None,
        wind_active=False,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_width = ui_width
        self.last_frame_time = 0
        self.render_mode = render_mode
        self.render_path = render_path

        self.wind_active = wind_active

        # Generate wind vector
        self.wind_vector = Vector2(0, 0)
        self.wind = Wind(5, 1, 0.1)

        # Generate drone
        self.drone = Drone(*self.setup_drone_parameters(rand_dynamics_seed))

        if self.render_mode == "human" or self.render_mode == "rgb_array":
            self.init_pygame()
            self.flight_path = []

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("AMR Assignment 3")
        self.clock = pygame.time.Clock()

        self.drone.load_sprite(
            pygame.image.load(
                str(pathlib.Path(__file__).parents[1].resolve()) + "/images/drone.png"
            ).convert_alpha()
        )

    def step(self, action):
        if self.wind_active:
            self.wind_vector = self.wind.get_wind(1.0 / 60)
        else:
            self.wind_vector = Vector2(0, 0)

        self.drone.step(action, 1.0 / 60, self.wind_vector)

        if self.render_mode == "human" or self.render_mode == "rgb_array":
            self.add_postion_to_flight_path(self.drone.position_px)

    def render(self, manager, target_pos):
        if self.render_mode == None:
            return
        self.screen.fill((243, 243, 243))

        self.draw_ui()

        # Draw drone
        helpers.blit_rotate(
            self.screen,
            self.drone.sprite,
            self.drone.position_px,
            (self.drone.width_px / 2, self.drone.height_px / 2),
            helpers.radians_to_degrees(-self.drone.attitude),
        )

        # Draw drone's path
        if len(self.flight_path) > 2:
            pygame.draw.aalines(self.screen, (16, 19, 97), False, self.flight_path)
        # Draw target
        pygame.draw.circle(
            self.screen, (255, 0, 0), (target_pos[0] * 100, target_pos[1] * 100), 5
        )

        # Draw button panel
        pygame.draw.rect(self.screen, (211, 211, 211), (800, 0, 900, 800))
        manager.draw_ui(self.screen)

        if self.render_mode == "human":
            pygame.display.flip()
            self.clock.tick(60)
        elif self.render_mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
            )

    def draw_ui(self):
        # Draw left throttle command
        pygame.draw.line(  # Background
            self.screen,
            (211, 211, 211),
            (20, 120),
            (20, 20),
            8,
        )
        pygame.draw.line(  # Throttle 1 bar
            self.screen,
            (255, 105, 97),
            (20, 120),
            (20, 120 - np.rint((self.drone.last_action[0] * 100))),
            8,
        )

        # Draw right throttle command
        pygame.draw.line(  # Background
            self.screen,
            (211, 211, 211),
            (40, 120),
            (40, 20),
            8,
        )

        pygame.draw.line(  # Throttle 2 bar
            self.screen,
            (255, 105, 97),
            (40, 120),
            (40, 120 - np.rint((self.drone.last_action[1] * 100))),
            8,
        )

        # Draw wind vector
        if self.wind_vector.magnitude() != 0 and self.wind_active:
            helpers.draw_arrow(
                self.screen,
                Vector2(self.screen_width - self.ui_width - 60, 60)
                - self.wind_vector.normalize() * 50,
                Vector2(self.screen_width - self.ui_width - 60, 60)
                + self.wind_vector.normalize() * 50,
                (108, 171, 221),
                self.wind_vector.magnitude(),
                self.wind_vector.magnitude() * 2,
                self.wind_vector.magnitude() * 2,
            )

    def toggle_wind(self):
        self.wind_active = not self.wind_active

    def setup_drone_parameters(self, rand_dynamics_seed):
        # set up the drone with random values seeded from group number

        random.seed(rand_dynamics_seed)
        mass = random.uniform(0.5, 1.3)
        # Note that the worst case thrust to weight is just over 2
        rotational_inertia = random.uniform(0.25, 0.5)
        drag_coefficient = random.uniform(0.25, 0.75)
        reference_area = random.uniform(0.05, 0.15)
        thrust_coefficient = 0.0000001984
        rotor_time_constant = random.uniform(0.05, 0.1)
        rotor_constant = 6432
        omega_b = 1779

        return (
            Vector2(4, 4),
            Vector2(0, 0),
            0,
            0,
            mass,
            rotational_inertia,
            drag_coefficient,
            reference_area,
            thrust_coefficient,
            rotor_time_constant,
            rotor_constant,
            omega_b,
        )

    def reset(self, rand_dynamics_seed=None, wind_active=False):
        self.drone.reset(*self.setup_drone_parameters(rand_dynamics_seed))
        self.wind_active = wind_active
        self.wind_vector = Vector2(0, 0)
        self.wind = Wind(
            self.wind.max_steady_state, self.wind.max_gust, self.wind.k_gusts
        )
        if self.render_mode == "human" or self.render_mode == "rgb_array":
            self.flight_path = []

    def close(self):
        pygame.quit()

    def add_postion_to_flight_path(self, position):
        self.flight_path.append((position[0], position[1]))
