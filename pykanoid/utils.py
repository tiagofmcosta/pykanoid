import os
import random
import time

import pygame

BASE_IMAGE_PATH = "data/images/"
RANDOM_GENERATOR = random.Random(time.time_ns())


def load_image(path):
    image = pygame.image.load(BASE_IMAGE_PATH + path).convert_alpha()
    return image


def load_images(path):
    images = {}
    for image_name in os.listdir(BASE_IMAGE_PATH + path):
        images[image_name] = load_image(path + "/" + image_name)
    return images
