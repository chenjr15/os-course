try:
    from process import Process
except ImportError:
    import sys
    sys.path.append('..')
    from process import Process


class JobState:
    max_num = 100

    def __init__(self, pid, need_time, arrive_time, pname=""):
        '''任务状态, 包含每个进程的pcb和到达时间,开始时间,结束时间等信息
        '''
        self.pcb = Process(pid, need_time, pname)
        # 到达时间
        self.arrive_time = arrive_time
        # 开始时间
        self.start_time = 0
        # 结束时间
        self.finish_time = 0

    def reset(self):
        self.pcb.reset()
        # 开始时间
        self.start_time = 0
        # 结束时间
        self.finish_time = 0

    @property
    def whole_time(self):
        '''周转时间: 完成时间-到达时间
        '''
        return self.finish_time - self.arrive_time

    @property
    def weight_time(self):
        '''
        带权周转时间: 周转时间/服务时间
        '''
        return self.whole_time/self.pcb.runtime

    def __repr__(self):
        return f"{repr(self.pcb)}"

    def __str__(self):
        return f"{self.pcb.pname} 完成时间:{self.finish_time}, 周转时间:{self.whole_time} ,带权周转:{self.weight_time}"


def average(iters, key=lambda x: x):
    from functools import reduce
    return reduce(lambda x, y: x+y, [key(i) for i in iters])/len(iters)


def fcfs(jobs: list):
    '''模拟FCFS调度算法调度程序
    '''
    current_time = 0
    # 按照到到达时间模拟执行进程并记录时间
    for job in jobs:
        job.start_time = current_time
        print("Time :", current_time)
        job.pcb.run(echo=True)
        current_time += job.pcb.need_time
        job.finish_time = current_time
    # 输出每个进程的完成时间, 周转时间 ,带权周转时间
    for j in jobs:
        print(j)
    # 计算平均周转时间和平均带权周转时间
    print("平均周转时间: ", average(jobs, lambda j: j.whole_time))
    print("平均带权周转时间: ", average(jobs, lambda j: j.weight_time))

    print("!! FCFS FINISHED !!")


def sjf(jobs: list):
    '''模拟SJF调度算法
    '''
    print("!! SJF START !!")
    current_time = 0
    # 取得当前到达并且为完成的进程
    avaivble = list(filter(
        lambda job: (job.arrive_time <=
                     current_time) and not job.pcb.is_finish(), jobs))
    # 将进程按服务时间排序
    avaivble.sort(key=lambda job: job.pcb.need_time)

    while avaivble:
        print("Time :", current_time)
        # 选择服务时间最短的执行
        job = avaivble[0]
        job.start_time = current_time
        job.pcb.run(echo=True)
        current_time += job.pcb.need_time
        job.finish_time = current_time

        avaivble = list(filter(lambda job: (job.arrive_time <=
                                            current_time)and not job.pcb.is_finish(), jobs))
        avaivble.sort(key=lambda job: job.pcb.need_time)
   # 输出每个进程的完成时间, 周转时间 ,带权周转时间
    for j in jobs:
        print(j)
    # 计算平均周转时间和平均带权周转时间
    print("平均周转时间: ", average(jobs, lambda j: j.whole_time))
    print("平均带权周转时间: ", average(jobs, lambda j: j.weight_time))
    print("!! SJF FINISHED !!")


if __name__ == "__main__":
    jobs_josn = []
    with open("jobs.json") as f:
        import json
        jobs_josn = json.load(f)
    jobs = [JobState(**p) for p in jobs_josn]
    # 确保按到达时间排序
    jobs.sort(key=lambda job: job.arrive_time)
    print(jobs)
    fcfs(jobs)
    # 重置状态
    [job.reset() for job in jobs]

    sjf(jobs)
