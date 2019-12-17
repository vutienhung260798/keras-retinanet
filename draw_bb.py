import cv2
import json
import numpy as np

img = cv2.imread('/home/hung-vt/Pictures/a.jpg')

with open('./bb.json', 'r') as f_r:
    data = f_r.read()

obj = json.loads(data)

list_id = obj.keys()

list_bb = []

for _id in list_id:
    list_bb.extend(obj[_id])

for bb in list_bb:
    cv2.rectangle(img, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), (0, 255, 0), 1)

cv2.imwrite('/home/hung-vt/Pictures/demo.jpg', img)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 3000,1000)
cv2.imshow('image', img)
cv2.waitKey(0)

print(list_bb[0])

# print(type(obj))