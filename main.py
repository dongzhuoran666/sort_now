import pickle
from itertools import groupby

import fastapi
from fastapi import FastAPI
from typing import Optional, Union
from GraphObject import *
import datetime
from utils import get_short_id, search_enemy_plane, calculate_dis,search_area,search_zhang_plane
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
app = FastAPI(default_response_class=fastapi.responses.ORJSONResponse)

ins_list_map = []
enemy_planes = []
self_planes = []
aircraft_carriers = []
areas = []
graph = Graph(None,None,None,None)

# def print_list(a):
#     for i in a:
#         print(i)

# ins_type_dict = {0:"攻击（发射后）",1:"攻击（发射前）",2:"探测（目标）",3:"探测（区域）"}
# ins_source_dict = {0:"上级指挥系统",1:"起飞前任务规划",2:"小编队长机飞行员",3:"编队自主识别"}
# target_type_dict = {0:"战斗机",1:"预警机",2:"电子战飞机",3:"运输机"}

@app.get("/sortNow")
async def sortNow():
    sort_final_all = []
    #首先按照来源进行排序
    all_ins_sort_res = []
    for source,group in groupby(sorted(ins_list_map, key=lambda ins: ins.source), key=lambda x: x.source):
        source_ins = list(group)
        before_attack_order = None
        ins_type3_res = []
        ins_type2_res = []
        ins_type1_res = []
        ins_type0_res = []

        for ins_type,type_group in groupby(sorted(source_ins, key=lambda ins: -ins.ins_type), key=lambda x: x.ins_type):
            # print(list(type_group))
            #倒过来排序为了照顾发射后需要依照发射前的顺序
            sort_list = list(type_group)
            # print(ins_type)
            if ins_type == 3:
                print(ins_type)
                zhang_plane = search_zhang_plane(self_planes) #寻找长机
                for i in sort_list:
                    target_area = search_area(areas,i.target)
                    area_x = target_area.x + 0.5*target_area.width
                    area_y = target_area.y + 0.5*target_area.height
                    # print(zhang_plane)
                    dis = calculate_dis(zhang_plane.x,area_x,zhang_plane.y,area_y) #计算与每个区域中心的距离
                    i.area_dis = dis
                sorted_res = sorted(sort_list,
                                    key=lambda a: (a.area_dis,a.timestamp))
                ins_type3_res = sorted_res
            if ins_type == 2:
                print(ins_type)
                for i in sort_list:
                    target_id = i.target
                    target_palne = search_enemy_plane(enemy_planes,target_id)
                    min_dis = float('inf')
                    for j in self_planes:
                        dis = calculate_dis(j.x,target_palne.x,j.y,target_palne.y)
                        if dis < min_dis:
                            min_dis = dis
                    i.min_dis = min_dis
                    i.target_speed = target_palne.spreed
                sorted_res = sorted(sort_list,
                                    key=lambda a: (a.min_dis,-a.target_speed))
                ins_type2_res = sorted_res
            if ins_type == 1:
                print(ins_type)
                for i in sort_list:
                    target_id = i.target
                    target_plane = search_enemy_plane(enemy_planes,target_id)
                    min_depth = float('inf')
                    i.in_attack = False
                    min_attack_time = float('inf')
                    for j in self_planes:
                        dis = calculate_dis(j.x,target_plane.x,j.y,target_plane.y)
                        if dis < target_plane.attack_radius:
                            i.in_attack = True
                            if target_plane.attack_radius-dis< min_depth:
                                min_depth = target_plane.attack_radius-dis
                    if not i.in_attack:
                        for j in self_planes:
                            dis = calculate_dis(j.x, target_plane.x, j.y, target_plane.y)
                            attack_time = (dis - j.max_attack_distance)/target_plane.spreed
                            if attack_time<min_attack_time:
                                min_attack_time = attack_time
                    i.min_attack_time = min_attack_time
                    i.min_depth = min_depth
                sorted_res = sorted(sort_list,
                                    key=lambda a: (not a.in_attack,-a.min_depth,a.min_attack_time))
                ins_type1_res = sorted_res
                before_attack_order = [k.target for k in ins_type1_res]
            if ins_type == 0:
                print(ins_type)
                for i in sort_list:
                    print("adasda")
                    target_index = before_attack_order.index(i.target)  #假定攻击后的目标一定出现在攻击前里面
                    i.target_index = target_index
                sorted_res = sorted(sort_list,
                                    key=lambda a: a.target_index)
                ins_type0_res = sorted_res

        all_ins_sort_res.extend(ins_type0_res)
        all_ins_sort_res.extend(ins_type1_res)
        all_ins_sort_res.extend(ins_type2_res)
        all_ins_sort_res.extend(ins_type3_res)

    print(all_ins_sort_res)
                    # print(area_x,area_y)
                    # print(dis)



    with open('res.txt', 'w') as f:
        # 写入每行文本

        for j in all_ins_sort_res:
            f.write(str(j.__repr__()) + '\n')
    return all_ins_sort_res
        # print(list(group))
        # sort1 = sorted(ins_list,key=lambda ins: ins.ins_type)

