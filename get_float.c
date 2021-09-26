#include <stdio.h>

float get_float(void* buf, int pos) {
    printf("buf: %p, pos: %d\n", buf, pos);
    return *((float*)(buf) + pos);
}
