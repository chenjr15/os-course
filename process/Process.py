from time import sleep
from enum import Enum


class State(Enum):
    UNINIT = 0
    RUNINIG = 1
    PAUSE = 2
    READY = 3
    FINISH = 4


class Process(object):
    '''进程类, 大概是一个pcb
    '''

    def __init__(self, pid, need_time, pname=""):
        self.pid = pid
        self.pname = pname
        # 完成进程所需时间
        self.need_time = need_time
        # 已经执行了的时间
        self.runtime = 0
        # 进程状态
        self.state = State.READY

    def run(self, time=0, skip=False, echo=False):
        '''模拟进程执行, 取需要时间和给定时间最小的

        :time 给定执行时间, 为0表示执行到进程结束

        :skip 是否跳过模拟执行
        '''
        if not time:
            time = self.left_time
        current = min(self.left_time, time)
        self.state = State.RUNINIG
        echo and print(self)
        skip or sleep(0.01*current)
        self.runtime += current
        if self.runtime == self.need_time:
            self.state = State.FINISH
        else:
            self.state = State.PAUSE
        return self.state

    def is_finish(self):
        return self.state == State.FINISH

    def reset(self):
        self.state = State.READY

    @property
    def left_time(self):
        '''完成进程所需的剩余时间
        '''
        return self.need_time-self.runtime

    def __repr__(self):
        return f"<P {self.state}@{self.pid} {self.left_time or ''}>"

    def __str__(self):
        return f"<Process#{self.pid} {self.pname} {self.state} {self.left_time or ''}>"


def test():
    import random
    p = Process(1, 100, 'init')
    while p.state != State.FINISH:
        p.run(random.randint(5, 20))
        print(p)


if __name__ == "__main__":
    test()
