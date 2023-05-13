import pickle
from itertools import groupby

from fastapi import FastAPI
from typing import Optional, Union
from GraphObject import *
import datetime
from utils import get_short_id, search_enemy_plane, calculate_dis
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
app = FastAPI()

ins_list_map = [[],[]]
enemy_planes = []
self_planes = []
aircraft_carriers = []
graph = Graph(None,None,None)

# def print_list(a):
#     for i in a:
#         print(i)

# ins_type_dict = {0:"攻击（发射后）",1:"攻击（发射前）",2:"探测（目标）",3:"探测（区域）"}
# ins_source_dict = {0:"上级指挥系统",1:"小编队长机飞行员",2:"子编队长机飞行员",3:"起飞前任务规划"}
# target_type_dict = {0:"战斗机",1:"预警机",2:"电子战飞机",3:"运输机"}

@app.get("/sortNow")
async def sortNow():
    sort_final_all = []
    for ins_list in ins_list_map:
        sort_final = []
        #首先要区分开攻击 探测
        after_attack = [i for i in ins_list if i.ins_type==0]
        before_attack = [i for i in ins_list if i.ins_type==1]
        tance = [i for i in ins_list if i.ins_type==2 or i.ins_type==3]
        #然后根据指令来源排序
        after_attack_sort_res = after_attack #忽略，先不排序
        for source, group in groupby(sorted(after_attack, key=lambda ins: ins.source), key=lambda ins: ins.source):
            print()
            # print(list(group))

        before_attack_sort_res = []
        for source, group in groupby(sorted(before_attack, key=lambda ins: ins.source), key=lambda ins: ins.source):
            #攻击前
            before_attack_sort_list = []
            for ins_list_source in list(group):
                target_id = ins_list_source.target_id
                # print(target_id)
                enemy_plane = search_enemy_plane(enemy_planes,target_id)  #获取指令要攻击谁
                in_attack = False
                depth = None
                # out_dis = None
                min_dis = float("inf")
                for self_plane in self_planes:
                    dis = calculate_dis(enemy_plane.x,self_plane.x,enemy_plane.y,self_plane.y)
                    if dis<enemy_plane.attack_radius:
                        in_attack = True
                        depth = enemy_plane.attack_radius - dis
                    else:
                        if dis < min_dis:
                            min_dis = dis
                #目前如果不在攻击区内，假设为离我方飞机越近，越优先
                if in_attack:
                    before_attack_sort_list.append(BeforeAttackSort(ins_list_source,in_attack,depth,None))
                else:
                    before_attack_sort_list.append(BeforeAttackSort(ins_list_source,in_attack,None,min_dis))
                # print(before_attack_sort_list)
             #然后根据攻击区、深度、距离排序

            sorted_res = sorted(before_attack_sort_list, key=lambda a : (not a.in_attack,(- a.depth) if a.depth is not None else None,a.dis))
            before_attack_sort_res.extend(sorted_res)
        print("攻击前指令排序：")
        print(before_attack_sort_res)

        detect_sort_res = []

        #因为目标和区域也有排序标准，只是暂时不考虑而已，因此都放在一起然后排序
        for source, group in groupby(sorted(tance, key=lambda ins: ins.source), key=lambda ins: ins.source):
            detect_sort_list= []
            for ins_list_source in list(group):
                target_id = ins_list_source.target_id
                # print(target_id)
                if ins_list_source.ins_type ==2 : #探测目标
                    enemy_plane = search_enemy_plane(enemy_planes,target_id)  #获取指令要探测谁
                    target_type = enemy_plane.target_type
                    min_dis = float("inf")
                    for self_plane in self_planes:
                        dis = calculate_dis(enemy_plane.x, self_plane.x, enemy_plane.y, self_plane.y)
                        if dis < min_dis:
                            min_dis = dis
                    detect_sort_list.append(DetectSort(ins_list_source,target_type,min_dis))
                if ins_list_source.ins_type ==3 :  #探测区域
                    #暂时不处理，只根据时间排序，简化
                    detect_sort_list.append(DetectSort(ins_list_source,None,None))

                # print(detect_sort_list)
            #先排序目标和区域，然后排序距离，然后排序敌机参数
            sorted_res = sorted(detect_sort_list, key=lambda a : (a.ins.ins_type,a.dis,a.target_type,a.ins.timestamp))
            detect_sort_res.extend(sorted_res)
        print("探测指令排序：")
        print(detect_sort_res)
        sort_final.extend(after_attack_sort_res)
        sort_final.extend(before_attack_sort_res)
        sort_final.extend(detect_sort_res)
        sort_final_all.append(sort_final)
    print(sort_final_all)
    return sort_final_all
        # print(list(group))
        # sort1 = sorted(ins_list,key=lambda ins: ins.ins_type)

