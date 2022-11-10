#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <stdint.h>

size_t pack_uint32(void* buf, uint32_t val) {
  uint32_t v32 = htonl(val);
  memcpy(buf, &v32, sizeof(uint32_t));
  return sizeof(uint32_t);
}

int main() {
  char *p = calloc (sizeof(uint32_t) * 3, sizeof(char)), *ptr;
  const char *msg = "Message to broadcast";
  const char *fifo = "/tmp/wspipein.fifo";
  int fd;

  ptr = p;
  ptr += pack_uint32(ptr, 0);
  ptr += pack_uint32(ptr, 0x01);
  ptr += pack_uint32(ptr, strlen(msg));

  fd = open(fifo, O_WRONLY);
  write(fd, p, sizeof(uint32_t) * 3);
  write(fd, msg, strlen(msg));
  close(fd);
  free (p);

  return 0;
}
