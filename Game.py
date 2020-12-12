# Import necessary libraries
import pygame
from pygame.locals import *
from pylab import *
import math
import random
import time
import dcgan_game.py

# Init the pygame window
pygame.init()

# Define some key values
# Life of the warrior
life=5
# Size of grids
n=61
# Number of cells in a row and in a column
ROW = 61
COL = 61
# Width and height of each cell
w_cell = 14
h_cell = 14
# Width and height of the window
w = ROW * w_cell
h = COL* h_cell
# Size of the window
size = (w, h)
# Initial levl
level=1

# Define the window to display the pygame
window = pygame.display.set_mode(size)
# Write the caption as the name of the game
pygame.display.set_caption("MYSTERIOUS TOWER")

# Randomly select one pivot around the existing pivot so that if we generate two 55 squares
# whose centers are the existing pivot and the new pivot, the two 585 squares generated will have overlapping areas or sides.
def select(x, y):
    while True:
        a = random.randint(x - 5, x + 5)
        b = random.randint(y - 5, y + 5)
        if abs(x - a) != 5 or abs(y - b) != 5:
            break
    # Return the coordinates of the selected pivot
    return [a, b]


# Select the space around the pivots as space or barriers
def paint(x, y):
    global config
    # First make the 5*5 square with pivot in its center as space on which the player can move
    for a in range(x - 2, x + 3):
        for b in range(y - 2, y + 3):
            config[a, b] = 1
    # Have a 15% probability to have barrier in it
    if random.random() < 0.25:
        for a in range(x - 1, x + 2):
            for b in range(y - 1, y + 2):
                config[a, b] = 0

# Define a function to randomly select a pair of coordinates in the standable places
def locate_random(num_space):
    # Randomly select a number in the range of total number of spaces
    loc=random.sample(range(1,num_space+1),1)[0]
    current=0
    # Iterate the whole map, and find the corresponding coordinates for the randomly selected number
    for a in range(n):
        for b in range(n):
            if config[a, b] != 0:
                current+=1
                if current==loc:
                    return [a,b]

# Initialize the parameters, and the configuration of the map
def initialize():
    global config, selected, current_place, num_space, destination, animal_list

    # Generate an n*n plain to generate the maps (Part 2 Step 1)
    config = zeros([n, n])

    # Create a list to store results of pivots (Part 2 Step 2)
    selected = [0] * 63
    selected[0] = ([int((n - 1) / 2), int((n - 1) / 2)])

    # Generate two new pivots around the existing pivot. Generate 63 pivots in total. (Part 2 Step 3 and 4)
    for i in range(1, 63):
        x = selected[int(math.ceil(i / 2) - 1)][0]
        y = selected[int(math.ceil(i / 2) - 1)][1]
        selected[i] = select(x, y)

    # Record the selections with the paint function
    for k in selected:
        paint(k[0], k[1])

    # Calculate the total number of standable places
    num_space = 0
    for a in range(n):
        for b in range(n):
            if config[a, b] != 0:
                num_space += 1

    # Randomly choose the current plce
    current_place = locate_random(num_space)

    # Iterate for 30 loops to find if there can be a randomly selected coordinates for the posistion of "door"
    for i in range(30):
        destination = locate_random(num_space)
        # Calculate the absolute distance between the starting point and the "door"
        dis=((destination[0]-current_place[0])**2+(destination[1]-current_place[1])**2)**0.5
        # If the abs dis is larger than 20, then place the door there
        if dis>20:
            config[destination[0]][destination[1]]=2
            break
        # Other wise, randomly place the door

    # Randomly choose the position of animals in the level
    animal_list=[]
    # Use 5+level to represents the total num of animals in this level
    while len(animal_list)<5+level:
        # Randomly choose a position
        animal_loc=locate_random(num_space)
        # Calculate the abs dis from the starting point
        dis=((animal_loc[0]-current_place[0])**2+(animal_loc[1]-current_place[1])**2)**0.5
        # If larger than 3 in abs dis, not covering with other animals, and not covering the "door", assign the positions to the animal
        if animal_loc not in animal_list and dis>3 and config[animal_loc[0]][animal_loc[1]]!=2:
            animal_list.append(animal_loc)


# Main function for the game
def main(mode=1,player=2):
    while True:
        # Play the bgm infinitely
        music = pygame.mixer.Sound("game_resources/bgm.wav")
        music.play(-1)
        # Start the game
        startgame()
        # After the introduction page, start the main game
        playgame()
        # Stop the music
        music.stop()
        t_now=time.time()
        # Load the "you lose" voice
        pygame.mixer.music.load("game_resources/youlose.wav")
        # Play it for once
        pygame.mixer.music.play(1)
        # Quit the program after 3 seconds
        while time.time()-t_now<3:
            continue
        break

# Define a function to quit the game
def terminate():
    pygame.quit()
    sys.exit()

# The introduction page
def startgame():
    # Load the introduction page to the window
    gameStart = pygame.image.load("game_resources/gamestart.png")
    window.blit(gameStart, (70, 30))
    pygame.display.update()
    # Listen to the events of the keyboard, if RETURN button is pressed, enter the main game
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_ESCAPE):
                    terminate()
                elif (event.key == pygame.K_RETURN):
                    return

