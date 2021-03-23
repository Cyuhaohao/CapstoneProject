# Import necessary libraries
import pygame
from pygame.locals import *
from pylab import *
import math
import random
import time
import sys
# import dcgan_game





'''
This part show the map generation algorithms
'''

# Define a function to randomly select a pair of coordinates in the standable places
def locate_random(num_space,way):
    # Randomly select a number in the range of total number of spaces
    loc=random.sample(range(1,num_space),1)[0]
    current=0
    # Iterate the whole map, and find the corresponding coordinates for the randomly selected number
    if way=="random":
        for a in range(n):
            for b in range(n):
                if config[a, b] != 0:
                    current+=1
                    if current==loc:
                        return [a,b]
    elif way=="inroom":
        for a in range(n):
            for b in range(n):
                if config[a, b] == 7:
                    current += 1
                    if current == loc:
                        return [a, b]

# The function to
def placement(way="random"):
    global config, current_place, num_space, destination, animal_list, ai_current_place

    # Calculate the total number of standable places
    num_space = 0
    if way=="random":
        for a in range(n):
            for b in range(n):
                if config[a, b] != 0:
                    num_space += 1

    elif way=="inroom":
        for a in range(n):
            for b in range(n):
                if config[a, b] == 7:
                    num_space += 1

    # Randomly choose the current place
    current_place = locate_random(num_space,way)
    ai_current_place = [current_place[0],current_place[1]]

    find_door=0
    # Iterate for 30 loops to find if there can be a randomly selected coordinates for the posistion of "door"
    for i in range(30):
        destination = locate_random(num_space,way)
        # Calculate the absolute distance between the starting point and the "door"
        dis = ((destination[0] - current_place[0]) ** 2 + (destination[1] - current_place[1]) ** 2) ** 0.5
        # If the abs dis is larger than 20, then place the door there
        if dis > n/3:
            config[destination[0]][destination[1]] = 2
            find_door=1
            break
        # Other wise, randomly place the door
    if find_door==0:
        config[destination[0]][destination[1]] = 2


    # Randomly choose the position of animals in the level
    animal_list = []
    # Use 5+level to represents the total num of animals in this level
    while len(animal_list) < 5 + level:
        # Randomly choose a position
        animal_loc = locate_random(num_space,way)
        if animal_loc==None:
            continue
        # Calculate the abs dis from the starting point
        dis = ((animal_loc[0] - current_place[0]) ** 2 + (animal_loc[1] - current_place[1]) ** 2) ** 0.5
        # If larger than 3 in abs dis, not covering with other animals, and not covering the "door", assign the positions to the animal
        if dis > 3 and config[animal_loc[0]][animal_loc[1]] != 2:
            animal_list.append(animal_loc)
            config[animal_loc[0]][animal_loc[1]]=3


# Create a class for Room Overlay map generation algorithm
class Roomoverlay():
    # Randomly select one pivot around the existing pivot so that if we generate two 55 squares
    # whose centers are the existing pivot and the new pivot, the two 585 squares generated will have overlapping areas or sides.
    def select(self,x, y):
        while True:
            a = random.randint(x - 5, x + 5)
            b = random.randint(y - 5, y + 5)
            if abs(x - a) != 5 or abs(y - b) != 5:
                break
        # Return the coordinates of the selected pivot
        return [a, b]


    # Select the space around the pivots as space or barriers
    def paint(self,x, y):
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

    # Initialize the parameters, and the configuration of the map
    def initialize(self):
        global config

        # Generate an n*n plain to generate the maps (Part 2 Step 1)
        config = zeros([n, n])

        # Create a list to store results of pivots (Part 2 Step 2)
        selected = [0] * 63
        selected[0] = ([int((n - 1) / 2), int((n - 1) / 2)])

        # Generate two new pivots around the existing pivot. Generate 63 pivots in total. (Part 2 Step 3 and 4)
        for i in range(1, 63):
            x = selected[int(math.ceil(i / 2) - 1)][0]
            y = selected[int(math.ceil(i / 2) - 1)][1]
            selected[i] = self.select(x, y)

        # Record the selections with the paint function
        for k in selected:
            self.paint(k[0], k[1])

        placement()


