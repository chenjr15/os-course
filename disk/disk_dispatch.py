import json
from typing import List
from dataclasses import dataclass
from collections import deque

@dataclass
class DiskRequest:
    sector_no: int

    def __str__(self):
        return f"REQ@{self.sector_no}"



class Dispatch(object):
    def __init__(self, req_list: List[DiskRequest],cur_pos: int, direction: int = 1):
        # 请求序列
        self.req_list = req_list
        # 当前的磁头位置
        self.cur_pos = cur_pos
        # 寻道方向
        self.direction = direction
        # 移动距离累计
        self.differ: int = 0
        # 是否完成标志
        self.finished:bool = False

    def get_cur_req(self)-> DiskRequest:
        ''' 返回当前处理的请求
        '''
        return None
    def do(self):
        print(f"*进入{self.__class__.__name__}调度算法*")
        while not self.finished:
            r = self.get_cur_req()
            if not r :
                continue
            movement =  abs(r.sector_no - self.cur_pos)
            print(r,movement)
            self.differ += movement
            self.cur_pos = r.sector_no
        print(f"平均寻道长度 {self.differ/len(self.req_list):.1f}")
class FCFS(Dispatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.reqs = list(self.req_list)
    
    def get_cur_req(self) ->DiskRequest:
        if not self.reqs :
            self.finished = True
            return None
        return self.reqs.pop(0)

class SSTF(Dispatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.queue = deque(req_list)
    
    def get_cur_req(self) ->DiskRequest:
        
        if not self.queue :
            self.finished = True
            return None
        r = min(self.queue, key=lambda x: abs(x.sector_no - self.cur_pos))
        self.queue.remove(r)
        return r

class SCAN(Dispatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.queue = deque(req_list)
    
    def get_cur_req(self) ->DiskRequest:
        if not self.queue:
            self.finished = True
            return None
        if self.direction > 0:
            t = [i for i in self.queue if self.cur_pos <= i.sector_no]
        else:
            t = [i for i in self.queue if self.cur_pos >= i.sector_no]
        if not t:
            self.direction = -self.direction
            return None
        r = min(t, key=lambda x: abs(x.sector_no - self.cur_pos))
        self.queue.remove(r)
        return r

class CSCAN(Dispatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.queue = deque(req_list)
    
    def get_cur_req(self) ->DiskRequest:
        if not self.queue:
            self.finished = True
            return None
        t = [i for i in self.queue if self.cur_pos <= i.sector_no]
        if not t:
            # 找不到比当前大的则直接跳到当前最小的磁道去
            r = r = min(self.queue, key=lambda x: x.sector_no)
        else:
            r = min(t, key=lambda x: abs(x.sector_no - self.cur_pos))
        self.queue.remove(r)
        return r


if __name__ == "__main__":
    n = int(input("total request:"))
    reqs = input("req:").split(maxsplit=n)
    req_list = tuple((DiskRequest(int(i)) for i in reqs))
    # print(req_list)
    init_pos = int(input("init_pos:"))
    print()
    for Dispatch in (FCFS,SSTF,SCAN,CSCAN):
        d = Dispatch(req_list, init_pos)
        print('-'*10)
        d.do()
