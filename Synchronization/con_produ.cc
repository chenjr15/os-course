#include <iostream>
#include<atomic>
#include<thread>
#include<ctime>
#include<cstdio>
#include<chrono>
class Semaphore {
public:
    Semaphore( unsigned _count ):
        count( _count ) {}
    void wait() {
        while ( count <= 0 ) {
            std::this_thread::sleep_for( std::chrono::milliseconds( 100 ) );
        }
        --count;
    }
    void sinal() {
        ++count;
    }
private:
    std::atomic<unsigned>  count;
};

const int buffer_size = 10;
Semaphore mutex( 1 );
Semaphore full( 0 );
Semaphore empty( buffer_size );
char buffer[buffer_size];

int in = 0;
int out = 0;
/* 消费者模型 */
void consumer(size_t id ) {
    
    while ( true ) {
        printf( "consumer %d waiting \n",id );
        full.wait();
        mutex.wait();
        out = out % buffer_size;
        int item = buffer[out];
        ++out;
        printf( "consumer#%d \t-[%d] \n",id, item );
        mutex.sinal();
        empty.sinal();
        std::this_thread::sleep_for( std::chrono::seconds( 3 ) );

    }

}
/* 生产者模型 */
int   item_add = 0;
void producer(size_t id ) {
    while ( true ) {
        printf( "producer#%d waiting \n",id );

        empty.wait();
        mutex.wait();
        // buffer[in];
        in = in % buffer_size;
        ++item_add;
        buffer[in] = item_add;
        printf( "producer#%d \t+[%d] \n",id, item_add);
        ++in;
        mutex.sinal();
        full.sinal();
        std::this_thread::sleep_for( std::chrono::seconds( 1 ) );
    }

}

int main() {
    const int consumer_amount = 3;
    const int producer_amount = 3;

    std::thread c[consumer_amount];
    std::thread p[producer_amount];
    for ( size_t i = 0; i < consumer_amount; i++ ) {
        c[i] = std::thread( consumer,i );

    }
    for ( size_t i = 0; i < producer_amount; i++ ) {
        p[i] = std::thread( producer,i );

    }

    for ( size_t i = 0; i < consumer_amount; i++ ) {
        c[i].join();

    }
    for ( size_t i = 0; i < producer_amount; i++ ) {
        p[i].join();

    }
    // c.join();
    // p.join();
    printf( "Done.\n" );

}
