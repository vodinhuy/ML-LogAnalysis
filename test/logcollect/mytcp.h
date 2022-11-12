#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <stdint.h>
#include <netinet/in.h>

#define BUF_SIZE 1024
#define HDR_SIZE 4
// 0 -> Broadcast to all clients. You may specify the client id.
// # 1 -> Message type. 2 -> binary, 1 -> text

#ifdef FUTURE
enum MSG_TYPE
{
    MSG_TYPE_TEXT = 1,
    MSG_TYPE_BINARY = 2
};

struct Header
{
    uint32_t client;
    uint32_t type;
    uint32_t msg_size;
};
#endif

size_t pack_uint32(void *buf, uint32_t val);
size_t unpack_uint32(const void *b, uint32_t *val);
char *pack(const uint32_t &msgsize);
char *pack(const uint32_t &msgsize, uint32_t client, uint32_t type);
uint32_t unpack(char *p);