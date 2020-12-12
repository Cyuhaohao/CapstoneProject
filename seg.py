#Import the necessary libraries
import keras
import os
import glob
from io import BytesIO
import numpy as np
from PIL import Image
import tensorflow as tf
import sys
import datetime
from resizeimage import resizeimage


class DeepLabModel(object):
  """Class to load deeplab model and run inference."""

  INPUT_TENSOR_NAME = 'ImageTensor:0'
  OUTPUT_TENSOR_NAME = 'SemanticPredictions:0'
  INPUT_SIZE = 513
  FROZEN_GRAPH_NAME = 'frozen_inference_graph'

  def __init__(self, tarball_path):
    """Creates and loads pretrained deeplab model."""
    self.graph = tf.Graph()

    graph_def = None
    graph_def = tf.GraphDef.FromString(open(tarball_path + "/frozen_inference_graph.pb", "rb").read()) 

    if graph_def is None:
      raise RuntimeError('Cannot find inference graph in tar archive.')

    with self.graph.as_default():
      tf.import_graph_def(graph_def, name='')

    self.sess = tf.Session(graph=self.graph)

  def run(self, image):
    """Runs inference on a single image.

    Args:
      image: A PIL.Image object, raw input image.

    Returns:
      resized_image: RGB image resized from original input image.
      seg_map: Segmentation map of `resized_image`.
    """
    start = datetime.datetime.now()

    width, height = image.size
    resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
    target_size = (int(resize_ratio * width), int(resize_ratio * height))
    resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)
    batch_seg_map = self.sess.run(
        self.OUTPUT_TENSOR_NAME,
        feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(resized_image)]})
    seg_map = batch_seg_map[0]

    end = datetime.datetime.now()

    diff = end - start
    print("Time taken to evaluate segmentation is : " + str(diff))

    return resized_image, seg_map


# The function I design to do the preprocessing
def drawSegment(baseImg, matImg):
  # Store image data
  width, height = baseImg.size
  dummyImg = np.zeros([height, width, 4], dtype=np.uint8)
  for x in range(width):
      for y in range(height):
          color = matImg[y,x]
          (r,g,b) = baseImg.getpixel((x,y))
          if color == 0:
              dummyImg[y,x,3] = 0
          else :
              dummyImg[y,x] = [r,g,b,255]

  img = Image.fromarray(dummyImg)
  # Resize the image to 64*64
  img = resizeimage.resize_cover(img, [64, 64])

  # Use a algorthim to only select the largest group of image in a big image
  segs_list = []

  # Store the coordinates of the grids that belong to the same part in the image together in the same list in the seg_list
  for x in range(64):
      for y in range(64):
          if img.getpixel((x,y))[3]!=0:
              find_place=0
              # If the grid in the same column and row-1 is already exist in the seg_list, add it into the list
              if x-1>=0:
                  for i in range(len(segs_list)):
                      if [x-1,y] in segs_list[i]:
                          segs_list[i].append([x,y])
                          find_place=1

              if y-1>=0:
                  for i in range(len(segs_list)):
                      # If the grid in the same row and column-1 is alredy existing in the seg list
                      if [x,y-1] in segs_list[i]:
                          # If the grid in the same column and row-1 not exist in the seg_list
                          if find_place==0:
                              # Add the grid to the group with the the grid in the same row and column-1
                              segs_list[i].append([x,y])
                              find_place=1
                              break
                          # If the grid in the same column and row-1 not exist in the seg_list
                          else:
                              # Join the two lists of coordinates that containing grids connected with the current grid
                              for ori in range(len(segs_list)):
                                  if [x,y] in segs_list[ori]:
                                      if ori!=i:
                                          segs_list[i]=segs_list[ori]+segs_list[i]
                                          segs_list[ori]=[]
                                          break
              # If not existing any neighbor grids, just add it into the list
              if find_place==0:
                  segs_list.append([[x,y]])

  # If there is grids in the list, calculate the length of the sublists in the seg_list
  if len(segs_list)!=0:
      segs_l=[]
      for i in segs_list:
          segs_l.append(len(i))

      # Get the maximum of the lengths of sublists
      chosen_seg=segs_l.index(max(segs_l))
      im = img.load()

      # For the other parts, paint it transparent
      for i in range(len(segs_list)):
          if i!=chosen_seg:
              for grid in segs_list[i]:
                  im[grid[0], grid[1]] = (0,0,0,0)

      # Calculate the percentage of colored areas over total area
      color_percent = max(segs_l) / (64*64)

      # If the percentage is smaller than 0.15 or larger than 0.75, then discard the image
      if color_percent < 0.75 and color_percent > 0.15:
          img.save('Processed_Imgs2/'+outputFilePath)
      else:
          print("Fail because Color percent:",color_percent)
  else:
      print("Fail because Color percent:", 0)


inputFilePath = sys.argv[1]
outputFilePath = sys.argv[2]

if inputFilePath is None or outputFilePath is None:
  print("Bad parameters. Please specify input file path and output file path")
  exit()

modelType = "mobile_net_model"
if len(sys.argv) > 3 and sys.argv[3] == "1":
  modelType = "xception_model"

MODEL = DeepLabModel(modelType)
print('model loaded successfully : ' + modelType)

def run_visualization(filepath):
  """Inferences DeepLab model and visualizes result."""
  try:
  	#print("Trying to open : " + sys.argv[1])
  	# f = open(sys.argv[1])
  	jpeg_str = open(filepath, "rb").read()
  	orignal_im = Image.open(BytesIO(jpeg_str))
  except IOError:
    print('Cannot retrieve image. Please check file: ' + filepath)
    return

  #print('running deeplab on image %s...' % filepath)
  resized_im, seg_map = MODEL.run(orignal_im)

  # vis_segmentation(resized_im, seg_map)
  drawSegment(resized_im, seg_map)

# For the animal images inside the given dataset, iterate the images to do the image segmentation and preprocess
for animal_name in ['cane','cavallo','elefante','farfalla','gallina','gatto','mucca','pecora','ragno','scoiattolo']:
  for file_name in glob.glob('ImageSet/'+animal_name+'/*'):
    outputFilePath=file_name.split('.')[0][9:]+'.png'
    run_visualization(file_name)

