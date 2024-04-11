import os
import random
import time

import pygame

BASE_IMAGE_PATH = "data/images/"
RANDOM_GENERATOR = random.Random(time.time_ns())


def get_relative_path(source_path: str):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), "..", source_path))


def load_image(path):
    image = pygame.image.load(get_relative_path(BASE_IMAGE_PATH + path)).convert_alpha()
    return image


def load_images(path):
    images = {}
    for image_name in os.listdir(get_relative_path(BASE_IMAGE_PATH + path)):
        images[image_name] = load_image(path + "/" + image_name)
    return images