# Create a class for the Dungeon map generation algorithm
class Dungeon():

    # Check if there is place to put the corridor
    def check_nearby(self,x,y,x_pre,y_pre):
        x_p=[x-1,x,x+1]
        y_p=[y-1,y,y+1]
        if x==x_pre:
            y_p.remove(y_pre)
        elif y==y_pre:
            x_p.remove(x_pre)

        for x_coor in x_p:
            for y_coor in y_p:
                if x_coor<0 or y_coor<0 or x_coor>=n or y_coor>=n:
                    return False
                elif config[x_coor][y_coor]!=0:
                    return False
        return True

    # Move the corridor to attain all the places in the room
    def connector_move(self,x,y):
        global config

        # Random select a direction
        random_list=[[1,0],[-1,0],[0,1],[0,-1]]
        random.shuffle(random_list)

        # Check if the corridor can go in certain directions
        if self.check_nearby(x+random_list[0][0], y+random_list[0][1],x,y):
            config[x+random_list[0][0], y+random_list[0][1]]=1
            self.connector_move(x+random_list[0][0],y+random_list[0][1])
        if self.check_nearby(x+random_list[1][0], y+random_list[1][1],x,y):
            config[x+random_list[1][0], y+random_list[1][1]]=1
            self.connector_move(x+random_list[1][0],y+random_list[1][1])
        if self.check_nearby(x+random_list[2][0], y+random_list[2][1],x,y):
            config[x+random_list[2][0], y+random_list[2][1]]=1
            self.connector_move(x+random_list[2][0],y+random_list[2][1])
        if self.check_nearby(x+random_list[3][0], y+random_list[3][1],x,y):
            config[x+random_list[3][0], y+random_list[3][1]]=1
            self.connector_move(x+random_list[3][0],y+random_list[3][1])
        return

    # Main function to generate the map
    def initialize(self):
        global config,n

        n=np.min([20+2*level,61])
        lower_b=int(level/3)+2
        upper_b=int(level/2)+4

        config = zeros([n, n])

        # Locate the room
        square_loc=[]
        for i in range(200):
            r_w=random.randint(lower_b,upper_b)
            r_l=random.randint(lower_b,upper_b)
            place_x=random.randint(3,n - 3 - r_w)
            place_y = random.randint(3, n - 3-r_l)
            occupied=0
            for x in range(r_w+6):
                for y in range(r_l+6):
                    if config[place_x+x-3][place_y+y-3]!=0:
                        occupied=1
                        break
                if occupied==1:
                    break
            if occupied==0:
                for x in range(r_w):
                    for y in range(r_l):
                        config[place_x + x][place_y + y]=7
                square_loc.append([place_x,place_y,place_x + x,place_y + y])
        last_loc=square_loc[-1]
        xlist=[last_loc[0],last_loc[2]]

        #Select the starting point
        for x in range(2):
            for y in range(last_loc[1],last_loc[3]+1):
                cur_coor=[xlist[x],y]
                if self.check_nearby(cur_coor[0]+(x*2-1),cur_coor[1],cur_coor[0],cur_coor[1]):
                    config[cur_coor[0]+(x*2-1)][cur_coor[1]]=1
                    break

        # MOve the corridor to attain all the places in the room
        self.connector_move(cur_coor[0]+(x*2-1),cur_coor[1])

        # Connect the corridors with room
        for i in range(len(square_loc)-1):
            loc_now=square_loc[i]
            chosen_line=random.randint(0,3)
            connected=0
            if chosen_line in [0,2]:
                for y in range(loc_now[1],loc_now[3]+1):
                    if config[loc_now[chosen_line]+2*(chosen_line-1)][y]==1:
                        config[loc_now[chosen_line]+(chosen_line-1)][y]=1
                        connected=1
                        break
            else:
                for x in range(loc_now[0],loc_now[2]+1):
                    if config[x][loc_now[chosen_line]+2*(chosen_line-2)]==1:
                        config[x][loc_now[chosen_line]+(chosen_line-2)]=1
                        connected = 1
                        break
            if connected==0:
                for x in range(loc_now[0],loc_now[2]+1):
                    for y in range(loc_now[1], loc_now[3] + 1):
                        config[x][y]=0

        # Place other nodes
        placement(way="inroom")

        for x in range(61):
            for y in range(61):
                if x<n and y<n:
                    if config[x][y]==7:
                        config[x][y]=1






