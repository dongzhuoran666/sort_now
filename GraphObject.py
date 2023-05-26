from pydantic import BaseModel, fields


class EnemyPlane(BaseModel):
    target_id: int
    target_type: int  #目前只考虑机型
    x: float
    y: float
    attack_radius: float
    spreed: float #属性名写错了应该是speed

class SelfPlane(BaseModel):
    x: float
    y: float
    max_attack_distance: float
    plane_id: int
    is_zhang: int #1为是长机

class Area(BaseModel):
    area_id: int
    x: float
    y: float
    width: float
    height: float

class AircraftCarrier(BaseModel):
    x: float
    y: float
    defense_radius: float
    aircraft_carrier_id: int
#
# class BeforeAttackSort:
#     def __init__(self,ins,in_attack,depth,dis):
#         self.ins = ins
#         self.in_attack = in_attack #是否在攻击区内，布尔
#         self.depth = depth  #如果是探测区域，表示一个区域
#         self.dis = dis  #理论应该是到达最大攻击距离1.5倍时间越小越优先，用距离代替
#         # self.timestamp = timestamp
#     def __repr__(self):
#         return f"{self.ins}_在攻击区内？{self.in_attack}_深度{self.depth}_距离{self.dis}"


# class DetectSort:
#     def __init__(self,ins,target_type,dis):
#         self.ins = ins
#         self.target_type = target_type #敌机参数
#         self.dis = dis  #敌机距离
#         # self.timestamp = timestamp
#     def __repr__(self):
#         return f"{self.ins}_敌机类型？{self.target_type}_距离{self.dis}"

class Graph:
    def __init__(self, enemy_planes, self_planes, aircraft_carriers, areas):
        self.enemy_planes = enemy_planes
        self.self_planes = self_planes
        self.aircraft_carriers = aircraft_carriers
        self.areas = areas


ins_type_dict = {0:"攻击（发射后）",1:"攻击（发射前）",2:"探测（目标）",3:"探测（区域）"}
ins_source_dict = {0:"上级指挥系统",1:"起飞前任务规划",2:"小编队长机飞行员",3:"编队自主识别"}
target_type_dict = {0:"战斗机",1:"预警机",2:"电子战飞机",3:"运输机"}
class Instruction:
    def __init__(self,uuid, ins_type, target, source, timestamp):
        self.uuid = uuid
        self.ins_type = ins_type
        self.target = target  #如果是探测区域，表示一个区域,也可以另开一个属性来表示区域范围
        self.source = source
        self.timestamp = timestamp
    def __repr__(self):
        if self.ins_type == 0:
            return f"{self.uuid}_{ins_type_dict[self.ins_type]}_{ins_source_dict[self.source]}_作用目标{self.target}_{self.timestamp}_在攻击前指令的排序{self.target_index if hasattr(self,'target_index') else None}"

        if self.ins_type == 1:
            return f"{self.uuid}_{ins_type_dict[self.ins_type]}_{ins_source_dict[self.source]}_作用目标{self.target}_{self.timestamp}_是否在攻击区{self.in_attack if hasattr(self,'in_attack') else None}_深度{self.min_depth if hasattr(self,'min_depth') else None}_到达攻击距离时间{self.min_attack_time if hasattr(self,'min_attack_time') else None}"

        if self.ins_type == 2:
            return f"{self.uuid}_{ins_type_dict[self.ins_type]}_{ins_source_dict[self.source]}_作用目标{self.target}_{self.timestamp}_距编队{self.min_dis if hasattr(self,'min_dis') else None}_目标速度{self.target_speed if hasattr(self,'target_speed') else None}"

        if self.ins_type == 3:
            return f"{self.uuid}_{ins_type_dict[self.ins_type]}_{ins_source_dict[self.source]}_作用目标{self.target}_{self.timestamp}_距长机{self.area_dis if hasattr(self,'area_dis') else None}"

        return f"{self.uuid}_{ins_type_dict[self.ins_type]}_{ins_source_dict[self.source]}_作用目标{self.target}_{self.timestamp}"
