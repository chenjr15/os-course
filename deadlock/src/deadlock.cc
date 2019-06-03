#include<iostream>
#include <cstdio>
#include<iomanip>
#include<fstream>
#include <vector>
#include <algorithm>
using namespace std;

class Resource {
private :
    int a;
    int b;
    int c;
public:
    Resource() :a(0),b(0),c(0) {}
    Resource(int _a,int _b,int _c):a(_a),b(_b),c(_c) {}
    void set(int _a,int _b,int _c) {
        a=_a;
        b=_b;
        c=_c;
    }
    Resource  operator+(const Resource& other) {
        return Resource(a+other.a,b+other.b,c+other.c);
    }
    Resource  operator-(const Resource& other) {
        return Resource(a-other.a,b-other.b,c-other.c);
    }
    bool  operator==(const Resource& other) {
        return a==other.a && b==other.b&& c==other.c;
    }
    bool  operator>(const Resource& other) {

        return a>other.a ||  b>other.b || c>other.c;
    }
    bool  operator<(const Resource& other) {
        return a<other.a && b<other.b&& c<other.c;
    }
    bool  operator>=(const Resource& other) {
        return a>=other.a || b>=other.b || c>=other.c;
    }
    bool  operator<=(const Resource& other) {
        return a<=other.a && b<=other.b&& c<=other.c;
    }
    void print(bool newline = false) {
        std::cout<<" <"<<a<<" "<<b<<" "<<c<<"> ";
        if (newline) {
            std::cout<<std::endl;
        }
    }
};



class Process {
public:
    int id;
    Resource allocated;
    Resource max;
    bool finished;
    Process(int _id,Resource _allocated,Resource _max):id(_id),allocated(_allocated),max(_max),finished(false) {}
    Process(int _id) :id(_id),finished(false) {
        allocated = Resource();
        max = Resource();
    }
    Resource get_need() {
        return (this->max - this->allocated);
    }
    void print() {
        cout<<id<<": ";
        (this->max).print();
        (this->allocated).print();
        (this->max - this->allocated).print();
        cout<<endl;
    }
};
bool safety_check(vector<Process*>& _process_list,Resource work );

int main() {
    unsigned num_process= 0 ;
    printf("请输入进程数量");
    scanf("%u",&num_process);

    vector<Process*> process_list;
    int a,b,c;
    Process* p;
    printf("请输入剩余可用资源\n");
    scanf("%d %d %d",&a,&b,&c);
    Resource avaiable(a,b,c);


    for (size_t i = 0; i < num_process; i++) {
        p = new Process(i);
        printf("请输入第%lu个进程的最大需求资源\n",i);
        scanf("%d %d %d",&a,&b,&c);
        p->max.set(a,b,c);
        printf("请输入第%lu个进程的已分配资源\n",i);
        scanf("%d %d %d",&a,&b,&c);
        p->allocated.set(a,b,c);
        process_list.push_back(p);
    }
    safety_check(process_list,avaiable);
    unsigned reqid;
    Resource req;
    while (true) {
        printf("剩余可用资源: ");
        avaiable.print(true);
        for(auto p : process_list) {
            p->print();
        }
        printf("请输入新的请求进程id: ");
        scanf("%u",&reqid);
        if (reqid>process_list.size()) {
            printf("请输入正确的id!\n");
            continue;
        }
        p = process_list[reqid];
        printf("请输入请求资源\n");
        scanf("%d %d %d",&a,&b,&c);
        req.set(a,b,c);

        if (req > (p->get_need())) {
            printf("超过所声明最大资源!\n");
            continue;
        }
        if (req > avaiable) {
            printf("系统资源不足!\n");
            continue;
        }
        // 尝试分配
        avaiable = avaiable- req;
        p->allocated  = p->allocated + req;
        // 进行安全性检查
        bool is_safe = safety_check(process_list,avaiable);
        if (!is_safe) {
            //  安全性算法检查失败, 尝试回退
            cout<<"unsafe!"<<endl;
            avaiable = avaiable+ req;
            p->allocated  = p->allocated - req;
        }


    }


    return 0;
}

bool safety_check(vector<Process*>& process_list,Resource work ) {
    bool safe=true;
    //安全性算法
    unsigned process_amount = process_list.size();
    vector<bool> finished(process_amount,false);
    vector<int> safety_order;
    Process* p;

    unsigned i = 0 ;
    // 外层循环控制一次遍历所有进程(每次至少有一个进程被选中执行, 否则就是是失败了)
    while(safety_order.size()!=process_amount) {
        // 内层循环选择每次遍历需要被选中的进程
        for( ; i < process_amount; ++i ) {
            p = process_list[i];
            if (  finished[i]) {
                continue;
            }
            if (p->get_need()>work) {
                continue;
            }
            safety_order.push_back(p->id);
            finished[i]=true;
            work=work+p->allocated;
            break;
        }

        if(i>= process_amount) {
            // not found satisfied process
            // try to pull back
            if (safety_order.size()==0) {
                // unsafe
                safe=false;
                break;
            }
            i =safety_order.back()+1;
            work=work-p->allocated;
            safety_order.pop_back();
        } else {
            i = 0;
        }
    }
    if (safe)
    {
        printf("找到安全序列:< ");
        for(auto p :  safety_order)
        {
            printf("%d ",p);
        }
        printf(">\n");

    }
    
    return safe;
}
