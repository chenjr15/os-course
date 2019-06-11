import json
from typing import List
from dataclasses import dataclass


@dataclass
class DiskRequest:
    sector_no: int
    def __str__(self):
        return f"REQ@{self.sector_no}"



def fcfs(req_list: List[DiskRequest], init_pos: int, direction: int = 1):
    cur_pos = init_pos
    differ = 0
    for r in req_list:
        print(r)
        differ += abs(r.sector_no - cur_pos)
        cur_pos = r.sector_no
    print(f"平均寻道长度 {differ/len(req_list):.2f}")


def sstf(req_list: List[DiskRequest], init_pos: int, direction: int = 1):
    cur_pos = init_pos
    differ = 0
    from collections import deque
    q = deque(req_list)
    while len(q) > 0:
        r = min(q, key=lambda x: abs(x.sector_no - cur_pos))
        print(r)

        differ += abs(r.sector_no - cur_pos)
        cur_pos = r.sector_no
        q.remove(r)
    print("平均寻道长度", differ/len(req_list))


def scan(req_list: List[DiskRequest], init_pos: int, direction: int = 1):
    cur_pos = init_pos
    differ = 0
    from collections import deque
    q = deque(req_list)
    from functools import reduce
    while len(q) > 0:
        if direction > 0:
            t = [i for i in q if cur_pos <= i.sector_no]
        else:
            t = [i for i in q if   cur_pos >= i.sector_no]
        if not t :
            direction = -direction
            continue
        r = min(t, key=lambda x: abs(x.sector_no - cur_pos))
        print(r)

        differ += abs(r.sector_no - cur_pos)
        cur_pos = r.sector_no
        q.remove(r)
    print("平均寻道长度", differ/len(req_list))
def cscan(req_list: List[DiskRequest], init_pos: int, direction: int = 1):
    cur_pos = init_pos
    differ = 0
    from collections import deque
    q = deque(req_list)
    from functools import reduce
    while len(q) > 0:
        
        t = [i for i in q if cur_pos <= i.sector_no]

        if not t :
            # 找不到比当前大的则直接跳到当前最小的磁道去
            r = r = min(q, key=lambda x: x.sector_no)
        else:
            r = min(t, key=lambda x: abs(x.sector_no - cur_pos))
        print(r)

        differ += abs(r.sector_no - cur_pos)
        cur_pos = r.sector_no
        q.remove(r)
    print(f"平均寻道长度 {differ/len(req_list):.1f}")


if __name__ == "__main__":
    n = int(input("total request:"))
    reqs = input("req:").split(maxsplit=n)
    req_list = tuple((DiskRequest(int(i)) for i in reqs))
    # print(req_list)
    init_pos = int(input("init_pos:"))
    print()
    print("fcfs")
    fcfs(req_list, init_pos)
    print("sstf")
    sstf(req_list, init_pos)
    print("scan")
    scan(req_list, init_pos)
    print("cscan")

    cscan(req_list, init_pos)
