from dataclasses import dataclass
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
        return f'{self.addr}({"R" if self.isread else "W"}) 页号|offse: {self.get_page_no()}|{self.get_page_offset()}'

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
        
        print(red(f"尝试设置页号{self.page_no}为访问"))
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


@dataclass
class Process:
    page_table: List[int]


PhyAddr = namedtuple('PhyAddr', ['Block', 'Offset', 'Address'])
PhyAddr.__str__ = lambda self: f'块号: {self.Block} 偏移量: {self.Offset} 物理地址: {self.Address}'


class Mem:
    def __init__(self, mem_info: List[PageItem], replace_ptr: int, free_ptr: int):
        # 替换指针访问位置零
        self.replace_ptr = replace_ptr
        # 空闲指针
        self.free_ptr = free_ptr
        self.phy_table = mem_info

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

    def find_pre_item(self, index: int)->PageItem:
        '''找到指定节点的前驱'''
        pi = self.phy_table[index]
        while pi.pointer != index:
            pi = self.phy_table[pi.pointer]
        return pi

    def find_pre_item_index(self, index: int)->int:
        '''找到指定节点的前驱索引'''
        return self.phy_table.index(self.find_pre_item(index))

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
        # if not self.phy_table[to_replace].page_no:
        #     print("不能替换空闲页")
        #     return False

        replace_item = self.phy_table[to_replace]
        self.replace_ptr = replace_item.pointer
        # # 让上一个指向下一个
        # self.phy_table[last_index].pointer = replace_item.pointer
        print(magenta(self))
        # 将新页面插入队尾
        self.phy_table[to_replace] = PageItem(
            page_no=new_page,
            accessed=False,
            modified=False,
            pointer=replace_item.pointer
        )
        # self.phy_table[last_index].pointer = index
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
        if self.replace_ptr is not None:
            s += "replace list:"
            pi = self.first_replace
            s += f' {self.phy_table.index(pi)}@{pi}'
            pi = self.phy_table[pi.pointer]
            while pi != self.first_replace:
                s += f' {self.phy_table.index(pi)}@{pi}'
                pi = self.phy_table[pi.pointer]
            s += '\n'
        else:
            s += '可替换队列为空\n'
        if self.free_ptr is not None:
            s += "free list:"
            pi = self.phy_table[self.free_ptr]
            s += f' {self.phy_table.index(pi)}@{pi}'
            pi = self.phy_table[pi.pointer]
            while pi != self.phy_table[self.free_ptr]:
                s += f' {self.phy_table.index(pi)}@{pi}'
                pi = self.phy_table[pi.pointer]
            s += '\n'
        else:
            s += '空闲队列为空\n'
        return s


def clock(mem: Mem)->int:
    '''Clock 置换算法 返回可以被置换的页面索引'''
    to_replace: int = -1
    # 这里肯定是页面不在内存的情况
    pi = mem.phy_table[mem.replace_ptr]
    if pi.accessed:
        pi.unaccess()
    else:
        to_replace = mem.phy_table.index(pi)
        return to_replace
        pi = mem.phy_table[pi.pointer]
    while pi != mem.first_replace:
        if pi.accessed:
            pi.unaccess()
            return to_replace
        else:
            to_replace = mem.phy_table.index(pi)
        pi = mem.phy_table[pi.pointer]
    return to_replace


def clock_advanced(mem: Mem)->int:
    '''Clock 置换算法 返回可以被置换的页面索引'''
    to_replace: int = -1
    # 这里肯定是页面不在内存的情况
    pi = mem.phy_table[mem.replace_ptr]
    # 第一步
    if pi.accessed or pi.modified:
        pi = mem.phy_table[pi.pointer]
    else:
        # A=0 M = 0
        to_replace = mem.phy_table.index(pi)
        return to_replace
    
    while pi != mem.first_replace:
        if pi.accessed or pi.modified:
            pass
        else:
            # A=0 M = 0
            to_replace = mem.phy_table.index(pi)
            return to_replace
        pi = mem.phy_table[pi.pointer]
    # 第二步
    pi = mem.phy_table[mem.replace_ptr]
    if not pi.accessed and pi.modified:
        # A = 1 M = 0
        to_replace = mem.phy_table.index(pi)
        return to_replace
    pi.unaccess()
    pi = mem.phy_table[pi.pointer]
    while pi != mem.first_replace:
        if not pi.accessed and pi.modified:
            # A = 1 M = 0
            to_replace = mem.phy_table.index(pi)
            return to_replace
        pi.unaccess()
        pi = mem.phy_table[pi.pointer]
    return to_replace


def test():
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
    use_clock = False
    print(red('程序开始'), '使用算法为', 'Clock'if use_clock else 'Clock+')
    print(mem)

    # print(mem.load_free(5), mem)
    # print(mem.load_free(6), '\n', mem)
    # print(mem.replace(1, 6), '\n', mem)

    page_table = [None for i in range(7)]
    page_table[0] = 3
    page_table[1] = 1
    page_table[4] = 0

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
    for req in page_reqs:
        print('-'*10)
        print(f"{blue('->')} requst: {req}")
        phy_no = None
        phyaddr: PhyAddr
        for p in mem.phy_table:
            if req.get_page_no() == p.page_no:
                # 改地址在内存中, 直接访问即可
                # 获取对应物理块号
                phy_no = mem_info.index(p)
                mem.handle_req(req, phy_no)
        if phy_no is not None:
            phyaddr = mem.get_phy_addr(req)
            print(f"物理地址为: {green(phyaddr)}")
        else:
            print(f"  该地址不在内存块中, {red('发生缺页中断')}")
            if mem.load_free(req.get_page_no()):
                phyaddr = mem.get_phy_addr(req)
                print(f"物理地址为: {green(phyaddr)}")
                mem.handle_req(req, phyaddr.Block)
                print(green("成功载入空闲内存"))
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
                        print("clock 改进 第一轮和第二轮")
                        print(mem)
                        to_replace = clock_advanced(mem)
                        print(mem)
                
                print(f"替换物理块{to_replace}")
                mem.replace(to_replace, req.get_page_no())
                mem.handle_req(req, to_replace)
                # print(mem)
                phyaddr = mem.get_phy_addr(req)
                print(f"物理地址为: {green(phyaddr)}")
        print('当前内存状态为:\n')
        print(mem)


if __name__ == "__main__":
    test()
