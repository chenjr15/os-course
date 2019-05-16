from threading import Thread
import threading
import time
import random
# import queue.
# 初始化全局变量
class Semaphore(object):
    '''用条件变量实现的简单信号量
    '''
    def __init__(self, value):
        print("construct",value)
        self.value = value
        self.cond = threading.Condition()
    def wait(self):
        
        while self.value < 1:
            with self.cond:
                self.cond.wait()
        self.value -=1
    def signal(self):
        with self.cond:
            self.value +=1
            self.cond.notify()
        
mutex = Semaphore(0)
full = Semaphore(3)
empty = Semaphore(2)
items = []
# 他使用名称 P() 和 V() 而不是 wait() 和 signal()
class Consumer(Thread):
    def __init__(self,_id):
        self._id = _id
        Thread.__init__(self)

    def run(self):
        global items
        while True:
            full.wait()
            # print(f"Consumer#{self._id}","got full")
            mutex.wait()
            # print(f"Consumer#{self._id}","got mutex")
            item = items[0]
            items= items[0:]
            print(f"{time.clock()} Consumer#{self._id} consumed {(item)}, total <{(items)}>", )
            
            empty.signal()
            mutex.signal()
            time.sleep(1)
            


class Producer(Thread):
    i = 0
    def __init__(self,_id,total_produce = 20):
        self._id = _id
        self.total_produce= total_produce
        Thread.__init__(self)
    

    def run(self):
        global items
        
        while self.i <self.total_produce:
            time.sleep(2*random.random())

            empty.wait()
            # print(f"Producer#{self._id}","got empty")
            mutex.wait()
            item = random.randint(1,100)
            items.append(item)
            full.signal()
            mutex.signal()
            print(f"{time.clock()} Producer#{self._id} Produced {item}, total :<{items}>")

            


if __name__ == "__main__":

    # consumer_size = int(input("Consumer size:"))
    # producer_size = int(input("Producer size:"))
    # buffer_size = int(input("Buffer size:"))
    consumer_size = 2
    producer_size = 3
    buffer_size = 5

    mutex = Semaphore(1)

    full = Semaphore(0)
    # 设定初始的空buffer 及有几个生产者线程可以生产
    empty = Semaphore(buffer_size)
    # 创建指定数量的Consumer和Producer
    consumers = [ Consumer(i) for i in range(consumer_size)]
    producers = [ Producer(i) for i in range(producer_size)]
    time.clock()
    print("{:8f} Starting.".format(time.clock()))
    [p.start() for p in producers]
    [c.start() for c in consumers]


    [p.join() for p in producers]
    print("Produce finished")



