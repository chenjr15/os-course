from Process import Process


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
        return self.whole_time/self.pcb.runtime if self.pcb.runtime != 0 else 0

    def wait_time(self, current_time):
        '''根据current_time 参数计算当前等待了多久
        '''
        if current_time-self.arrive_time > 0:
            return current_time-self.arrive_time
        else:
            return 0

    def __repr__(self):
        return f"{repr(self.pcb)}"

    def __str__(self):
        return f"{self.pcb.pname} 完成时间:{self.finish_time}, 周转时间:{self.whole_time} ,带权周转:{self.weight_time}"


def average(iters, key=lambda x: x):
    from functools import reduce
    return reduce(lambda x, y: x+y, [key(i) for i in iters])/len(iters)


class JobScheduling:
    _name = "JobScheduling"

    def __init__(self, jobs: list, timestamp=0):
        self.jobs = jobs
        self.timestamp = timestamp

    def run(self):
        '''fire all jobs
        '''
        for job in jobs:
            job.start_time = timestamp
            timestamp += job.pcb.run()
            job.finish_time = timestamp

    def launch(self):
        '''launch this scheduling machine
        '''
        print("\n", '-'*10, "\n", self._name, "strarted!")
        self.run()
        # 输出每个进程的完成时间, 周转时间 ,带权周转时间
        for j in self.jobs:
            print(j)
        # 计算平均周转时间和平均带权周转时间
        print("平均周转时间: ", average(jobs, lambda j: j.whole_time))
        print("平均带权周转时间: ", average(jobs, lambda j: j.weight_time))
        print(self._name, "finished!")


class FCFSScheduling(JobScheduling):
    '''FCFS 调度算法的实现
    '''
    _name = "FCFS"

    def run(self):
        # 按照到到达时间模拟执行进程并记录时间
        for job in jobs:
            job.start_time = self.timestamp
            print("Time :", self.timestamp)
            job.pcb.run(echo=True)
            self.timestamp += job.pcb.need_time
            job.finish_time = self.timestamp


class SJFScheduling(JobScheduling):
    '''SJF 调度算法的实现
    '''
    _name = "SJF"

    def run(self):
        # 取得当前到达并且为完成的进程
        avaivble = list(filter(
            lambda job: (job.arrive_time <=
                         self.timestamp) and not job.pcb.is_finish(), jobs))
        # 将进程按服务时间排序
        avaivble.sort(key=lambda job: job.pcb.need_time)

        while avaivble:
            print("Time :", self.timestamp)
            # 选择服务时间最短的执行
            job = avaivble[0]
            job.start_time = self.timestamp
            job.pcb.run(echo=True)
            self.timestamp += job.pcb.need_time
            job.finish_time = self.timestamp

            avaivble = list(filter(lambda job: (job.arrive_time <=
                                                self.timestamp)and not job.pcb.is_finish(), jobs))
            avaivble.sort(key=lambda job: job.pcb.need_time)


class RRScheduling(JobScheduling):
    '''RR 调度算法的实现
    '''
    _name = "RR"

    def __init__(self, jobs: list, timestamp=0, time_slice=2):
        self.jobs = jobs
        self.timestamp = timestamp
        self.time_slice = time_slice

    def run(self):
        import queue
        
        ready_queue = queue.SimpleQueue()
        wait_queue = queue.SimpleQueue()
        for job in jobs:
            if job.arrive_time <= self.timestamp:
                ready_queue.put(job)
            else:
                wait_queue.put(job)
        # 按照到到达时间模拟执行进程并记录时间
        while not ready_queue.empty():
            job: JobState = ready_queue.get()
            print(
                f"\n时间片:[{self.timestamp}->{self.timestamp+self.time_slice}]")
            job.start_time = min((self.timestamp, job.start_time))
            used = job.pcb.run(time = self.time_slice, echo=True)
            self.timestamp += used
            for i in range(wait_queue.qsize()):
                j = wait_queue.get()
                if j.arrive_time <= self.timestamp:
                    ready_queue.put(j)
                else:
                    wait_queue.put(j)
            if job.pcb.is_finish():
                #
                job.finish_time = self.timestamp 
                print(f"{used!= self.time_slice and '提前'}结束:{job}")
            else:
                ready_queue.put(job)


class HRRNScheduling(JobScheduling):
    '''HRRN(高响应比优先)调度算法
    '''
    _name = 'HRRN'

    def get_priority(self, job: JobState):
        '''计算优先级
        '''
        return (job.wait_time(self.timestamp)+job.pcb.need_time)/job.pcb.need_time

    def run(self):
        for i in range(len(self.jobs)):
            print("当前时间:", self.timestamp)

            j = None
            # 找到未完成任务中优先级最高的
            for job in self.jobs:
                if job.pcb.is_finish():
                    continue
                if not j:
                    j = job
                else:
                    j = max(j, job, key=lambda j: self.get_priority(j))
            j.start_time = self.timestamp
            self.timestamp += j.pcb.run(echo=True)
            j.finish_time = self.timestamp
            # print(j.pcb)


if __name__ == "__main__":
    jobs_josn = []
    with open("jobs.json") as f:
        import json
        jobs_josn = json.load(f)
    jobs = [JobState(**p) for p in jobs_josn]
    # 确保按到达时间排序
    jobs.sort(key=lambda job: job.arrive_time)
    print(jobs)
    fcfs = FCFSScheduling(jobs)
    fcfs.launch()
    # 重置状态
    [job.reset() for job in jobs]

    sjf = SJFScheduling(jobs)
    sjf.launch()
    [job.reset() for job in jobs]

    rr = RRScheduling(jobs, time_slice=1)
    rr.launch()
    [job.reset() for job in jobs]

    hrrn = HRRNScheduling(jobs)
    hrrn.launch()
