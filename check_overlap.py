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

def check_internal_list(list_bb, threshold = 0.85):
    over_lap_list = []
    temp_list = []
    for i in range(len(list_bb)):
        for j in range(i+1, len(list_bb)):
            if check_box(list_bb[i], list_bb[j], 0.85):
                over_lap_list.append(i)
                break
    for i in range(len(over_lap_list)):
        temp_list.append(list_bb[over_lap_list[i]])
    list_bb = temp_list
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
    with open(file_out, 'w') as outfile:
        json.dump(boundingbox, outfile)
    return "./process_bb"
check_json("./list_bb_0.8.json", "./process_bb.json")