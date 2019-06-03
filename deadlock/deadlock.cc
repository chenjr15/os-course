#include<iostream>
#include<iomanip>
#include<fstream>
using namespace std;
#define MAX_PROC_NUMBER 100

int Available[MAX_PROC_NUMBER];
int Max[MAX_PROC_NUMBER][MAX_PROC_NUMBER];
int Allocation[MAX_PROC_NUMBER][MAX_PROC_NUMBER];
int Need[MAX_PROC_NUMBER][MAX_PROC_NUMBER];
int Request[MAX_PROC_NUMBER];
int SafeOrder[MAX_PROC_NUMBER];
// 进程数量
int process_amount;
// 资源数量
int res_amount;

void safety_check(int id);
void bank(int id);

int main() {
    int i = 0;
    int j = 0;
    ifstream fin;
    fin.open("input.txt");
    fin>>process_amount;
    fin>>res_amount;
    for( i = 0; i < res_amount; ++i) {
        //初始化Request
        Request[i] = 0;
    }
    for(i=0; i<process_amount; ++i) {
        // 输入已分配的资源
        for(j=0; j<res_amount; ++j) {
            fin>>Allocation[i][j];
        }
    }
    for(i=0; i<process_amount; ++i) {
        //读入Need ij
        for(j=0; j<res_amount; ++j) {
            fin>>Need[i][j];
        }
    }
    for(i=0; i<res_amount; ++i) {
        //读入Available
        fin>>Available[i];
    }

    for(i=0; i<process_amount; ++i) {
        //计算Max
        for(j=0; j<res_amount; ++j) {
            Max[i][j] = Need[i][j] + Allocation[i][j];
        }
    }

    //输出资源分配表
    int a=1;
    cout<<"资源分配情况如下："<<endl;
    cout<<"资源 "<<setw(15)<<"Max"<<setw(15)<<"Allocation"<<setw(15)<<"Need"<<setw(15)<<"Available"<<endl;
    cout<<"进程 "<<setw(15)<<"A    B    C"<<setw(15)<<"A    B    C"<<setw(15)<<"A    B    C"<<setw(15)<<"A    B    C"<<endl;
    for(i=0; i<process_amount; ++i) {
        cout<<i<<"    ";
        for(j=0; j<res_amount; ++j) {
            cout<<setw(5)<<Max[i][j];
        }
        for(j=0; j<res_amount; ++j) {
            cout<<setw(5)<<Allocation[i][j];
        }
        for(j=0; j<res_amount; ++j) {
            cout<<setw(5)<<Need[i][j];
        }
        if (a == 1) {
            for(j=0; j<res_amount; ++j) {
                cout<<setw(5)<<Available[j];
            }
            a=0;
        }
        cout<<endl;
    }

    safety_check(0);

    int id = -1;//要请求的进程id

    while(1) {
        cout<<"请输入要请求的进程号码：";
        cin>>id;
        cout<<"请分别输入请求的资源："<<endl;
        for(j=0; j<res_amount; ++j)
            cout<<(char)(65+j)<<" ";
        cout<<endl;
        for(j=0; j<res_amount; ++j)
            cin>>Request[j];

        bank(id);

    }
    return 0;
}

void safety_check(int id) {
    //安全性算法
    int Work[MAX_PROC_NUMBER];
    bool Finish[MAX_PROC_NUMBER];
    int SafeOrder[MAX_PROC_NUMBER];
    int i = 0;
    int j = 0;
    int k = 0;
    for(i = 0; i < res_amount; ++i)
        Work[i] = Available[i];
    for(i = 0; i < process_amount; ++i)
        Finish[i] = false;

    int coutt = 0, time = 0, c=0;

    while(time != 300) {
        for( i = 0; i < process_amount; ++i ) {
            time++;
            if( Finish[i] == false ) {
                for( j = 0; j < res_amount; ++j ) {
                    if( Need[i][j] <= Work[j] )
                        c++;
                    else {
                        c = 0;
                        break;
                    }
                }
                if ( c == res_amount ) {
                    /*找到了满足下述条件的进程：
                    　　                  Finish[i]=false
                    　　                  Need[i,j]≤Work[j]*/
                    for( j = 0; j < res_amount; ++j)
                        Work[j] = Work[j] + Allocation[i][j];
                    Finish[i] = true;
                    SafeOrder[coutt] = i;//将进程id插入安全序列
                    coutt++;
                    c = 0;
                }
            }
        }
    }
    if (coutt == process_amount) {
        cout<<"安全序列为：";
        for ( k = 0; k < process_amount; k++)
            cout<<SafeOrder[k];
        cout<<endl;
    } else {
        cout<<"不安全"<<endl<<endl;
        for( i = 0; i < res_amount; ++i) {
            Available[i] += Request[i];
            Allocation[id][i] -= Request[i];
            Need[id][i] += Request[i];
        }
    }
}

void bank(int id) {
    //银行家算法
    int i, cou=0, coutt=0;
    for( i = 0; i < res_amount; ++i)
        if( Request[i] <= Need[id][i] )
            cou++;
    if(cou == res_amount) {
        for( i = 0; i < res_amount; ++i)
            if( Request[i] <= Available[i] )
                coutt++;
        if( coutt == res_amount ) {
            for( i = 0; i < res_amount; ++i) {
                Available[i] -= Request[i];
                Allocation[id][i] += Request[i];
                Need[id][i] -= Request[i];
            }
            cou=0;
            coutt=0;
            safety_check(id);
        } else {
            cout<<"出错，无足够资源"<<endl;
            cou=0;
            coutt=0;
        }

    } else {
        cout<<"出错，所需资源大于需要的最大值"<<endl;
        cou=0;
    }
}
