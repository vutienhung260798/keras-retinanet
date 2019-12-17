#Đầu vào là 1 list các bounding box (x, y, w, h)
#Lưu trữ các bounding box theo tọa độ y cộng với tọa độ tương đối theo x lớn nhất

import json
def check_box(box1, box2, threshold = 0.75):
    if len(box1) ==0 or len(box2) ==0:
        return 0
    if box2[0] > (box1[0] + box1[2])/2 or box2[1] > (box1[1] + box1[3])/2:
        return 0
    w = box1[2] - box2[0]
    h = box1[3] - box2[1]
    area = w*h
    if area/((box1[2] - box1[0])*(box1[3] - box1[1])) < threshold:
        return 0 #2 box không trùng nhau
    else:
        return 1 #2 box trùng nhau

def check_list(list1, list2):
    if len(list1) == 0 or len(list2) == 0:
        return
    for box1 in list1:
        for box2 in list2:
            if check_box(box1, box2): #Nếu trùng thì xóa bb trùng ở list 1 đi.
                list1.remove(box1)
                break

# def check_internal_list(list_bb, threshold = 0.85):
#     over_lap_list = []
#     temp_list = []
#     for i in range(len(list_bb)):
#         for j in range(i+1, len(list_bb)):
#             if check_box(list_bb[i], list_bb[j], 0.85):
#                 over_lap_list.append(i)
#                 break
#     for i in range(len(over_lap_list)):
#         temp_list.append(list_bb[over_lap_list[i]])
#     list_bb = temp_list

#Hàm loại bỏ các boundingbox trùng lặp, đầu vào là file json chứa bounding box
def check_json(file_in, file_out = "./process_bb"):
    file = open(file_in, "r")
    boundingbox = file.read()
    boundingbox = json.loads(boundingbox)
    file.close()
    max_i = 0
    max_j = 0
    for key in boundingbox.keys():
        temp1, temp2 = key.split(".")
        if max_i < int(temp1):
            max_i = int(temp1)
        if max_j < int(temp2):
            max_j = int(temp2)
    for i in range(max_i):
        for j in range(max_j):
            if i <= max_i - 2 and j<= max_j -2:
                check_list(boundingbox[str(i) + "." + str(j)], boundingbox[str(i+1) + "." + str(j)])
                check_list(boundingbox[str(i) + "." + str(j)], boundingbox[str(i) + "." + str(j+1)])
            if i == max_i -1 and j <= max_j -2:
                check_list(boundingbox[str(i) + "." + str(j)], boundingbox[str(i) + "." + str(j+1)])
            if i <= max_i -1 and j == max_j -1:
                check_list(boundingbox[str(i) + "." + str(j)], boundingbox[str(i+1) + "." + str(j)])
    with open(file_out, 'w') as outfile:
        json.dump(boundingbox, outfile)
# check_json("./list_bb.json", "./process_bb")

#Hàm sắp xếp các bounding box

def sort_bounding_box(list_bb, dimension): #Tham số dimension chỉ định sắp xếp theo chiều x hay chiều y, chiều x là 0 chiều y là 1
    if (len(list_bb) == 0):
        return []
    else:
        pivot = list_bb[0]
        lesser = sort_bounding_box([bb for bb in list_bb[1:] if bb[dimension] < pivot[dimension]], dimension)
        greater = sort_bounding_box([bb for bb in list_bb[1:] if bb[dimension] >= pivot[dimension]], dimension)
        return lesser + [pivot] + greater

#Vấn đề: Trường hợp phần lớn nhất của list không detect được thì tỷ lệ không còn chính xác.
#Giải pháp: ta tính tỷ số so với độ lớn theo trục x của solar.

def save_json(path_file_json, thresshold = 38):
    file = open(path_file_json, "r")
    boundingbox = file.read()
    boundingbox = json.loads(boundingbox)
    file.close()
    max_i = 0
    max_j = 0
    for key in boundingbox.keys():
        temp1, temp2 = key.split(".")
        if max_i < int(temp1):
            max_i = int(temp1)
        if max_j < int(temp2):
            max_j = int(temp2)
        #Loại bỏ các boundingbox trùng trong cùng 1 list 
        # check_internal_list(boundingbox[key])
    for i in range(max_i):
        for j in range(max_j):
            if i <= max_i - 2 and j<= max_j -2:
                check_list(boundingbox[str(i) + "." + str(j)], boundingbox[str(i+1) + "." + str(j)])
                check_list(boundingbox[str(i) + "." + str(j)], boundingbox[str(i) + "." + str(j+1)])
            if i == max_i -1 and j <= max_j -2:
                check_list(boundingbox[str(i) + "." + str(j)], boundingbox[str(i) + "." + str(j+1)])
            if i <= max_i -1 and j == max_j -1:
                check_list(boundingbox[str(i) + "." + str(j)], boundingbox[str(i+1) + "." + str(j)])
    # file = open(path_file_json, "r")
    # raw_bb = file.read()
    # raw_bb = json.loads(raw_bb)
    raw_bb = boundingbox
    list_bb = []
    for key in raw_bb.keys():
        if len(raw_bb[key]) != 0:
            list_bb.extend(raw_bb[key])
    list_bb = sort_bounding_box(list_bb, 1)
    bb_dict = dict()
    iter = 1
    bb_dict[str(iter)] = [list_bb[0]]
    for i in range(1, len(list_bb)):
        if len(list_bb[i]) == 0:
            continue
        if (abs(bb_dict[str(iter)][0][1] - list_bb[i][1]) <= thresshold):
            bb_dict[str(iter)].append(list_bb[i])
        else:
            iter += 1
            bb_dict[str(iter)] = [list_bb[i]]
    for key in bb_dict.keys():
        bb_dict[key] = sort_bounding_box(bb_dict[key], 0)
        #Chiều rộng tấm đầu tiên trong bounding box 
        width = abs(bb_dict[key][0][0] - bb_dict[key][0][2])
        #Mỗi tấm lưu thêm vị trí tương đối so với đầu đoạn
        for box in bb_dict[key]:
            box.append((box[0] - bb_dict[key][0][0])/width)
        for box in bb_dict[key][0:-1]:
            index = bb_dict[key].index(box)
            if abs(bb_dict[key][index][0] - bb_dict[key][index+1][0]) < 15:
                bb_dict[key].remove(box)
    json.dump(bb_dict, open("./bb_json.json", "w"))
    # return "./bb_json"

save_json("./list_bb.json")