@app.get("/saveObject")
async def saveObject():
    # for i in ins_list_map:
    #     for j in i:
    #         j.target_id = int(j.target_id)
    with open('datasave.pk', 'wb') as f:
        pickle.dump((ins_list_map, enemy_planes,self_planes,aircraft_carriers), f)

@app.get("/loadObject")
async def loadObject():
    with open('datasave.pk', 'rb') as f:
        global ins_list_map, enemy_planes, self_planes, aircraft_carriers
        ins_list_map, enemy_planes,self_planes,aircraft_carriers = pickle.load(f)

@app.get("/updateGrqph")
async def updateGraph():
    graph.enemy_planes = enemy_planes
    graph.self_planes = self_planes
    graph.aircraft_carriers = aircraft_carriers

@app.get("/drawGrqph")
async def drawGraph():
    fig, ax = plt.subplots()
    plt.xlim([-100, 200])
    plt.ylim([-100, 200])
    for item in graph.self_planes:
        ax.scatter(item.x, item.y, color='b')
        circle = Circle((item.x, item.y), item.max_attack_distance, color='g',alpha = 0.2)
        ax.add_artist(circle)
    for item in graph.enemy_planes:
        ax.scatter(item.x, item.y, color='r')
        circle = Circle((item.x, item.y), item.attack_radius, color='c',alpha = 0.2)
        ax.add_artist(circle)

    for item in graph.aircraft_carriers:
        ax.scatter(item.x, item.y, color='y')
        circle = Circle((item.x, item.y), item.defense_radius, color='y',alpha = 0.2)
        ax.add_artist(circle)

    # 设置图形标题和坐标轴标签
    ax.set_title('2D Coordinate Points with Colors and Circles')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')

    # 显示图形
    plt.show()


@app.get("/showInstruction")
async def showInstruction():
    # print("战机1")
    for i in range(len(ins_list_map)):
        print("战机{}指令集合******************".format(str(i+1)))
        for item in ins_list_map[i]: #我方战机指令集合
            print(item)
    # print(ins_list)
@app.get("/addInstruction")
async def addInstruction(ins_type: int, source: int, target_id: int, which_plane : int , timestamp: Union[datetime.datetime,None] = None):
    uuid_ge = get_short_id()
    if timestamp is None:
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp = dt
    instruction = Instruction(uuid_ge,ins_type,target_id,source,timestamp)

    ins_list_map[which_plane].append(instruction)

@app.get("/removeInstruction")
async def removeInstruction(uuid_remove : str,which_plane :int):
    for item in ins_list_map[which_plane]:
        if item.uuid == uuid_remove:
            ins_list_map[which_plane].remove(item)


@app.post("/enemy_planes/")
async def create_enemy_plane(enemy_plane: EnemyPlane):
    enemy_planes.append(enemy_plane)
    return {"message": "Enemy plane created successfully"}

@app.get("/enemy_planes/")
async def read_enemy_planes():
    return enemy_planes

