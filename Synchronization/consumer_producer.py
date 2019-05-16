from threading import Thread
import threading
import time
import random
# import queue.
# 初始化全局变量

mutex = threading.Semaphore(0)
full = threading.Semaphore(3)
empty = threading.Semaphore(2)
items = []
class Consumer(Thread):
    def __init__(self,_id):
        self._id = _id
        Thread.__init__(self)

    def run(self):
        while True:
            full.acquire()
            # print(f"Consumer#{self._id}","got full")
            mutex.acquire()
            # print(f"Consumer#{self._id}","got mutex")

            item = items.pop()
            print(f"{time.clock()} Consumer#{self._id} consumed {(item)}, total <{(items)}>", )
            
            empty.release()
            mutex.release()
            time.sleep(2)
            


class Producer(Thread):
    i = 0
    def __init__(self,_id,total_produce = 20):
        self._id = _id
        self.total_produce= total_produce
        Thread.__init__(self)
    

    def run(self):
        
        while self.i <self.total_produce:
            time.sleep(2*random.random())

            empty.acquire()
            # print(f"Producer#{self._id}","got empty")
            mutex.acquire()
            item = random.randint(1,100)
            items.append(item)
            full.release()
            mutex.release()
            print(f"{time.clock()} Producer#{self._id} Produced {item}, total :<{items}>")

            


if __name__ == "__main__":

    # consumer_size = int(input("Consumer size:"))
    # producer_size = int(input("Producer size:"))
    # buffer_size = int(input("Buffer size:"))
    consumer_size = 2
    producer_size = 3
    buffer_size = 8

    mutex = threading.BoundedSemaphore(1)

    full = threading.Semaphore(0)
    # 设定初始的空buffer 及有几个生产者线程可以生产
    empty = threading.Semaphore(buffer_size)
    # 创建指定数量的Consumer和Producer
    consumers = [ Consumer(i) for i in range(consumer_size)]
    producers = [ Producer(i) for i in range(producer_size)]
    time.clock()
    print("{:8f} Starting.".format(time.clock()))
    [p.start() for p in producers]
    [c.start() for c in consumers]


    [p.join() for p in producers]
    print("Produce finished")