'''
This part show the GAME AI algorithms
'''

# Define the function for intelligent agent player to check the surrondings.
def look_around(x, y,config_copy,pre_loc,mode="random"):

    # Check whether there is door nearby
    door_pos=[]
    for x_c in range(np.max([0,x-3]),np.min([x+4,n])):
        for y_c in range(np.max([0,y-3]),np.min([y+4,n])):
            if [x_c,y_c] not in [[x-3,y-3],[x-3,y+4],[x+4,y-3],[x+4,y+4]]:
                # Record the place of the door
                if config[x_c][y_c]==2:
                    door_pos=[x_c,y_c]

    # Check the spaces in each direction and the Prospect Score
    potentiallist = []
    potenticalscore = []
    if config[x-1, y] != 0:
        potentiallist.append([x-1,y])
        pscore=0
        for x_c in range(np.max([0,x-3]),x):
            for y_c in range(np.max([0,y-3]),np.min([y+4,n])):
                if [x_c, y_c] not in [[x - 3, y - 3], [x - 3, y + 4]]:
                    if config[x_c][y_c]==1 and config_copy[x_c][y_c]==1:
                        pscore+=1
        potenticalscore.append(pscore)

    if config[x, y+1] != 0:
        potentiallist.append([x, y+1])
        pscore=0
        for x_c in range(np.max([0,x-3]),np.min([x+4,n])):
            for y_c in range(y, np.min([y + 4, n])):
                if [x_c, y_c] not in [[x - 3, y+4], [x+4, y + 4]]:
                    if config[x_c][y_c] == 1 and config_copy[x_c][y_c] == 1:
                        pscore += 1
        potenticalscore.append(pscore)

    if config[x+1, y] != 0:
        potentiallist.append([x+1, y])
        pscore=0
        for x_c in range(x,np.min([x+4,n])):
            for y_c in range(np.max([0, y - 3]), np.min([y + 4, n])):
                if [x_c, y_c] not in [[x+4, y - 3], [x+4, y + 4]]:
                    if config[x_c][y_c] == 1 and config_copy[x_c][y_c] == 1:
                        pscore += 1
        potenticalscore.append(pscore)

    if config[x, y-1] != 0:
        potentiallist.append([x, y-1])
        pscore=0
        for x_c in range(np.max([0,x-3]),np.min([x+4,n])):
            for y_c in range(np.max([0, y - 3]), y):
                if [x_c, y_c] not in [[x - 3, y - 3], [x +4, y -3]]:
                    if config[x_c][y_c] == 1 and config_copy[x_c][y_c] == 1:
                        pscore += 1
        potenticalscore.append(pscore)

    # If there is a door nearby, use A* algorithm to move towards the door
    if door_pos!=[]:
        new_potlist=[]
        for i in potentiallist:
            if config_copy[i[0]][i[1]]==1 and config[i[0]][i[1]]!=3:
                new_potlist.append(i)
        pot_dis=[]
        if new_potlist!=[]:
            for i in new_potlist:
                pot_dis.append(abs(i[0]-door_pos[0])+abs(i[1]-door_pos[1]))
            return new_potlist[pot_dis.index(np.min(pot_dis))]

    # Follow the RandomWalk Algorithm's instructing rules described in the paper
    if mode=="random":
        worst_choice=[]
        bad_choice=[]
        normal_choice=[]
        great_choice=[]
        for i in potentiallist:
            if config[i[0]][i[1]]==2:
                return i
            elif config[i[0]][i[1]]==3:
                worst_choice.append(i)
            elif config_copy[i[0]][i[1]]==1:
                great_choice.append(i)
            elif i in pre_loc:
                bad_choice.append(i)
            else:
                normal_choice.append(i)

        if len(great_choice)>0:
            score_list=[]
            for i in great_choice:
                score_list.append(potenticalscore[potentiallist.index(i)])
            return great_choice[score_list.index(np.max(score_list))]
        elif len(normal_choice)>0:
            score_list = []
            for i in normal_choice:
                score_list.append(potenticalscore[potentiallist.index(i)])
            max_score=np.max(score_list)
            possible_i=[]
            for i in range(len(score_list)):
                if score_list[i]==max_score:
                    possible_i.append(i)
            return normal_choice[random.sample(possible_i,1)[0]]
        elif len(bad_choice)>0:
            return random.sample(bad_choice, 1)[0]
        else:
            return random.sample(worst_choice, 1)[0]

    if mode=="findspace":
        return potentiallist[potenticalscore.index(np.max(potenticalscore))]

    # Follow the WallFollow Algorithm's instructing rules described in the paper
    if mode=="wallfollow":
        if pre_loc[-1]==[]:
            return potentiallist[0]

        # Mark the explored or barriers grids as explored
        notexplored=[]
        for i in potentiallist:
            if config_copy[i[0]][i[1]]==1 and config[i[0]][i[1]]==1:
                notexplored.append(i)

        # Find the next direction to go
        right_direction=[]
        if pre_loc[-1][0]==x:
            if pre_loc[-1][1]==y-1:
                right_direction=[x,y+1]
            else:
                right_direction=[x,y-1]
        elif pre_loc[-1][1]==y:
            if pre_loc[-1][0]==x-1:
                right_direction = [x+1, y]
            else:
                right_direction=[x-1,y]

        # Have available directions
        direction_seq=[[x,y-1],[x-1,y],[x,y+1],[x+1,y]]

        # If not explored, check whether we can go (step5 in the paper's rules)
        if direction_seq[direction_seq.index(right_direction)-1] in notexplored:
            return direction_seq[direction_seq.index(right_direction)-1]
        elif right_direction in notexplored:
            return right_direction
        elif direction_seq[(direction_seq.index(right_direction)+1)%4] in notexplored:
            return direction_seq[(direction_seq.index(right_direction)+1)%4]
        else:
            for i in potentiallist:
                if config[i[0]][i[1]]==3:
                    potenticalscore[potentiallist.index(i)]=-2
                if i in pre_loc:
                    potenticalscore[potentiallist.index(i)]=-1
            possible_result=[]
            for i in range(len(potenticalscore)):
                if potenticalscore[i]==np.max(potenticalscore):
                    possible_result.append(potentiallist[i])
            return random.sample(possible_result,1)[0]


