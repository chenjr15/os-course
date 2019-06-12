try :
    from dataclasses import dataclass
except ModuleNotFoundError:
    print("请使用Python 3.7+运行!")
    exit(-1)
from typing import List
from collections import namedtuple
from compose.cli.colors import green, red, blue, magenta
PAGE_SIZE = 1024


@dataclass
class PageReq:
    addr: int
    isread: bool

    def get_page_no(self):
        '''获取页号
        '''
        return self.addr // PAGE_SIZE

    def get_page_offset(self):
        '''获取页内地址
        '''
        return self.addr % PAGE_SIZE

    def __str__(self):
        return f'{self.addr}({"R" if self.isread else "W"}) 页号: {self.get_page_no()}'

    def __repr__(self):
        return self.__str__()


@dataclass
class PageItem(object):
    '''内存块情况
    '''
    page_no: int
    accessed: bool
    modified: bool
    pointer: int

    def access(self):
        # print(red(f"尝试访问{self.page_no}"))
        self.accessed = True

    def modify(self):
        self.modified = True

    def unaccess(self):
        ''' 访问位置零'''
        self.accessed = False

    def unmodified(self):
        ''' 访问位置零'''
        self.modified = False

    def __str__(self):
        return f'<{self.page_no if self.page_no is not None else "_"} '\
            f'{"A" if  self.accessed else "_"} ' \
            f'{"M" if self.modified else "_" } ' \
            f'next:{self.pointer}>'
    def __repr__(self):
        return f'[{self.page_no if self.page_no is not None else "_"}'\
            f'{"A" if  self.accessed else "_"}' \
            f'{"M" if self.modified else "_" }]'


PhyAddr = namedtuple('PhyAddr', ['Block', 'Offset', 'Address'])
PhyAddr.__str__ = lambda self: f'块号: {self.Block} 偏移量: {self.Offset} 物理地址: {self.Address}'


class Mem:
    def __init__(self, mem_info: List[PageItem], replace_ptr: int, free_ptr: int):
        # 替换指针访问位置零
        self.replace_ptr = replace_ptr
        # 空闲指针
        self.free_ptr = free_ptr
        self.phy_table = mem_info

    def get_generator(self, start=None, length=-1):
        ''' 返回一个通用生成器, 用来简化 替换队列和空闲队列 的遍历操作
            start : 生成器的起点
            length: 最多遍历个数
        '''
        count = 0
        if start is not None and start > -1 and start < len(self.phy_table):
            first = self.phy_table[start]
            pi = first
            yield pi
            pi = self.phy_table[pi.pointer]
            while pi != first:
                yield pi
                pi = self.phy_table[pi.pointer]

    def get_replace_generator(self):
        '''返回替换队列的生成器'''
        return self.get_generator(self.replace_ptr)

    def get_free_generator(self):
        '''返回空闲队列的生成器'''
        return self.get_generator(self.free_ptr)

    def get_phy_addr(self, req: PageReq):
        '''获得物理地址
        '''
        index = 0
        for pi in self.phy_table:
            if pi.page_no == req.get_page_no():
                break
            index += 1

        return PhyAddr(index, req.get_page_offset(), index*PAGE_SIZE + req.get_page_offset())

    @property
    def first_replace(self)->PageItem:
        '''返回替换队列第一个'''

        return self.phy_table[self.replace_ptr]

    @property
    def last_replace_index(self)->int:
        '''找到替换队列最后一个的索引'''

        pi = self.first_replace
        while pi.pointer != self.replace_ptr:
            pi = self.phy_table[pi.pointer]
        return self.phy_table.index(pi)

    def load_free(self,  new_page: int)->bool:
        '''将不在内存的页面调入空闲内存, 仅当内存有空闲块时可用'''

        if self.free_ptr is None:
            return False
        # 换到当前队列尾部
        lastitem = self.phy_table[self.last_replace_index]
        lastitem.pointer = self.free_ptr

        freeitem = self.phy_table[self.free_ptr]
        # self.phy_table[self.free_ptr] = PageItem()
        if freeitem.pointer == self.free_ptr:
            # 空闲块用尽
            self.free_ptr = None
        else:
            self.free_ptr = freeitem.pointer
        freeitem.page_no = new_page
        freeitem.unaccess()
        freeitem.unmodified()
        freeitem.pointer = self.replace_ptr

        return True

    def replace(self, to_replace: int, new_page: int):
        if self.phy_table[to_replace].page_no is None:
            print(red("不能替换空闲页!"))
            return False

        replace_item = self.phy_table[to_replace]
        # 让队头指针指向需要替换页面的下一个页面, 下一次就从那个页面开始替换
        # 然后原来第一个页面就自动变成队列的尾部(因为是循环队列/链表)
        self.replace_ptr = replace_item.pointer
        # print(magenta(self))
        # 将新页面换入, 并让其指向队头(就是原来的下一个)
        self.phy_table[to_replace] = PageItem(
            page_no=new_page,
            accessed=False,
            modified=False,
            pointer=replace_item.pointer
        )
        return True

    def access(self, index=None):
        if index is None:
            print(red("尝试访问全部"))
            [pi.access() for pi in self.phy_table]
        else:
            self.phy_table[index].access()

    def modify(self, index=None):
        if index is None:
            print(red("尝试修改全部"))

            [pi.modify() for pi in self.phy_table]
        else:
            self.phy_table[index].modify()

    def handle_req(self, req: PageReq, phy_no: int):
        self.access(phy_no)
        if not req.isread:
            self.modify(phy_no)

    def __str__(self):
        s = ''
        for i in range(len(self.phy_table)):
            s += f'{i} : {self.phy_table[i]}\n'

        s += "替换队列:"
        for pi in self.get_replace_generator():
            s += f" {self.phy_table.index(pi)}:{repr(pi)} ->"
        s += ' null\n'

        s += "空闲队列:"
        for pi in self.get_free_generator():
            s += f' #{self.phy_table.index(pi)} ->'
        s += ' null\n'
        return s


