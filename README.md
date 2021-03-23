# Tutorial to Replicate The Result and Play the Game

#### All the code can be run on Mac. Not sure whether it's adaptable on Windows.
You need to clone the repo to local and run the following commands for different tasks.

## For Creature Generation
### Data Preprocessing
1. use `./setup.sh` to install the necessary package;
2. download the dataset of images of animals, which can be found through link https://www.kaggle.com/alessiocorrado99/animals10;
3. run `python3 seg.py 1 1` to do the data preprocessing.

### DCGAN Training
1. have the preprocessed images, you can also access it by: https://drive.google.com/file/d/19jHdSa-W4SCvqRWt5i1DKWAAbJfjh2Go/view?usp=sharing;
2. open DCGAN_CP_v2.ipynb with google colab;
3. upload the datasets;
4. run the code blocks one by one.

## For Gameplay
### Play the Game
1. install required package like pygame. You can use command `pip install -r requirements.txt`;
2. run `python3 Playgame.py` to start playing the game;
3. run `python3 Playgame.py 1` to enter supervisor's mode where you can see the whole map and the trace of AIs. 

### Analyze the efficiency of different Game AIs
1. run `python3 Gamecopy_AISimulation.py`.