# Define the class for randomwalk algorithm
class RandomMove():
    # Initialize the room and parameters
    def __init__(self,mode="random"):
        self.config_copy =[]
        self.mode=mode
        self.pre_loc=[[]]*30

    # Restart the ai when entering a new level
    def start_ai(self):
        self.config_copy = []
        self.pre_loc = [[]] * 30
        # Generate the map record in the class
        for x in range(n):
            line_x=[]
            for y in range(n):
                if ai_current_place==[x,y]:
                    line_x.append(4)
                else:
                    line_x.append(1)
            self.config_copy.append(line_x)

    # Decide the next step of the agent
    def move(self):
        global config, ai_current_place
        next_choice = look_around(ai_current_place[0], ai_current_place[1],self.config_copy,self.pre_loc,mode=self.mode)
        self.pre_loc=self.pre_loc[1:]
        self.pre_loc.append(ai_current_place)
        ai_current_place=next_choice
        self.config_copy[next_choice[0]][next_choice[1]]=4
        # for x_c in range(np.max([0, next_choice[0] - 3]), np.min([next_choice[0] + 4, n])):
        #     for y_c in range(np.max([0, next_choice[1] - 3]), np.min([next_choice[1] + 4, n])):
        #         self.config_copy[x_c][y_c] = 4