@app.get("/saveObject")
async def saveObject():
    # for i in ins_list_map:
    #     for j in i:
    #         j.target_id = int(j.target_id)
    with open('datasave.pk', 'wb') as f:
        # global   ins_list_map
        # ins_list_map=[]
        pickle.dump((ins_list_map, enemy_planes,self_planes,aircraft_carriers,areas), f)

@app.get("/loadObject")
async def loadObject():
    with open('datasave.pk', 'rb') as f:
        global ins_list_map, enemy_planes, self_planes, aircraft_carriers, areas
        ins_list_map, enemy_planes,self_planes,aircraft_carriers,areas = pickle.load(f)

@app.get("/updateGraph")
async def updateGraph():
    graph.enemy_planes = enemy_planes
    graph.self_planes = self_planes
    graph.aircraft_carriers = aircraft_carriers
    graph.areas = areas

@app.get("/drawGraph")
async def drawGraph():
    fig, ax = plt.subplots()
    plt.xlim([-50, 300])
    plt.ylim([-100, 300])
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

    for item in graph.areas:
        rect = Rectangle((item.x, item.y), item.width, item.height, linewidth=1, edgecolor = 'r', facecolor = 'none')
        ax.add_artist(rect)


        # 设置图形标题和坐标轴标签
    ax.set_title('2D Coordinate Points with Colors and Circles')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')

    # 显示图形
    plt.show()


@app.get("/showInstruction")
async def showInstruction():
    print("战机指令集合******************")
    for item in ins_list_map: #我方战机指令集合
        print(item)
    # print(ins_list)
@app.get("/addInstruction")
async def addInstruction(ins_type: int, source: int, target_id: int, timestamp: Union[datetime.datetime,None] = None):
    uuid_ge = get_short_id()
    if timestamp is None:
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp = dt
    instruction = Instruction(uuid_ge,ins_type,target_id,source,timestamp)

    ins_list_map.append(instruction)

@app.get("/removeInstruction")
async def removeInstruction(uuid_remove : str):
    for item in ins_list_map:
        if item.uuid == uuid_remove:
            ins_list_map.remove(item)


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

@app.get("/areas")
async def get_areas():
    return areas

@app.post("/areas")
async def create_area(area: Area):
    areas.append(area)
    return area

@app.put("/areas/{area_id}")
async def update_area(area_id: int, area: Area):
    for i, a in enumerate(areas):
        if a.area_id == area_id:
            areas[i] = area
            return area
    return {"error": "Area not found"}

@app.delete("/areas/{area_id}")
async def delete_area(area_id: int):
    for i, a in enumerate(areas):
        if a.area_id == area_id:
            del areas[i]
            return {"message": "Area deleted successfully"}
    return {"error": "Area not found"}
