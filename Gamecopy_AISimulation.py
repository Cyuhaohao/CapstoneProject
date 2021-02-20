# Do the Monte Carlo analysis to compare RW and WF algorithms' efficiency

# Import necessary libraries
from pylab import *
import math
import random
import matplotlib.pyplot as plt

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

def placement(way="random"):
    global config, current_place1, current_place2, num_space, destination, animal_list

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
    current_place1 =current_place
    current_place2 =current_place

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

# Initialize the parameters, and the configuration of the map
def initialize():
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
        selected[i] = select(x, y)

    # Record the selections with the paint function
    for k in selected:
        paint(k[0], k[1])

    placement()

def check_nearby(x,y,x_pre,y_pre):
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


# The core function for this part
def simulate():
    global level
    rm_steps_levels = []
    wf_steps_levels = []

    # Iterate for each level
    for l in range(1,21):
        level = l
        rm_steps_list = []
        wf_steps_list = []
        # Iterate for 1000 times
        for times in range(1000):
            initialize()
            randommove_ai.start_ai()
            wallfollow_ai.start_ai()
            rm_steps=0
            wf_steps=0
            while True:
                if current_place1 == destination and current_place2 == destination:
                    rm_steps_list.append(rm_steps)
                    wf_steps_list.append(wf_steps)
                    break
                if rm_steps>1500 or wf_steps>1500:
                    rm_steps_list.append(rm_steps)
                    wf_steps_list.append(wf_steps)
                    break
                if current_place1 != destination:
                    randommove_ai.move()
                    rm_steps+=1
                if current_place2 != destination:
                    wallfollow_ai.move()
                    wf_steps+=1
                for animal in range(len(animal_list)):
                    # Use function 0.01+level*0.005 to act as the probability for each animal to move per millisecond
                    if random.random() < 0.01 + level * 0.005:
                        # 50% percent to move vertical
                        if random.random() < 0.5:
                            move = random.sample([-1, 1], 1)
                            if config[animal_list[animal][0] + move[0]][animal_list[animal][1]] == 1:
                                config[animal_list[animal][0]][animal_list[animal][1]] = 1
                                # Reset the place of the animal
                                animal_list[animal] = [animal_list[animal][0] + move[0], animal_list[animal][1]]
                                config[animal_list[animal][0]][animal_list[animal][1]] = 3
                        # 50% percent to move horizontal
                        else:
                            move = random.sample([-1, 1], 1)
                            if config[animal_list[animal][0]][animal_list[animal][1] + move[0]] == 1:
                                config[animal_list[animal][0]][animal_list[animal][1]] = 1
                                animal_list[animal] = [animal_list[animal][0], animal_list[animal][1] + move[0]]
                                config[animal_list[animal][0]][animal_list[animal][1]] = 3
        rm_steps_levels.append(mean(rm_steps_list))
        wf_steps_levels.append(mean(wf_steps_list))
        print("Level",l,"analysis finished")


    # Draw the plots
    plt.plot(rm_steps_levels,label="RandomWalk")
    plt.plot(wf_steps_levels,label="WallFollow")
    plt.xlabel("Levels")
    plt.ylabel("Average steps taken to pass the level")
    plt.legend()
    plt.title("Average steps taken to pass each level for the two algorithms")
    plt.show()





# Define the function for intelligent agent player to check the surrondings.
def look_around(x, y,config_copy,pre_loc,mode="random"):
    door_pos=[]
    for x_c in range(np.max([0,x-3]),np.min([x+4,n])):
        for y_c in range(np.max([0,y-3]),np.min([y+4,n])):
            if [x_c,y_c] not in [[x-3,y-3],[x-3,y+4],[x+4,y-3],[x+4,y+4]]:
                if config[x_c][y_c]==2:
                    door_pos=[x_c,y_c]

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

    if mode=="wallfollow":
        if pre_loc[-1]==[]:
            return potentiallist[0]

        notexplored=[]
        for i in potentiallist:
            if config_copy[i[0]][i[1]]==1 and config[i[0]][i[1]]==1:
                notexplored.append(i)

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

        direction_seq=[[x,y-1],[x-1,y],[x,y+1],[x+1,y]]
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



class RandomMove():
    # Initialize the room and parameters
    def __init__(self,mode="random"):
        self.config_copy =[]
        self.mode=mode
        self.pre_loc=[[]]*30

    def start_ai(self):
        self.config_copy = []
        self.pre_loc = [[]] * 30
        for x in range(n):
            line_x=[]
            for y in range(n):
                if current_place1==[x,y]:
                    line_x.append(4)
                else:
                    line_x.append(1)
            self.config_copy.append(line_x)

    # Decide the next step of the agent
    def move(self):
        global config, current_place1
        next_choice = look_around(current_place1[0], current_place1[1],self.config_copy,self.pre_loc,mode=self.mode)
        self.pre_loc=self.pre_loc[1:]
        self.pre_loc.append(current_place1)
        current_place1=next_choice
        self.config_copy[next_choice[0]][next_choice[1]]=4


class WallFollow():
    def __init__(self):
        self.config_copy =[]
        self.pre_loc=[[]]*30
        self.mode=0

    def start_ai(self):
        self.mode=0
        self.config_copy = []
        self.pre_loc=[[]]*30
        for x in range(n):
            line_x=[]
            for y in range(n):
                if current_place2==[x,y]:
                    line_x.append(4)
                else:
                    line_x.append(1)
            self.config_copy.append(line_x)

    def move(self):
        global config, current_place2
        if self.mode==0:
            if config[current_place2[0]-1][current_place2[1]]==1:
                next_choice=[current_place2[0]-1,current_place2[1]]
            else:
                self.mode=1
        if self.mode==1:
            next_choice = look_around(current_place2[0], current_place2[1], self.config_copy, self.pre_loc, mode="wallfollow")
        self.pre_loc = self.pre_loc[1:]
        self.pre_loc.append(current_place2)
        current_place2 = next_choice
        self.config_copy[next_choice[0]][next_choice[1]] = 4


# Run the simulation
randommove_ai=RandomMove()
wallfollow_ai=WallFollow()

simulate()

