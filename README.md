# Tutorial to Replicate The Result

#### All the code can be run on Mac. Not sure whether it's adaptability on Windows.

## For Creature Generation
### Data Preprocessing
1. use `./setup.sh` to install the necessary package
2. download the dataset of images of animals, which can be found through link https://www.kaggle.com/alessiocorrado99/animals10
3. run `python3 seg.py 1 1` to do the data preprocessing

### DCGAN Training
1. have the preprocessed images, you can also access it by: https://drive.google.com/file/d/19jHdSa-W4SCvqRWt5i1DKWAAbJfjh2Go/view?usp=sharing
2. open DCGAN_CP_v2.ipynb with google colab
3. upload the datasets
4. run the code blocks one by one

## For Gameplay
1. install required package like pygame
2. run `python3 Game.py` to start the game
3. run `python3 Game.py MAPNAME COVERSTATE AINAME` to run different modes
   1. MAPNAME: myway - room overlay algorithm; dungeon - dungeon algorithm
   2. COVERSTATE: on - you can see the shadow; off - you cannot see the shadow
   3. AINAME: rw - Random Walk Algorithm; wf - WallFollow Algorithm

