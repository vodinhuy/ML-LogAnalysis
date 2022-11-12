#include "server.h"
#include <fstream>
#include <arpa/inet.h>

std::ofstream out;
void writeLog(const char *msg)
{
    // out << msg << "\n";
    // out.flush();
    std::string s(msg);
    std::string delimiter = "<br>";

    size_t pos = 0;
    std::string token;
    while ((pos = s.find(delimiter)) != std::string::npos)
    {
        token = s.substr(0, pos);
        out << token << "\n";
        s.erase(0, pos + delimiter.length());
    }
    out << s << "\n";
    out.flush();
}

TcpServer::TcpServer() : server_fd(0)
{
    memset(buffer, '\0', BUF_SIZE);
    memset(hdr, '\0', HDR_SIZE);
    memset(&address, 0, sizeof(address));
    init();
}

void TcpServer::init()
{
    int opt = 1;
    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET,
                   SO_REUSEADDR | SO_REUSEPORT, &opt,
                   sizeof(opt)))
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address,
             sizeof(address)) < 0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
}

void TcpServer::serverlisten()
{
    int addrlen = sizeof(address);
    int new_socket, valread;

    if (listen(server_fd, 3) < 0)
    {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    printf("Server listening on port %d\n", PORT);

    if ((new_socket = accept(server_fd, (struct sockaddr *)&address,
                             (socklen_t *)&addrlen)) < 0)
    {
        perror("accept");
        exit(EXIT_FAILURE);
    }
    printf("Connect from %s on port %d\n", inet_ntoa(address.sin_addr), (int)ntohs(address.sin_port));
    handleClient(new_socket);

    // closing the connected socket
    close(new_socket);
}

void TcpServer::sendmessage(const char *msg, const int &socket)
{
    const char *ptr = pack(strlen(msg));
    send(socket, ptr, HDR_SIZE, 0);
    send(socket, msg, strlen(msg), 0);
    printf("Send: %s\n", msg);
}

char *TcpServer::recv(const int &socket)
{
    printf("\nFrom client: %d\n", socket);
    memset(hdr, '\0', HDR_SIZE);
    int bs = read(socket, hdr, HDR_SIZE);
    if (bs < 4)
    {
        return NULL;
    }
    printf("Header (bytes): %d\n", bs);
    uint32_t msgsize = unpack(hdr);
    printf("msgsize=%d\n", msgsize);

    char *data = (char *)calloc(msgsize + 1, sizeof(char)); // data[msgsize] = '\0';
    uint32_t x = 0;
    while (x < msgsize)
    {
        memset(buffer, '\0', BUF_SIZE);
        int bs = (msgsize - x < BUF_SIZE) ? msgsize - x : BUF_SIZE;
        printf("Bytes read: %d\n", bs);
        int n = read(socket, buffer, bs);
        strncpy(data + x, buffer, n);
        x += n;
    }
    printf("Recv: %ld bytes\n", strlen(data));
    send(socket, ACK_MSG, 7, 0);
    return data;
}

void TcpServer::handleClient(const int &cli_socket)
{
    char *data = NULL;
    data = recv(cli_socket);
    if (data == NULL)
    {
        printf("null\n");
        return;
    }
    printf("Data: %s\n", data);
    free(data);
    const char *hello = "Message to broadcast!";
    sendmessage(hello, cli_socket);

    while (1)
    {
        data = recv(cli_socket);
        if (data == NULL)
        {
            printf("Client %d disconnected.\n", cli_socket);
            break;
        }
        writeLog(data);
        printf("%s\n", data);
        if (strcmp(data, "exit") == 0)
        {
            printf("Exiting...\n");
            break;
        }
        free(data);
    }
}

void TcpServer::finish()
{
    printf("finish\n");
    // closing the listening socket
    shutdown(server_fd, SHUT_RDWR);
}

int main(int argc, char const *argv[])
{
    TcpServer *server = new TcpServer;
    out.open("output.txt", std::ios::out);
    server->serverlisten();
    server->finish();
    out.close();
    return 0;
}