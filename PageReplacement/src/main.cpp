#include <iostream>
#include <cstdio>
#include <ctime>
#include <vector>
#include <algorithm>
using namespace std;
// 页面数据类型
typedef int page_t;
typedef vector<page_t> page_seq_t;
#define EMPTY_PAGE -1
void print_physics_page(page_t& current_request,page_seq_t& physics_page, int page_fault_index);
// 返回缺页次数
unsigned pr_opi(page_seq_t& page_requests,page_seq_t& physics_page,unsigned page_amount);
unsigned pr_fifo(page_seq_t& page_requests,page_seq_t& physics_page);
unsigned pr_lru(page_seq_t& page_requests,page_seq_t& physics_page,unsigned page_amount);

unsigned get_min_index(vector<clock_t>& page_usage, page_seq_t& physics_page);


int main() {
    unsigned physics_page_size;
    unsigned page_requests_size;
    unsigned page_size;

    cout<<"请输入页面数量,物理页大小和页面引用串数量：";
    cin>>page_size>>physics_page_size>>page_requests_size;
    // 页面请求引用串
    page_seq_t page_requests(page_requests_size,EMPTY_PAGE);
    // 物理页
    page_seq_t physics_page(physics_page_size,EMPTY_PAGE);

    for (size_t i = 0; i < page_requests_size; ++i) {
        cout<<"请输入第"<<i<<"个页面引用:";
        cin>>page_requests[i];
    }
    cout<<endl;

    unsigned page_fault_count =0;
    int selected = 0;
    cout<<"请选择算法：0.fifo 1.lru 2.opi"<<endl;
    while (cin>>selected) {

        switch (selected) {
        case 0:
            page_fault_count =  pr_fifo(page_requests,physics_page);
            break;
        case 1:
            page_fault_count =  pr_lru(page_requests,physics_page,page_size);
            break;
        case 2:
            page_fault_count =  pr_opi(page_requests,physics_page,page_size);
            break;

        default:
            cout<<"Worng input!"<<endl;
            continue;
        }
        printf("缺页次数:%u 缺页率: %d%%\n",page_fault_count,page_fault_count*100/page_requests_size);
        cout<<"请选择算法：0.fifo 1.lru 2.opi"<<endl;
        for (size_t i = 0; i < physics_page.size(); i++)
        {
            physics_page[i] = EMPTY_PAGE;
        }
        

    }

}
int get_furthest(page_seq_t& page_requests,page_seq_t& physics_page,unsigned cur_index) {
    vector<unsigned> distance(physics_page.size(),-1);
    int to_replace = 0;
    for (size_t i = 0; i < physics_page.size(); ++i) {
        
        if(physics_page[i] == EMPTY_PAGE) {
            // 页面未满
            return i;
        }
        for (size_t j = cur_index+1; j < page_requests.size(); ++j) {
            if (page_requests[j] == physics_page[i]) {
                distance[i] = j;
                break;
            }
        }
        if (distance[i]>distance[to_replace])
        {
            to_replace = i;
        }
    }
    return to_replace;

}
unsigned pr_opi(page_seq_t& page_requests,page_seq_t& physics_page,unsigned page_amount) {
    unsigned page_fault_count = 0;
    unsigned physics_page_size = physics_page.size();
    auto current_request = page_requests[0];
    int  to_replace = -1;
    printf("OPI 置换算法\n");
    for (size_t cur_index = 0; cur_index < page_requests.size(); ++cur_index) {
        current_request = page_requests[cur_index];

        // 检查当前访问页面是否在物理页中
        auto result = find(begin(physics_page),end(physics_page),current_request);
        if (result == end(physics_page)) {
            // 未找到, 缺页中断发生
            ++page_fault_count;
            to_replace = get_furthest(page_requests,physics_page,cur_index);
            // 替换最先加入的页面为新的页面
            physics_page[to_replace] = current_request;

        } else {
            to_replace = -1;
        }
        print_physics_page(current_request,physics_page,to_replace);

    }
    return page_fault_count;
}
unsigned pr_fifo(page_seq_t& page_requests,page_seq_t& physics_page) {
    unsigned head_ptr = 0;
    unsigned physics_page_size = physics_page.size();
    unsigned page_fault_count = 0;
    int to_replace = -1;
    printf("FIFO 置换算法\n");
    for (size_t i = 0; i < page_requests.size(); ++i) {
        // 检查当前访问页面是否在物理页中
        auto result = find(begin(physics_page),end(physics_page),page_requests[i]);
        if (result == end(physics_page)) {
            // 未找到, 缺页中断发生
            ++page_fault_count;
            // 替换最先加入的页面为新的页面
            physics_page[head_ptr] = page_requests[i];
            to_replace = head_ptr;
            // 更新头指针
            ++head_ptr;
            head_ptr%= physics_page_size;
        } else {
            to_replace = -1;
        }

        print_physics_page(page_requests[i],physics_page,to_replace);

    }
    return page_fault_count;

}
unsigned pr_lru(page_seq_t& page_requests,page_seq_t& physics_page,unsigned page_amount) {
    unsigned page_fault_count = 0;
    unsigned physics_page_size = physics_page.size();
    vector<clock_t> page_usage(page_amount,-1);
    auto current_request = page_requests[0];
    int  to_replace = -1;
    printf("LRU 置换算法\n");
    for (size_t i = 0; i < page_requests.size(); ++i) {
        current_request = page_requests[i];
        page_usage[current_request]=clock();

        // 检查当前访问页面是否在物理页中
        auto result = find(begin(physics_page),end(physics_page),current_request);
        if (result == end(physics_page)) {
            // 未找到, 缺页中断发生

            ++page_fault_count;
            to_replace = get_min_index(page_usage,physics_page);
            // 替换最先加入的页面为新的页面
            physics_page[to_replace] = current_request;

        } else {
            to_replace = -1;
        }
        print_physics_page(current_request,physics_page,to_replace);

    }
    return page_fault_count;
}

unsigned get_min_index(vector<clock_t>& page_usage, page_seq_t& physics_page) {
    unsigned to_replace = 0;
    time_t  min_val = page_usage[physics_page[0]];
    // putchar('\n');
    for(size_t i = 0 ; i< physics_page.size(); ++i) {
        if(physics_page[i] == -1) {
            // 页面未满
            return i;
        }
        // printf("x page_usage[physics_page[%u]](%lu) < min_val=%lu | %d \n",i,page_usage[physics_page[i]],min_val,page_usage[physics_page[i]] < min_val);
        if (page_usage[physics_page[i]] < min_val) {
            to_replace = i;
            min_val = page_usage[physics_page[i]];
        }
    }
    return to_replace;
}
void print_physics_page(page_t& current_request,page_seq_t& physics_page, int page_fault_index) {
    printf("%d: %c ",current_request,page_fault_index!=-1?'*':' ');
    for (size_t i = 0; i < physics_page.size(); i++) {
        if (i == page_fault_index) {
            printf("\033[32m%c\033[0m ",(physics_page[i])<0?'_':physics_page[i]+'0');
        } else {
            printf("%c ",(physics_page[i])<0?'_':physics_page[i]+'0');
        }
    }
    putchar('\n');
}