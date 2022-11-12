#include "client.h"
#include <fstream>
#include <cstring>

TcpClient::TcpClient() : client_fd(0), sock(0)
{
    memset(buffer, '\0', BUF_SIZE);
    memset(hdr, '\0', HDR_SIZE);
    memset(&serv_addr, 0, sizeof(serv_addr));
    init();
}

void TcpClient::init()
{
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("\n Socket creation error \n");
        return;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    // Convert IPv4 and IPv6 addresses from text to binary form
    if (inet_pton(AF_INET, HOST, &serv_addr.sin_addr) <= 0)
    {
        printf("\nInvalid address/ Address not supported \n");
        return;
    }
}

void TcpClient::tcpconnect()
{
    int valread;

    if ((client_fd = connect(sock, (struct sockaddr *)&serv_addr,
                             sizeof(serv_addr))) < 0)
    {
        printf("\nConnection Failed \n");
        return;
    }
    const char *hello = "Hello from client";
    sendmessage(hello);
    printf("Hello message sent\n");
    char *data = NULL;
    data = recv();
    printf("Data: %s\n", data);
    free(data);
}

void TcpClient::sendmessage(const char *msg)
{
    const char *ptr = pack(strlen(msg));
    send(sock, ptr, HDR_SIZE, 0);
    send(sock, msg, strlen(msg), 0);
    printf("%s\n", msg);
    char buf[7] = {0};
    int ack = read(sock, buf, 7);
    printf("ACK: %d\n", ack);
    if (strncmp(ACK_MSG, buf, strlen(ACK_MSG)) == 0)
    {
        printf("Received ACK %s\n", ACK_MSG);
    }
}

char *TcpClient::recv()
{
    char *data = NULL;
    memset(hdr, '\0', HDR_SIZE);
    int bs = read(sock, hdr, HDR_SIZE);
    printf("Header (bytes): %d\n", bs);
    uint32_t msgsize = unpack(hdr);
    printf("msgsize=%d\n", msgsize);

    data = (char *)calloc(msgsize + 1, sizeof(char)); // data[msgsize] = '\0';
    uint32_t x = 0;
    while (x < msgsize)
    {
        memset(buffer, '\0', BUF_SIZE);
        int bs = (msgsize - x < BUF_SIZE) ? msgsize - x : BUF_SIZE;
        printf("Bytes read: %d\n", bs);
        int n = read(sock, buffer, bs);
        strncpy(data + x, buffer, bs);
        x += n;
    }
    return data;
}

void TcpClient::disconnect()
{
    printf("disconnect\n");
    // closing the connected socket
    close(client_fd);
}

int main(int argc, char const *argv[])
{
    TcpClient *client = new TcpClient;
    client->tcpconnect();

#ifdef USER_INPUT_TEST
    while (1)
    {
        char msg[255];
        printf("Enter message: ");
        std::cin.getline(msg, 255);
        sendmessage(msg);
    }
#endif

    std::ifstream logfile("../access_log.txt", std::ios::in);
    std::string line;
    while (getline(logfile, line))
    {
        printf("\nSend: %ld bytes\n", line.length());
        char *msg = new char[line.length() + 1];
        std::strcpy(msg, line.c_str());
        client->sendmessage(msg);
        usleep(ms);
        delete[] msg;
    }
    client->disconnect();
    return 0;
}