# Define the class for wallfollow algorithm
class WallFollow():
    #Initiaze the AI agent
    def __init__(self):
        self.config_copy =[]
        self.pre_loc=[[]]*30
        self.mode=0

    # Restart the ai when entering a new level
    def start_ai(self):
        self.mode=0
        self.config_copy = []
        self.pre_loc=[[]]*30
        # Generate the map record in the class
        for x in range(n):
            line_x=[]
            for y in range(n):
                if ai_current_place==[x,y]:
                    line_x.append(4)
                else:
                    line_x.append(1)
            self.config_copy.append(line_x)

    # Decide the next step of the agent
    def move(self):
        global config, ai_current_place
        if self.mode==0:
            if config[ai_current_place[0]-1][ai_current_place[1]]==1:
                next_choice=[ai_current_place[0]-1,ai_current_place[1]]
            else:
                self.mode=1
        if self.mode==1:
            next_choice = look_around(ai_current_place[0], ai_current_place[1], self.config_copy, self.pre_loc, mode="wallfollow")
        self.pre_loc = self.pre_loc[1:]
        self.pre_loc.append(ai_current_place)
        ai_current_place = next_choice
        self.config_copy[next_choice[0]][next_choice[1]] = 4





'''
This part is the Gameplay part
'''

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
ai_speed=3


# Define the window to display the pygame
window = pygame.display.set_mode((14*n,14*n))
# Write the caption as the name of the game
pygame.display.set_caption("MYSTERIOUS TOWER")



# Main function for the game
def main(map_generation="myway",cover="on",ai=None,mode=1,player=2):
    while True:
        # Play the bgm infinitely
        music = pygame.mixer.Sound("game_resources/bgm.wav")
        music.play(-1)
        # Start the game
        startgame()
        # After the introduction page, start the main game
        playgame(map_generation,cover,ai)
        # Stop the music
        music.stop()
        t_now=time.time()
        # Load the "you lose" voice
        if ai==None:
            pygame.mixer.music.load("game_resources/youlose.wav")
        else:
            pygame.mixer.music.load("game_resources/oppowins.wav")
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
def playgame(map_generation,cover,ai):
    global level,life,cover_surf
    ai_timer = 0
    quit = True
    clock = pygame.time.Clock()
    # Initialize the map for the first level
    if map_generation=="myway":
        roomoverlay=Roomoverlay()
        roomoverlay.initialize()
    elif map_generation=="dungeon":
        dungeon=Dungeon()
        dungeon.initialize()
    radius = w_cell * 3.5
    if ai!=None:
        ai.start_ai()
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

        # when AI get to the place, you lose
        if ai != None:
            if ai_current_place==destination:
                break

        # Display the levels you are in
        pygame.display.set_caption("MYSTERIOUS TOWEL(Level "+str(level)+")")

        # If the character met the destination
        if current_place==destination:
            # Load next level voice
            pygame.mixer.music.load("game_resources/nextlevel.wav")
            pygame.mixer.music.play(1)
            # Iniatilize the new map
            if map_generation == "myway":
                roomoverlay.initialize()
            elif map_generation == "dungeon":
                dungeon.initialize()
            if ai!=None:
                ai.start_ai()
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
                        config[animal_list[animal][0]][animal_list[animal][1]]=3
                # 50% percent to move horizontal
                else:
                    move = random.sample([-1, 1], 1)
                    if config[animal_list[animal][0]][animal_list[animal][1] + move[0]] == 1:
                        config[animal_list[animal][0]][animal_list[animal][1]] = 1
                        animal_list[animal] = [animal_list[animal][0], animal_list[animal][1] + move[0]]
                        config[animal_list[animal][0]][animal_list[animal][1]] = 3

        if ai!=None:
            if ai_timer%4==0:
                ai.move()
            ai_timer+=ai_speed

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
        if cover=="on":
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
                if ai!=None and cover=='off':
                    if ai.config_copy[a][b]==4:
                        pygame.draw.rect(window, (0, 100, 0), (left, top, w_cell, h_cell))

        # Draw the warrior(player)
        pygame.draw.circle(window, (255, 0, 0), ((current_place[0]+0.5) * w_cell, (current_place[1]+0.5) * h_cell),w_cell/2)

        # Draw the AI warrior(player)
        if ai != None:
            pygame.draw.circle(window, (120, 0, 0), ((ai_current_place[0] + 0.5) * w_cell, (ai_current_place[1] + 0.5) * h_cell),w_cell / 2)

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
        if cover=="on":
            window.blit(cover_surf, clip_rect)
        pygame.display.flip()

        # If the player crashed into an animal
        if met_animal==1:

            # Randomly show the picture of a randomly generated animal(bugs need to be fixed)
            # dcgan_game.create_creature()
            # animal_image = pygame.image.load("animal.png")

            monster_list=["game_resources/q1.png",
                          "game_resources/q4.png"]

            # Randomly choose an image generated monster figure
            animal_image = pygame.image.load(random.sample(monster_list,1)[0])
            window.blit(animal_image, ((current_place[0] - 2) * w_cell, (current_place[1] - 2) * w_cell))
            pygame.display.update()

            # Display the image for 1 second
            t_now = time.time()
            while time.time() - t_now < 1:
                continue

        clock.tick(20)




