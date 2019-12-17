#Đầu vào là 1 list các bounding box (x, y, w, h)
#Lưu trữ các bounding box theo tọa độ y cộng với tọa độ tương đối theo x lớn nhất

#Hàm sắp xếp các bound box
import json
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

def save_json(path_file_json, thresshold):
    file = open(path_file_json, "r")
    raw_bb = file.read()
    raw_bb = json.loads(raw_bb)
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
    json.dump(bb_dict, open("./bb.json", "w"))
    # return "./bb_json"

save_json("./process_bb.json", 40)