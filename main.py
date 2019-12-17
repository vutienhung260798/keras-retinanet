import os
import shutil
import zipfile
import urllib
import xml.etree.ElementTree as ET
import numpy as np
import csv
import pandas
# from google.colab import drive
# from google.colab import files

# %matplotlib inline

# # automatically reload modules when they have changed
# %reload_ext autoreload
# %autoreload 2
# # import keras
import keras

# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
import time
# set tf backend to allow memory to grow, instead of claiming everything
import tensorflow as tf
import json
import os
import pickle as pkl
import Save_solar
import shutil

def sliding_window(path_img):
    over_lap_x = 100
    over_lap_y = 80
    list_img = []
    list_solar = []
    window_size = (240, 250)
    img = cv2.imread(path_img)
    # print(np.shape(img))
    x, y,_ = np.shape(img)
    # print(x, y)
    x = x//(window_size[0] - over_lap_x)
    y = y//(window_size[1] - over_lap_y)
    print(x, y)
    image_size_x = (window_size[0] - over_lap_x) * x + over_lap_x
    image_size_y = (window_size[1] - over_lap_y) * y + over_lap_y
    print(image_size_x, image_size_y)
    image_size = (image_size_y, image_size_x)
    image = cv2.resize(img, (image_size))
    # print(np.shape(image))
    for i in range(x):
        for j in range(y):
            if(i != 0 and j != 0):
                split_image = image[(window_size[0]-over_lap_x)*i :(window_size[0]-over_lap_x)*i + window_size[0], (window_size[1]-over_lap_y)*j : (window_size[1]-over_lap_y)*j + window_size[1]]
            if(i == 0 and j != 0):
                split_image = image[0 : window_size[0], (window_size[1]-over_lap_y)*j : (window_size[1]-over_lap_y)*j + window_size[1]]
            if(j == 0 and i != 0):
                split_image = image[(window_size[0]-over_lap_x)*i :(window_size[0]-over_lap_x)*i + window_size[0], 0 : window_size[1]]
            if(i == 0 and j == 0):
                split_image = image[0: window_size[0], 0 : window_size[1]]
            # list_img.append(split_image)
            cv2.imwrite('./anh/' + str(i)+'.'+str(j) + '.jpg', split_image)
    cv2.imwrite('./a.jpg', image)

def img_inference(img_path, pos_window, model, labels_to_names):
    window_size = (240, 250)
    over_lap_x = 100
    over_lap_y = 80
    list_bb = []
    image = read_image_bgr(img_path)

    # copy to draw on
    draw = image.copy()
    draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

    # preprocess image for network
    image = preprocess_image(image)
    image, scale = resize_image(image)
    # print(scale)

    # process image
    start = time.time()
    boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
    print("processing time: ", time.time() - start)
    boxes /= scale
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        box_restore = []
        # scores are sorted so we can break
        if score < 0.8 or labels_to_names[label] != "solar":
            break
        
        box_restore.append(box[0] + pos_window[1] * (window_size[1]- over_lap_y))
        box_restore.append(box[1] + pos_window[0] * (window_size[0]- over_lap_x))
        box_restore.append(box[2] + pos_window[1] * (window_size[1]- over_lap_y))
        box_restore.append(box[3] + pos_window[0] * (window_size[0]- over_lap_x))
        # print(box)
        # print(score)
        # print(labels_to_names[label])
        list_bb.append(box_restore)
        color = label_color(label)

        b = box.astype(int)
        draw_box(draw, b, color=color)

        caption = "{} {:.3f}".format(labels_to_names[label], score)
        draw_caption(draw, b, caption)
    plt.figure(figsize=(10, 10))
    plt.axis('off')
    plt.imshow(draw)
    plt.show()
    # for box in list_bb:
    #     print(box)
    # print(list_bb[0])
    return list_bb

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)

def solar_detection(images_path = ''):
    DATASET_DIR = 'dataset'
    ANNOTATIONS_FILE = 'annotations.csv'
    CLASSES_FILE = 'classes.csv'

    keras.backend.tensorflow_backend.set_session(get_session())
    #load model
    model_path = './resnet50_csv_10.h5'
    print(model_path)
    # load retinanet model
    model = models.load_model(model_path, backbone_name='resnet50')
    model = models.convert_model(model)

    # load label to names mapping for visualization purposes
    labels_to_names = pandas.read_csv(CLASSES_FILE,header=None).T.loc[0].to_dict()
    
    list_dir = os.listdir('./')
    if 'anh' in list_dir:
        shutil.rmtree('anh') 
    sliding_window(images_path)
    os.mkdir('anh')

    path_file = './anh/'
    list_bb = {}
    for img in os.listdir(path_file):
        A = img.split('.')
        pos_window = (int(A[0]), int(A[1]))
        path_img = os.path.join(path_file, img)
        id = A[0] + '.' + A[1]
        print(id)
        bb = img_inference(path_img, pos_window, model, labels_to_names)
        # print(bb)
        list_bb[id] = bb
    with open('./list_bb.json', 'w') as f_w:
        json.dump(list_bb, f_w)
solar_detection(images_path = './keras-retinanet/7fc8992d8a_012288112DOPENPIPELINE_Orthomosaic_export_FriNov22014645.383588.jpg')
Save_solar.save_json('./list_bb.json')

   