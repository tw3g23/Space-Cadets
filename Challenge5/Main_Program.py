import pygame, Spirographs, time
from PIL import Image



class main_stuff:

    def __init__(self):
        pass


    def execute(self):
        line_thickness = int(input("Enter line thickness: "))
        size = int(input("Enter size multiplier of spirograph: "))
        x = int(input("Enter centre x coordinate: "))
        y = int(input("Enter centre y coordinate: "))
        moving_radius = int(input("Enter moving circle's radius: "))
        fixed_radius = int(input("Enter fixed circle's radius: "))
        accuracy = int(input("Enter accuracy: "))
        pen_position = int(input("Enter pen's position(pen offset): "))
        iterations = int(input("Enter number of iterations of 2 pi: "))

        window_width = 1000
        window_height = 1000
        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption('Fancy Lines')
        time_before = time.time()
        spiro = Spirographs.spirograph(line_thickness, size, (x,y), moving_radius, fixed_radius, accuracy, pen_position, iterations, 1000, 1000)
        to_draw = spiro.get_pixels()
        time_taken = time.time() - time_before

        print(f"done, time taken:{time_taken}")

        self.draw_pixels('red', 1, to_draw, screen)
        pygame.display.flip()

        pygame.display.set_icon(screen)
        pygame.image.save(screen, 'test.png')
        Image.open('test.png').show()
        quit = False
        while not quit: #Wait for the window 'x' button to be pressed then quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit = True
        pygame.quit()


    def draw_pixels(self, colour, speed, to_draw, screen):
        counter = 0
        cap = speed*100 #to speed up drawing process
        for pixel in to_draw:
            screen.set_at(pixel, colour)
            counter+=1
            if counter == cap:
                pygame.display.update()
                counter = 0



if __name__ == '__main__':
    spirograph = main_stuff()
    spirograph.execute()

