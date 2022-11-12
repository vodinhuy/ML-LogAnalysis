#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include "mytcp.h"

#define PORT 5555

class TcpServer
{
public:
    TcpServer();
    void init();
    void serverlisten();
    void sendmessage(const char *msg, const int &socket);
    char *recv(const int &socket);
    void handleClient(const int &socket);
    void finish();

private:
    int server_fd;
    struct sockaddr_in address;
    char buffer[BUF_SIZE];
    char hdr[HDR_SIZE];
};