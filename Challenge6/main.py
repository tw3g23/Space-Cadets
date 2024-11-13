import sys
import time
import copy
import math
import numpy as np
from PIL import Image, ImageFilter


class circlesV2:

    def __init__(self, min_radius: int, image: list[list[int]], max_radius=0):
        self.img_width = len(image[0])
        self.img_height = len(image)
        self.min_radius = min_radius
        self.min_centre_x = min_radius
        self.min_centre_y = min_radius
        self.max_centre_x = grey_width - min_radius  # -1
        self.max_centre_y = grey_height - min_radius  # -1
        self.image = image
        self.max_radius = max_radius
        self.generate_accumalator()

    def generate_accumalator(self):
        if self.max_radius == 0:
            if self.img_height > self.img_width:
                max_radius = self.img_width / 2
            else:
                max_radius = self.img_height / 2
        else:
            max_radius = self.max_radius
        self.accumalator = np.zeros((self.img_height, self.img_width, int(max_radius)), int)

    def find_circles(self, accuracy, threshold):
        for x in range(self.img_width):
            for y in range(self.img_height):
                if self.image[y][x] != 0:
                    self.per_pixel_circles(x, y, accuracy)
            print(f'done column: {x}')
        circles = []
        for y in range(len(self.accumalator)):
            for x in range(len(self.accumalator[y])):
                for radius in range(len(self.accumalator[y, x])):
                    accumalated = self.accumalator[y, x, radius]
                    if accumalated > threshold:
                        circles.append(np.array([x, y, radius, accumalated]))
        print(f'Found circles: {circles}')
        return np.array(circles)

    def per_pixel_circles(self, x_coord, y_coord, accuracy):
        last_circle = np.zeros(3, int)
        for theta in range(0, 360 * accuracy):
            last_circle = self.per_angle_circles(x_coord, y_coord, np.radians(theta / accuracy), last_circle)

    def per_angle_circles(self, x_coord, y_coord, theta, last_circle):
        max_radius = self.get_max_radius(x_coord, y_coord, theta)
        for radius in range(self.min_radius, max_radius):
            centre_x = int(x_coord + (radius * math.cos(theta)))
            if centre_x >= self.max_centre_x:
                break
            centre_y = int(y_coord - (radius * math.sin(theta)))
            if centre_y >= self.max_centre_y:
                break
            current_circle = np.array([centre_x, centre_y, radius])
            if current_circle[0] != last_circle[0] and current_circle[1] != last_circle[1] and current_circle[2] != \
                    last_circle[2]:
                last_circle = current_circle
                self.accumalator[centre_y, centre_x, radius] += 1
        return last_circle

    def get_max_radius(self, x_coord, y_coord,
                       theta):  # Returns the maximum radius circle that can fit within the image based on the point on the circumference and angle
        max_radius_left = (x_coord / (abs(math.cos(theta)) + 1))  # - 1
        max_radius_right = (self.img_width - x_coord / (abs(math.cos(theta)) + 1))  # - 1
        max_radius_top = (y_coord / (abs(math.sin(theta)) + 1))  # - 1
        max_radius_bottom = (self.img_height - y_coord / (abs(math.sin(theta)) + 1))  # - 1
        possible_max_radius = np.array([max_radius_left, max_radius_right, max_radius_top, max_radius_bottom], int)
        max = np.min(possible_max_radius)
        if max > self.max_radius and self.max_radius != 0:
            return self.max_radius
        return max


def format(width, height, pixels):
    formatted = []
    for y in range(height):
        row = []
        for x in range(width):
            to_add = [[], [], []]
            for i in range(-1, 2):
                if y + i >= 0 and y + i < height:
                    if x != 0:
                        to_add[i + 1].append(pixels[y + i][x - 1])
                    else:
                        to_add[i + 1].append(0)
                    to_add[i + 1].append(pixels[y + i][x])
                    if x != width - 1:
                        to_add[i + 1].append(pixels[y + i][x + 1])
                    else:
                        to_add[i + 1].append(0)
                else:
                    to_add[i + 1] = [0, 0, 0]
            row.append(to_add)
        formatted.append(row)
    return formatted


def convolve(kernel, image_piece):
    gradient = 0
    for y in range(3):
        for x in range(3):
            gradient = gradient + (kernel[2 - y][2 - x] * image_piece[y][x])
    return gradient


def get_gradients(formated_pixels, edge_threshold):
    gradients = []
    for y in range(len(formated_pixels)):
        gradient_row = []
        for x in range(len(formated_pixels[y])):
            if x == 0 or x == grey_width - 1 or y == 0 or y == grey_height - 1:  # Prevents image border
                gradient_row.append(0)
                continue
            pixel = formated_pixels[y][x]
            gradient_x = convolve(kernel_x, pixel)
            gradient_y = convolve(kernel_y, pixel)
            gradient = int(math.sqrt(math.pow(gradient_x, 2) + math.pow(gradient_y, 2)))
            if gradient > edge_threshold:
                gradient_row.append(255)
            else:
                gradient_row.append(0)
        gradients.append(gradient_row)
    return gradients


def flatten(two_d_list):
    flattened = []
    for row in two_d_list:
        for item in row:
            flattened.append(item)
    return flattened


def multiply(first, second):
    return first @ second


