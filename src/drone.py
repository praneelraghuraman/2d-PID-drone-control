import pygame.math as math
import numpy as np
from . import helpers


class Drone:
    def __init__(
        self,
        position_m: math.Vector2,
        velocity: math.Vector2,
        attitude: float,
        angular_velocity: float,
        mass: float,
        rotational_inertia: float,
        drag_coefficient: float,
        reference_area: float,
        thrust_coefficient: float,
        rotor_time_constant: float,
        rotor_constant: float,
        omega_b: float,
    ):
        self.mass = mass
        self.rotational_inertia = rotational_inertia
        self.drag_coefficient = drag_coefficient
        self.reference_area = reference_area

        self.left_rotor = Rotor(
            rotor_time_constant, thrust_coefficient, rotor_constant, omega_b
        )
        self.right_rotor = Rotor(
            rotor_time_constant, thrust_coefficient, rotor_constant, omega_b
        )

        self.position_m = position_m
        self.position_px = position_m * 100
        self.velocity = velocity
        self.attitude = attitude
        self.angular_velocity = angular_velocity

        self.air_density = 1.225
        self.width_px = 50
        self.height_px = 10
        self.last_action = [0, 0]

        self.arm_length = 0.25
        self.box = [
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 0],
        ]

    def load_sprite(self, sprite):
        self.sprite = sprite
        self.width_px, self.height_px = self.sprite.get_size()
        self.update_box()

    def step(self, action, dt, wind_vector):
        u_1 = max(0, min(action[0], 1))  # Clamp between 0 and 1
        u_2 = max(0, min(action[1], 1))  # Clamp between 0 and 1
        self.last_action = [u_1, u_2]

        self.left_rotor.set_throttle(u_1)
        self.right_rotor.set_throttle(u_2)

        self.left_rotor.step(dt)
        self.right_rotor.step(dt)

        thrust_1 = self.left_rotor.get_thrust()
        thrust_2 = self.right_rotor.get_thrust()

        thrust_vector: math.Vector2 = math.Vector2(
            np.sin(self.attitude),
            -np.cos(self.attitude),
        ).elementwise() * (thrust_1 + thrust_2)

        gravitational_acceleration = math.Vector2(0, 9.81)

        air_relative_velocity = self.velocity - wind_vector

        if air_relative_velocity.magnitude() != 0:
            drag = (
                0.5
                * self.drag_coefficient
                * self.reference_area
                * self.air_density
                * (air_relative_velocity.magnitude() ** 2)
            ) * -air_relative_velocity.normalize()
        else:
            drag = math.Vector2(0, 0)

        # acceleration = (
        #     thrust_vector.elementwise() / self.mass + gravitational_acceleration
        # )

        acceleration = (
            thrust_vector.elementwise() / self.mass
            + gravitational_acceleration
            + drag.elementwise() / self.mass
        )

        self.velocity = self.velocity + acceleration * dt
        self.position_m = self.position_m + self.velocity * dt
        self.position_px = self.position_m * 100

        torque = (thrust_1 - thrust_2) * self.arm_length
        angular_acceleration = torque / self.rotational_inertia
        self.angular_velocity = self.angular_velocity + angular_acceleration * dt
        self.attitude = self.attitude + self.angular_velocity * dt
        if self.attitude > np.pi:
            self.attitude = -np.pi + np.fmod(self.attitude, np.pi)
        elif self.attitude < -np.pi:
            self.attitude = np.pi + np.fmod(self.attitude, np.pi)

        self.update_box()

    def check_collision(self, walls):
        for wall in walls:
            if helpers.box_line_collided(self.box, wall.coordinates):
                if wall.is_ground:
                    return True, True
                return True, False
        return False, False

    def update_box(self):
        self.box = [
            helpers.rotate_point(
                self.position_px,
                self.position_px
                + math.Vector2(-self.width_px / 2, -self.height_px / 2),
                self.attitude,
            ),
            helpers.rotate_point(
                self.position_px,
                self.position_px + math.Vector2(self.width_px / 2, -self.height_px / 2),
                self.attitude,
            ),
            helpers.rotate_point(
                self.position_px,
                self.position_px + math.Vector2(-self.width_px / 2, self.height_px / 2),
                self.attitude,
            ),
            helpers.rotate_point(
                self.position_px,
                self.position_px + math.Vector2(self.width_px / 2, self.height_px / 2),
                self.attitude,
            ),
        ]

    def get_state(self):
        return (
            self.position_m.x,
            self.position_m.y,
            self.velocity.x,
            self.velocity.y,
            self.attitude,
            self.angular_velocity,
        )

    def reset(
        self,
        position_m: math.Vector2,
        velocity: math.Vector2,
        attitude: float,
        angular_velocity: float,
        mass: float,
        rotational_inertia: float,
        drag_coefficient: float,
        reference_area: float,
        thrust_coefficient: float,
        rotor_time_constant: float,
        rotor_constant: float,
        omega_b: float,
    ):
        self.position_m = position_m
        self.position_px = position_m * 100
        self.velocity = velocity
        self.attitude = attitude
        self.angular_velocity = angular_velocity
        self.mass = mass
        self.rotational_inertia = rotational_inertia
        self.drag_coefficient = drag_coefficient
        self.reference_area = reference_area
        self.left_rotor = Rotor(
            rotor_time_constant, thrust_coefficient, rotor_constant, omega_b
        )
        self.right_rotor = Rotor(
            rotor_time_constant, thrust_coefficient, rotor_constant, omega_b
        )
        self.last_action = [0, 0]
        self.update_box()


# First order model for rotors
class Rotor:
    def __init__(
        self,
        time_constant: float,
        thrust_coefficient: float,
        rotor_constant: float,
        omega_b: float,
    ):
        self.time_constant = time_constant
        self.thrust_coefficient = thrust_coefficient
        self.rotor_constant = rotor_constant
        self.omega_b = omega_b
        self.desired_speed = 0
        self.speed = 0
        self.thrust = 0

    def step(self, dt):
        self.speed = (
            self.speed + ((self.desired_speed - self.speed) / self.time_constant) * dt
        )
        self.thrust = self.thrust_coefficient * self.speed**2

    def set_throttle(self, throttle):
        self.desired_speed = throttle * self.rotor_constant + self.omega_b

    def get_thrust(self):
        return self.thrust

    def reset(self):
        self.desired_speed = 0
        self.speed = 0
        self.thrust = 0
