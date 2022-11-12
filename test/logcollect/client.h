#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include "mytcp.h"

#define HOST "127.0.0.1"
#define PORT 5555
#define INTERVAL 100
unsigned int ms = INTERVAL * 1000;

class TcpClient
{
public:
    TcpClient();
    void init();
    void tcpconnect();
    void sendmessage(const char *msg);
    char *recv();
    void disconnect();

private:
    int client_fd;
    int sock;
    struct sockaddr_in serv_addr;
    char buffer[BUF_SIZE];
    char hdr[HDR_SIZE];
};