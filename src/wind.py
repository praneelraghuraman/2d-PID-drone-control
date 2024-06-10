# generate a 2D vector of wind velocities using a steady state,
# turbulence, and gusts.
#
# setup a find field with a 2D grid of points and return a wind vector
# when a position is queried from the grid.
#
# the wind field is defined by three contibutions:
# 1 steady state wind (same as base model)
# 2 continuous turbulence (TODO)
# 3 discrete gusts (based on 1-cos() theory)
import numpy as np
import pygame.math as math
import random


class Wind:
    def __init__(self, max_steady_state=15, max_gust=0, k_gusts=0):
        self.max_steady_state = max_steady_state
        self.max_gust = max_gust
        self.k_gusts = k_gusts

        self.steady_state_on = True
        self.gusts_on = True

        if self.max_steady_state == 0:
            self.steady_state_on = False
        if self.max_gust == 0:
            self.gusts_on = False

        self.current_wind = math.Vector2(0, 0)
        self.t = 0

        # Inspried by https://arc.aiaa.org/doi/full/10.2514/1.C036772
        # there is a list of parameters for the discrete gusts
        # V = (wg0/2)*[1-cos(2*pi*t/lg)]
        # Each gust has:
        #   --theta (primary direction 0-2*pi, where zero is left to right)
        #   --wg0 (max gust velocity - calculated from aggressiveness)
        #   --lg (gust wavelength
        #           -- if 1 the gust is exactly 1s long,
        #           -- we want between 0.1 and 2 seconds duration(ish),
        #           -- therefore lg in range = [0.1 2]
        #   --pos (2D location of its centre)
        #   --t0 (time the gust began in s)
        #
        self.gust_params = []
        self.gust_rate_max = 10  # max of x10 new gusts per second (ish)
        self.last_gust_t0 = 0

        # init based on the current aggressiveness settings
        self.calc_init_wind()

    def calc_init_wind(self):
        # fill in all values in the wind array
        if self.steady_state_on:
            # set the steady state
            random.seed()
            angle = random.uniform(
                0.25 * np.pi, 0.75 * np.pi
            )  # limit to 45 degrees above and below level
            sign = random.choice([-1, 1])
            angle = angle * sign
            self.current_wind = math.Vector2(
                random.uniform(0, self.max_steady_state) * np.sin(angle),
                random.uniform(0, self.max_steady_state) * np.cos(angle),
            )

        if self.gusts_on:
            # randomly decide if a gust is already happening, and append to the list
            # TODO: needs to allow for a random number of gusts to be happening at the start
            if self.prob_gust():
                self.new_gust()

    def prob_gust(self):
        # has a new gust randomly occured. This is based
        # on the time elapsed since the last gust addition

        # 1/K_gusts+.1 = ~0.1-1s
        if (self.t - self.last_gust_t0) > random.uniform(0, 1 / (self.k_gusts + 0.1)):
            return 1
        else:
            return 0

    def new_gust(self):
        # make a new gust
        theta = random.uniform(0, 2 * np.pi)
        wg0 = random.uniform(0, self.max_gust)
        lg = self.loguniform(0.1, 2)
        if self.t == 0:
            t0 = self.loguniform(-lg, 0)  # offset for how far along in time the gust is
        else:
            t0 = self.t
        self.gust_params.append([theta, wg0, lg, t0])
        self.last_gust_t0 = t0

    def step(self, dt):
        # advance the time
        self.t = self.t + dt
        current_gust = math.Vector2(0, 0)
        if self.steady_state_on:
            pass

        if self.gusts_on:
            if self.prob_gust():
                self.new_gust()

            for gust_entry in self.gust_params:
                # find current value of each discrete gust
                # V = (wg0/2)*[1-cos(2*pi*t/lg)]
                rel_t = self.t - gust_entry[3]  # how far into this gust
                # if within the gust period
                if rel_t < gust_entry[2]:
                    gust_v = (gust_entry[1] / 2.0) * (
                        1 - np.cos((2 * np.pi * self.t) / gust_entry[2])
                    )
                    current_gust += math.Vector2(
                        np.sin(gust_entry[0]) * gust_v,
                        np.cos(gust_entry[0]) * gust_v,
                    )
                else:
                    del self.gust_params[
                        self.gust_params.index(gust_entry)
                    ]  # remove the gust from the list
                    # gust is over
        return current_gust

    def get_wind(self, dt):
        # perform any time-stepping updates to the wind field
        current_gust = self.step(dt)

        return self.current_wind + current_gust

    def loguniform(self, low, high):
        # random loguniform number from range expressed in linear scale
        return np.exp(random.uniform(np.log(low), np.log(high)))
