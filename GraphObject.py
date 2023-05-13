from pydantic import BaseModel, fields


class EnemyPlane(BaseModel):
    target_id: int
    target_type: int  #目前只考虑机型
    x: float
    y: float
    attack_radius: float

class SelfPlane(BaseModel):
    x: float
    y: float
    max_attack_distance: float
    plane_id: int

class AircraftCarrier(BaseModel):
    x: float
    y: float
    defense_radius: float
    aircraft_carrier_id: int

class BeforeAttackSort:
    def __init__(self,ins,in_attack,depth,dis):
        self.ins = ins
        self.in_attack = in_attack #是否在攻击区内，布尔
        self.depth = depth  #如果是探测区域，表示一个区域
        self.dis = dis  #理论应该是到达最大攻击距离1.5倍时间越小越优先，用距离代替
        # self.timestamp = timestamp
    def __repr__(self):
        return f"{self.ins}_在攻击区内？{self.in_attack}_深度{self.depth}_距离{self.dis}"


class DetectSort:
    def __init__(self,ins,target_type,dis):
        self.ins = ins
        self.target_type = target_type #敌机参数
        self.dis = dis  #敌机距离
        # self.timestamp = timestamp
    def __repr__(self):
        return f"{self.ins}_敌机类型？{self.target_type}_距离{self.dis}"

class Graph:
    def __init__(self, enemy_planes, self_planes, aircraft_carriers):
        self.enemy_planes = enemy_planes
        self.self_planes = self_planes
        self.aircraft_carriers = aircraft_carriers


ins_type_dict = {0:"攻击（发射后）",1:"攻击（发射前）",2:"探测（目标）",3:"探测（区域）"}
ins_source_dict = {0:"上级指挥系统",1:"小编队长机飞行员",2:"子编队长机飞行员",3:"起飞前任务规划"}
target_type_dict = {0:"战斗机",1:"预警机",2:"电子战飞机",3:"运输机"}
class Instruction:
    def __init__(self,uuid, ins_type, target_id, source, timestamp):
        self.uuid = uuid
        self.ins_type = ins_type
        self.target_id = target_id  #如果是探测区域，表示一个区域,也可以另开一个属性来表示区域范围
        self.source = source
        self.timestamp = timestamp
    def __repr__(self):
        return f"{self.uuid}_{ins_type_dict[self.ins_type]}_{ins_source_dict[self.source]}_作用目标{self.target_id}_{self.timestamp}"
