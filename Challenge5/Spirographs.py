import math, threading


class spirograph:

    _draw_order = []
    _display = []
    _display_width = 0
    _display_height = 0

    def __init__(self, line_thickness, size, centre, moving_radius, fixed_radius, accuracy, pen_position, iterations, display_width, display_height):
        self._display_width = display_width
        self._display_height = display_height
        for height in range(0, display_height):
            self._display.append([])
            for width in range(0, display_width):
                self._display[height].append(False)

        threads = []
        for i in range(iterations): #break each multiple of 2pi into a separate thread
            threads.append(threading.Thread(target=self.perform_iteration,args=(line_thickness,size,centre,moving_radius,fixed_radius,accuracy,pen_position,int(i*(360*accuracy)))))
            threads[i].start()
        for thread in threads:
            thread.join()


    def perform_iteration(self, line_thickness, size, centre, moving_radius, fixed_radius, accuracy, pen_pos, iteration_start): #Performs an iteration of 2pi
        precalculated_0=fixed_radius - moving_radius
        precalculated_1=(fixed_radius / moving_radius) - 1
        for theta in range(iteration_start, int(iteration_start + (360 * accuracy)), 1):
            theta_divided = math.radians(theta/accuracy)
            x = int(((precalculated_0 * math.cos(theta_divided)) + (
                        pen_pos * math.cos(precalculated_1 * theta_divided))) * size +
                    centre[0])
            y = int(((precalculated_0 * math.sin(theta_divided)) - (
                        pen_pos * math.sin(precalculated_1 * theta_divided))) * size +
                    centre[1])
            self.add_square(line_thickness, (x,y))
            current = (x, y)
            if theta == iteration_start:
                previous = current
            elif not self.check_points_attached(line_thickness, previous, current):
                self.between_points(line_thickness, previous, current)
            previous = current



    def get_pixels(self):
        return self._draw_order

    def add_square(self, size, point): #Add pixels needing to be drawn to the to_draw list and display matrix
        if point[0] >= self._display_width or point[1] >= self._display_height or point[0] < 0 or point[1] < 0:
            return
        pixels = []
        for offset_x in range(size):
            for offset_y in range(size):
                pixels.append((point[0] + offset_x, point[1] + offset_y))
                if offset_x != 0 or offset_y != 0: #Could be omitted for slight efficiency gain
                    pixels.append((point[0] - offset_x, point[1] - offset_y))
                    pixels.append((point[0] - offset_x, point[1] + offset_y))
                    pixels.append((point[0] + offset_x, point[1] - offset_y))
        for pixel in pixels:
            if not self._display[pixel[0]][pixel[1]]:
                self._draw_order.append(pixel)
                self._display[pixel[0]][pixel[1]] = True


    def check_points_attached(self, size, point1, point2): #Checks if 2 points are next to each other in any direction
        #return True
        if abs(point1[0] - point2[0]) <= 1 and abs(point1[1] - point2[1]) <= 1:
            return True
        return False


    def between_points(self, size, point1, point2): #Plots pixels between the gap of two points
        delta_x = point1[0] - point2[0]
        delta_y = point1[1] - point2[1]
        to_plot = 0
        if delta_x == 0:
            if delta_y < 0:
                for y in range(point1[1] + 1, point2[1]):
                    self.add_square(size, (point1[0], y))
            else:
                for y in range(point2[1] + 1, point1[1]):
                    self.add_square(size, (point1[0], y))
        elif delta_y == 0:
            if delta_x < 0:
                for x in range(point1[0] + 1, point2[0]):
                    self.add_square(size, (x, point1[1]))
            else:
                for x in range(point2[0] + 1, point1[0]):
                    self.add_square(size, (x, point1[1]))
        elif abs(delta_x) < abs(delta_y):
            to_plot = abs(delta_y)
        else:
            to_plot = abs(delta_x)
        previous_point = point2
        counter = 1
        while not self.check_points_attached(size, previous_point, point1) and counter < to_plot:
            current_point = (previous_point[0] + (delta_x // to_plot), previous_point[1] + (delta_y // to_plot))
            if not self.check_points_attached(size, previous_point, current_point): #If the newly placed point is not next to the previous method recursively called until all points attached
                self.between_points(size, previous_point, current_point)
            self.add_square(size, current_point)
            counter += 1
            previous_point = current_point
        return