@app.get("/enemy_planes/{enemy_plane_id}")
async def read_enemy_plane(enemy_plane_id: int):
    for enemy_plane in enemy_planes:
        if enemy_plane_id == enemy_plane.target_id:
            return enemy_plane
    return {"message": "Enemy plane not found"}

@app.put("/enemy_planes/{enemy_plane_id}")
async def update_enemy_plane(enemy_plane_id: int, enemy_plane: EnemyPlane):
    for i, existing_enemy_plane in enumerate(enemy_planes):
        if enemy_plane_id == existing_enemy_plane.target_id:
            enemy_planes[i] = enemy_plane
            return {"message": "Enemy plane updated successfully"}
    return {"message": "Enemy plane not found"}

@app.delete("/enemy_planes/{enemy_plane_id}")
async def delete_enemy_plane(enemy_plane_id: int):
    for i, enemy_plane in enumerate(enemy_planes):
        if enemy_plane_id == enemy_plane.target_id:
            enemy_planes.pop(i)
            return {"message": "Enemy plane deleted successfully"}
    return {"message": "Enemy plane not found"}

@app.post("/self_planes/")
async def create_self_plane(self_plane: SelfPlane):
    self_planes.append(self_plane)
    return {"message": "Self plane created successfully"}

@app.get("/self_planes/")
async def read_self_planes():
    return self_planes

@app.get("/self_planes/{self_plane_id}")
async def read_self_plane(self_plane_id: int):
    for self_plane in self_planes:
        if self_plane_id == self_plane.plane_id:
            return self_plane
    return {"message": "Self plane not found"}

@app.put("/self_planes/{self_plane_id}")
async def update_self_plane(self_plane_id: int, self_plane: SelfPlane):
    for i, existing_self_plane in enumerate(self_planes):
        if self_plane_id == existing_self_plane.plane_id:
            self_planes[i] = self_plane
            return {"message": "Self plane updated successfully"}
    return {"message": "Self plane not found"}

@app.delete("/self_planes/{self_plane_id}")
async def delete_self_plane(self_plane_id: int):
    for i, self_plane in enumerate(self_planes):
        if self_plane_id == self_plane.plane_id:
            self_planes.pop(i)
            return {"message": "Self plane deleted successfully"}
    return {"message": "Self plane not found"}


@app.post("/aircraft_carriers/")
async def create_aircraft_carrier(aircraft_carrier: AircraftCarrier):
    aircraft_carriers.append(aircraft_carrier)
    return {"message": "Aircraft carrier created successfully"}

@app.get("/aircraft_carriers/")
async def read_aircraft_carriers():
    return aircraft_carriers

@app.get("/aircraft_carriers/{aircraft_carrier_id}")
async def read_aircraft_carrier(aircraft_carrier_id: int):
    for aircraft_carrier in aircraft_carriers:
        if aircraft_carrier_id == aircraft_carrier.aircraft_carrier_id:
            return aircraft_carrier
    return {"message": "Aircraft carrier not found"}

@app.put("/aircraft_carriers/{aircraft_carrier_id}")
async def update_aircraft_carrier(aircraft_carrier_id: int, aircraft_carrier: AircraftCarrier):
    # print(aircraft_carrier_id)
    for i, existing_aircraft_carrier in enumerate(aircraft_carriers):
        # print(existing_aircraft_carrier)
        if aircraft_carrier_id == existing_aircraft_carrier.aircraft_carrier_id:
            aircraft_carriers[i] = aircraft_carrier
            return {"message": "Aircraft carrier updated successfully"}
    return {"message": "Aircraft carrier not found"}

@app.delete("/aircraft_carriers/{aircraft_carrier_id}")
async def delete_aircraft_carrier(aircraft_carrier_id: int):
    for i, aircraft_carrier in enumerate(aircraft_carriers):
        if aircraft_carrier_id == aircraft_carrier.aircraft_carrier_id:
            aircraft_carriers.pop(i)
            return {"message": "Aircraft carrier deleted successfully"}
    return {"message": "Aircraft carrier not found"}