def draw_circles(image, found_circles, accuracy, circles_number, scale):
    top_circles = np.zeros((circles_number, 4), int)
    found_circles = found_circles[found_circles[:, 3].argsort()]

    for j in range(found_circles.shape[0] - 1, -1, -1):
        circle = found_circles[j]
        similar = False
        for i in range(circles_number):
            if abs(circle[0] - top_circles[i, 0]) < 40 // scale and abs(
                    circle[1] - top_circles[i, 1]) < 40 // scale and abs(circle[2] - top_circles[
                i, 2]) < 20 // scale:  # Checks if a similar circle already exists in 'top_circles'
                similar = True
                if circle[3] * ((circle[2] + 1) ** 2) > top_circles[i, 3] * ((top_circles[i, 2] + 1) ** 2):
                    top_circles[i] = circle
                    print(f'adding1: {circle}')
                break
        if not similar:
            for i in range(circles_number):
                if circle[3] * ((circle[2] + 1) ** 2) > top_circles[i, 3] * ((top_circles[i, 2] + 1) ** 2):
                    top_circles[i] = circle
                    print(f'adding2: {circle}')
                    break

    print(f'top_circles: {top_circles}')
    for circle in top_circles:
        centre = (scale * circle[0], scale * circle[1])
        if centre != (0, 0):
            for angle in range(0, 360 * accuracy):
                x = int(scale * (circle[2] * math.cos(math.radians(angle / accuracy)) + circle[0]))
                y = int(scale * (circle[2] * math.sin(math.radians(angle / accuracy)) + circle[1]))
                image = add_square(image, x, y, 2)
            image = draw_cross(image, centre, 5)
            print(f'drawing centre:({scale * circle[0]},{scale * circle[1]})  radius: {circle[2]}')
    return image


def draw_cross(image, centre, size):
    for modifier in range(size):
        image = add_square(image, (centre[0] + modifier), (centre[1] + modifier), 2)
        image = add_square(image, (centre[0] + modifier), (centre[1] - modifier), 2)
        image = add_square(image, (centre[0] - modifier), (centre[1] + modifier), 2)
        image = add_square(image, (centre[0] - modifier), (centre[1] - modifier), 2)

    return image


def convert_to_list(image, img_width, img_height):
    output = []
    for y in range(img_height):
        row = []
        [row.append(image.load()[x, y]) for x in range(0, img_width)]
        output.append(row)
    return output


def add_square(image, point_x, point_y, size):
    for offset_x in range(size):
        for offset_y in range(size):
            if point_x + offset_x < clr_width and point_y + offset_y < clr_height and point_x + offset_x > 0 and point_y + offset_y > 0:
                high_x = point_x + offset_x
                high_y = point_y + offset_y
                image[high_y][high_x] = (0, 255, 0)
                if offset_x != 0 or offset_y != 0:  # Could be omitted for slight efficiency gain
                    low_x = point_x - offset_x
                    low_y = point_y - offset_y
                    image[high_y][low_x] = (0, 255, 0)
                    image[low_y][high_x] = (0, 255, 0)
                    image[low_y][low_x] = (0, 255, 0)
    return image


def remove_particles(image, img_width, img_height, threshold):
    for y in range(img_height):
        for x in range(img_width):
            pixel = image[y][x]
            if pixel != 0:
                accumulator = np.zeros((img_height, img_width), int)
                accumulator, group_size = remove_particle(image, accumulator, x, y, 0, threshold)
                if group_size < threshold:
                    for y_coord in range(img_height):
                        for x_coord in range(img_width):
                            if accumulator[y_coord, x_coord] != 0:
                                image[y_coord][x_coord] = 0
    return image


def remove_particle(image, accumulator, current_x, current_y, group_size, threshold):
    group_size += 1
    accumulator[current_y][current_x] += 1
    if group_size >= threshold:
        return accumulator, group_size
    for i in range(-1, 2, 2):
        if image[current_y][current_x + i] != 0:
            accumulator[current_y, current_x + i] += 1
            if accumulator[current_y, current_x + i] == 1:
                accumulator, group_size = remove_particle(image, accumulator, current_x + i, current_y, group_size,
                                                          threshold)
        if image[current_y + i][current_x] != 0:
            accumulator[current_y + i, current_x] += 1
            if accumulator[current_y + i, current_x] == 1:
                accumulator, group_size = remove_particle(image, accumulator, current_x, current_y + i, group_size,
                                                          threshold)
    return accumulator, group_size


if __name__ == '__main__':
    before = time.time()
    sys.setrecursionlimit(5000)
    reduce_factor = 2
    kernel_x = [[1, 0, -1], [2, 0, -2], [1, 0, -1]]
    kernel_y = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]

    colour_image = Image.open("moon.png")
    clr_width, clr_height = colour_image.size
    grey_image = colour_image.convert("L").reduce(reduce_factor)
    grey_width, grey_height = grey_image.size

    image = convert_to_list(grey_image, grey_width, grey_height)
    circles_image = convert_to_list(colour_image, clr_width, clr_height)
    formatted = format(grey_width, grey_height, image)
    gradient_image = get_gradients(formatted, 150)

    reduced_particles_image = remove_particles(copy.deepcopy(gradient_image), grey_width, grey_height,
                                               40 // reduce_factor)
    testing_circles = circlesV2(20 // reduce_factor, reduced_particles_image)  # , max_radius=100//reduce_factor)
    found_circles = testing_circles.find_circles(1, 70)  # //(reduce_factor**2))

    circles_image = draw_circles(circles_image, found_circles, 3, 1, reduce_factor)
    final_image = Image.new("RGB", (clr_width + grey_width, clr_height))

    joined_image = []
    for y in range(clr_height):
        for pixel in circles_image[y]:
            joined_image.append(pixel)

        if y < grey_height:
            for pixel in gradient_image[y]:
                joined_image.append((pixel, pixel, pixel))
        else:
            for pixel in reduced_particles_image[y - grey_height]:
                joined_image.append((pixel, pixel, pixel))
        print(f'done row: {y}')

    final_image.putdata(joined_image)
    final_image.show()
    print(f'took: {time.time() - before}')