'''
This part is the input and operation part 
'''

# Generate the AI warriors with different GAME AI algorithms
randommove_ai=RandomMove()
wallfollow_ai=WallFollow()

# Start the game, let the player to choose modes
if len(sys.argv)==1:
    while True:
        mode_choose=input("Choose the mode:\n1. Classic\n2. PvE\n")
        if mode_choose in ['1','2']:
            break
        else:
            print("Please enter 1 or 2")
    while True:
        map_choose=input("Choose the map:\n1. Classic\n2. Dungeon\n")
        if map_choose in ['1','2']:
            break
        else:
            print("Please enter 1 or 2")
    if mode_choose=='2':
        while True:
            difficulty_choose = input("Choose the difficulty:\n1. Easy\n2. Hard\n")
            if difficulty_choose in ['1','2']:
                main(map_generation=["myway", "dungeon"][int(map_choose) - 1], cover="on",
                     ai=[randommove_ai, wallfollow_ai][int(difficulty_choose) - 1])
                break
            else:
                print("Please enter 1 or 2")
    else:
        main(map_generation=["myway","dungeon"][int(map_choose)-1], cover="on", ai=None)

# Choose the superviosr mode
if len(sys.argv)==2:
    while True:
        mode_choose=input("Choose the mode:\n1. Classic\n2. PvE\n")
        if mode_choose in ['1','2']:
            break
        else:
            print("Please enter 1 or 2")
    while True:
        map_choose = input("Choose the map:\n1. Classic\n2. Dungeon\n")
        if map_choose in ['1', '2']:
            break
        else:
            print("Please enter 1 or 2")
    if mode_choose == '2':
        while True:
            difficulty_choose = input("Choose the difficulty:\n1. Easy\n2. Hard\n")
            if difficulty_choose in ['1', '2']:
                main(map_generation=["myway", "dungeon"][int(map_choose) - 1], cover="off",
                     ai=[randommove_ai, wallfollow_ai][int(difficulty_choose) - 1])
                break
            else:
                print("Please enter 1 or 2")
    else:
        main(map_generation=["myway", "dungeon"][int(map_choose) - 1], cover="off", ai=None)