# The function for the main part of the game
def playgame():
    global level,life,cover_surf
    quit = True
    clock = pygame.time.Clock()
    # Initialize the map for the first level
    initialize()
    radius = w_cell * 3
    # Listen to the event of the keyboard
    while quit:
        for event in pygame.event.get():
            # If quit button is clicked, then quit
            if event.type == pygame.QUIT:
                quit = False
            elif event.type == pygame.KEYDOWN:
                # Due to the press of Up, Left, Right, and Down button, move the character
                if event.key == K_LEFT:
                    if config[current_place[0]-1][current_place[1]]!=0:
                        current_place[0]-=1
                elif event.key == K_RIGHT:
                    if config[current_place[0] + 1][current_place[1]] != 0:
                        current_place[0] += 1
                elif event.key == K_UP:
                    if config[current_place[0]][current_place[1]-1] != 0:
                        current_place[1] -= 1
                elif event.key == K_DOWN:
                    if config[current_place[0]][current_place[1] + 1] != 0:
                        current_place[1] += 1

        # When life points go to 0, end the game
        if life==0:
            break

        # Display the levels you are in
        pygame.display.set_caption("MYSTERIOUS TOWEL(Level "+str(level)+")")

        # If the character met the destination
        if current_place==destination:
            # Load next level voice
            pygame.mixer.music.load("game_resources/nextlevel.wav")
            pygame.mixer.music.play(1)
            # Iniatilize the new map
            initialize()
            level+=1
            print("You enter level:", level)

        met_animal=0
        # Iterate the animal list to see if you meet an animal
        for animal in range(len(animal_list)):
            if animal_list[animal]==current_place:
                life-=1
                # Set meet animal value to 1
                met_animal=1
                # Delete the animal from the map
                animal_list.pop(animal)
                # Randomly play the sound of the animal, which is stored in the resources doc
                pygame.mixer.music.load(random.sample(["game_resources/creepylaugh.wav","game_resources/catcall.wav","game_resources/dogcall.wav","game_resources/tigercall.wav"],1)[0])
                pygame.mixer.music.play(1)
                break

        # Move the animal in a given algorithm
        for animal in range(len(animal_list)):
            # Use function 0.01+level*0.005 to act as the probability for each animal to move per millisecond
            if random.random() < 0.01+level*0.005:
                # 50% percent to move vertical
                if random.random()<0.5:
                    move = random.sample([-1, 1], 1)
                    if config[animal_list[animal][0] + move[0]][animal_list[animal][1]] == 1:
                        config[animal_list[animal][0]][animal_list[animal][1]] = 1
                        # Reset the place of the animal
                        animal_list[animal] = [animal_list[animal][0] + move[0], animal_list[animal][1]]
                        config[animal_list[animal][0]][animal_list[animal][1]]=0.5
                # 50% percent to move horizontal
                else:
                    move = random.sample([-1, 1], 1)
                    if config[animal_list[animal][0]][animal_list[animal][1] + move[0]] == 1:
                        config[animal_list[animal][0]][animal_list[animal][1]] = 1
                        animal_list[animal] = [animal_list[animal][0], animal_list[animal][1] + move[0]]
                        config[animal_list[animal][0]][animal_list[animal][1]] = 0.5

        # Make the view super effect of the game
        # Create the center of the clip, which is the warrior
        clip_center = ((current_place[0]+0.5)*w_cell,(current_place[1]+0.5)*w_cell)
        # Create another window to cover the untouchable areas into darkness
        cover_surf = pygame.Surface((radius * 2, radius * 2))
        cover_surf.fill(0)
        cover_surf.set_colorkey((255, 255, 255))
        # Draw the transparent center circle
        pygame.draw.circle(cover_surf, (255, 255, 255), (radius, radius), radius)
        window.fill(0)
        # Display the clip
        clip_rect = pygame.Rect(clip_center[0] - radius, clip_center[1] - radius, radius * 2, radius * 2)
        window.set_clip(clip_rect)

        # Draw the background to white
        pygame.draw.rect(window,(255,255,255), (0, 0, w, h))

        # Draw all the walls and barriers in the map
        for a in range(len(config)):
            for b in range(len(config)):
                left = a * w_cell
                top = b * h_cell
                if config[a][b]== 0:
                    pygame.draw.rect(window, (128,128,128), (left, top, w_cell, h_cell))

        # Draw the warrior(player)
        pygame.draw.circle(window, (255, 0, 0), ((current_place[0]+0.5) * w_cell, (current_place[1]+0.5) * h_cell),w_cell/2)

        # Draw the destination
        pygame.draw.rect(window, (0, 255, 0), (destination[0] * w_cell, destination[1] * h_cell, w_cell, h_cell))

        # Draw the animals
        for animal in animal_list:
            pygame.draw.circle(window, (0, 0, 255),
                               ((animal[0] + 0.5) * w_cell, (animal[1] + 0.5) * h_cell), w_cell / 2)

        # Function to render the level num in the window(Bugs to be fixed)
        # font = pygame.font.SysFont(None, 48)
        # textobj = font.render('Level: {}'.format(level), 1, (255,255,255))
        # textrect = textobj.get_rect()
        # textrect.topleft = (20, 20)
        # window.blit(textobj, textrect)

        # Display the maps situation
        window.blit(cover_surf, clip_rect)
        pygame.display.flip()

        # If the player crashed into an animal
        if met_animal==1:

            # Randomly show the picture of a randomly generated animal(bugs need to be fixed)
            # dcgan_game.create_creature()
            # animal_image = pygame.image.load("animal.png")

            # The current substitute method, to randomly choose an image from two imported monster figure
            animal_image = pygame.image.load(random.sample(["game_resources/q1.png","game_resources/q4.png"],1)[0])
            window.blit(animal_image, ((current_place[0] - 2) * w_cell, (current_place[1] - 2) * w_cell))
            pygame.display.update()

            # Display the image for 1 second
            t_now = time.time()
            while time.time() - t_now < 1:
                continue

        clock.tick(20)

main()