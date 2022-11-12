#include "mytcp.h"

size_t pack_uint32(void *buf, uint32_t val)
{
    uint32_t v32 = htonl(val);
    memcpy(buf, &v32, sizeof(uint32_t));
    return sizeof(uint32_t);
}

size_t unpack_uint32(const void *b, uint32_t *val)
{
    uint32_t v32 = 0;
    memcpy(&v32, b, sizeof(uint32_t));
    *val = ntohl(v32);
    return sizeof(uint32_t);
}

/**
 * @brief Pack message size
 */
char *pack(const uint32_t &msgsize)
{
    char *p = (char *)calloc(HDR_SIZE, sizeof(char));
    char *ptr = p;
    pack_uint32(ptr, msgsize);

    return p;
}

/**
 * @brief Pack client id, message type and message size
 */
char *pack(const uint32_t &msgsize, uint32_t client, uint32_t type)
{
    char *p = (char *)calloc(sizeof(uint32_t) * 3, sizeof(char));
    char *ptr = NULL;

    ptr = p;
    ptr += pack_uint32(ptr, client);
    ptr += pack_uint32(ptr, type);
    ptr += pack_uint32(ptr, msgsize);

    // free(p);
    return p;
}

uint32_t unpack(char *p)
{
    uint32_t size = 0;
    char *ptr = p;
    unpack_uint32(ptr, &size);
    return size;
}