def clock(mem: Mem)->int:
    '''Clock 置换算法 返回可以被置换的页面索引'''
    to_replace: int = -1
    # 这里肯定是页面不在内存的情况
    # 遍历页面 如果有未被访问的块, 这返回该块索引, 对被访问过的块则清除其访问位
    for pi in mem.get_replace_generator():
        if pi.accessed:
            pi.unaccess()
        else:
            to_replace = mem.phy_table.index(pi)
            break
    return to_replace


def clock_advanced(mem: Mem)->int:
    '''Clock 置换算法 返回可以被置换的页面索引'''
    to_replace: int = -1
    # 第一步 寻找A = 0 M = 0 找到就返回该页做替换
    for pi in mem.get_replace_generator():
        if pi.accessed == False and pi. modified == False:
            to_replace = mem.phy_table.index(pi)
            break
    if to_replace < 0:
        # 没找到, 执行第二步. 找 A = 0 M = 1, 并且边找边清access位, 找到就返回
        for pi in mem.get_replace_generator():
            if pi.accessed == False and pi. modified == True:
                to_replace = mem.phy_table.index(pi)
                break
            else:
                pi.unaccess()
    return to_replace
def load_test_data():
    # 替换指针
    replace_ptr = 0
    # 空闲指针
    free_ptr = 2
    mem_info = []
    mem_info.append(PageItem(4, True, True, 1))
    mem_info.append(PageItem(2, False, True, 3))
    mem_info.append(PageItem(None, None, None, 2))
    mem_info.append(PageItem(0, 1, 0, 0))
    mem = Mem(mem_info, replace_ptr, free_ptr)
    page_reqs = []
    page_reqs.append(PageReq(455, True))
    page_reqs.append(PageReq(1029, True))
    page_reqs.append(PageReq(2093, False))
    page_reqs.append(PageReq(2612, False))
    page_reqs.append(PageReq(3106, True))
    page_reqs.append(PageReq(4149, False))
    page_reqs.append(PageReq(5122, True))
    page_reqs.append(PageReq(6211, True))
    page_reqs.append(PageReq(6897, True))
    page_reqs.append(PageReq(875, False))

    return mem,page_reqs

def main():
    
    use_clock = False
    mem,page_reqs = load_test_data()
    print(red('####程序开始####'))
    print('初始内存状态为:')
    print(mem)
    choice = input('请选择调度算法 0.Clock 1.改进型Clock :')
    if choice == '0':
        use_clock = True
    print('您选择了', 'Clock'if use_clock else '改进型Clock')
    for req in page_reqs:
        # 遍历请求
        print('-'*10)
        print(f"\n{magenta('->')} requst: {req}\n")
        phy_no = None
        phyaddr: PhyAddr
        for p in mem.phy_table:
            if req.get_page_no() == p.page_no:
                # 该地址在内存中, 直接访问即可
                # 获取对应物理块号
                phy_no = mem.phy_table.index(p)
                mem.handle_req(req, phy_no)
        if phy_no is not None:
            phyaddr = mem.get_phy_addr(req)
            print(blue("命中内存"))
            print(f"{green(phyaddr)}")
        else:
            print(f"该地址不在内存块中, {red('发生缺页中断')}")
            if mem.load_free(req.get_page_no()):
                print(blue("成功载入空闲内存"))
                phyaddr = mem.get_phy_addr(req)
                print(f"{green(phyaddr)}")
                mem.handle_req(req, phyaddr.Block)
            else:
                # 尝试替换
                # clock
                if use_clock:
                    to_replace: int = clock(mem)
                    if to_replace < 0:
                        to_replace = clock(mem)
                else:
                    to_replace: int = clock_advanced(mem)

                    if to_replace < 0:
                        to_replace = clock_advanced(mem)

                print(blue(f"成功替换物理块{to_replace}"))
                mem.replace(to_replace, req.get_page_no())
                mem.handle_req(req, to_replace)
                # print(mem)
                phyaddr = mem.get_phy_addr(req)
                print(f"{green(phyaddr)}")
        print('当前内存状态为:')
        print(mem)


if __name__ == "__main__":
    main()
