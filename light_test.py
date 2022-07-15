import numpy as np

import board
import neopixel

from time import sleep
from picamera import PiCamera, array

from random import random


NUM_PIXELS = 128
MAX_BRIGHTNESS = 0.1


pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=MAX_BRIGHTNESS, auto_write=False)


def rainbow_generator(n):
    color = np.array((0, 0, 0))
    val = 4 * 255 // n
    i = 0
    while True:
        i %= 3
        color[i] = 255
        while color[i] >= 0:
            yield color
            color[i] -= val
            color[(i+1)%3] = 255 - color[i]
        color[i] = 0
        i += 1


def shoot(color = (255, 0, 0)):
    pixels[0] = color
    pixels.show()
    sleep(.01)

    for i in range(1, NUM_PIXELS):
        pixels[i-1] = (0, 0, 0)
        pixels[i] = color
        pixels.show()
        sleep(.01)

    for i in range(NUM_PIXELS-2, -1, -1):
        pixels[i+1] = (0, 0, 0)
        pixels[i] = color
        pixels.show()
        sleep(.01)

    pixels[0] = (0, 0, 0)
    pixels.show()


def bounce(n, left=0, right=NUM_PIXELS):
    points = [left+ int(random()*(right-left)) for _ in range(n)]
    points.sort()
    dirs = [1]*len(points)
    dirs[-1] = -1

    def safety_check():
        for i in range(n):
            assert left <= points[i] < right, points

    def move():
        for i in range(n):
            points[i] += dirs[i]
            if points[i] >= right:
                points[i] = left
            elif points[i] < left:
                points[i] = right-1

    def colorset():
        safety_check()
        color = rainbow_generator(len(points))
        for p in points:
            pixels[p] = next(color)

    def blackout():
        safety_check()
        for p in points:
            pixels[p] = (0, 0, 0)

    def dir_update():
        for i in range(n):
            if abs(points[i-1] - points[i]) <= 1:
                dirs[i-1] *= -1
                dirs[i] *= -1

    while True:
        print()
        print(' '.join(map(lambda i: str(i).ljust(3), points)))
        print(' '.join(map(lambda i: str(i).ljust(3), dirs)))

        colorset()
        pixels.show()
        sleep(0.04)
        blackout()

        move()

        dir_update()


def train(n_points, n_colors=64, left=32):
    train_color = rainbow_generator(n_colors)
    bullet_color = rainbow_generator(n_colors)

    right = NUM_PIXELS - left

    def set_color(j, color):
        pixels[j+left] = color

    for i in range(n_points):
        pixels[i+left] = next(train_color)

    i = right-1
    j = n_points-1

    t = 0

    while True:
        set_color(j, (0, 0, 0))
        j += 1
        j %= right

        if j != i:
            c = next(bullet_color)  # np.random.randint(0, 256, 3)
        else:
            c = next(train_color)

        set_color(j, c)

        if j == i:
            j += n_points
            j %= right
            i -= 1
            i %= right

        pixels.show()
        sleep(0.01 * np.sin(t)**4)
        t += 0.2
        t %= 2*np.pi


if __name__ == "__main__":
    try:
        print("zeroing")
        pixels.fill((0, 0, 0))
        pixels.show()
        sleep(1)
        print("done.")
        #shoot()
        n_colors = 64
        #for i, c in zip(range(n_colors), rainbow_generator(n_colors)):
        #    print(i, c)
        #    pixels.fill(c)
        #    pixels.show()
        #    sleep(0.0001)
        #pixels.fill((0, 0, 0))
        #bounce(n_colors, 36, 86)
        train(16, n_colors=n_colors)

    finally:
        pixels.fill((0, 0, 0))
        pixels.show()

