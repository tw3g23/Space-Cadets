import pygame, Spirographs, Main_Program, time
from PIL import Image

if __name__ == '__main__':
    window_width = 1000
    window_height = 1000
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption('Fancy Lines')
    time_before = time.time()
    spiro1 = Spirographs.spirograph(1, 3, (500, 500), 9, 110, 40, 5, 100, 1000, 1000)
    spiro1 = Spirographs.spirograph(1, 1, (500, 500), 140, 72, 40, 94, 100, 1000, 1000)
    spiro1 = Spirographs.spirograph(1, 2, (500, 500), 14, 140, 40, 5, 100, 1000, 1000)
    spiro1 = Spirographs.spirograph(1, 1, (500, 500), 18, 5, 40, 3, 100, 1000, 1000)
    to_draw = spiro1.get_pixels()
    time_taken = time.time() - time_before
    print(f"done, time taken:{time_taken}")
    program = Main_Program.main_stuff()
    program.draw_pixels('red', 1, to_draw, screen)
    pygame.display.flip()
    pygame.display.set_icon(screen)
    pygame.image.save(screen, 'test.png')
    Image.open('test.png').show()
    quit = False
    while not quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
    pygame.quit()