#include "license.h"
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define MAX_SIZE 65536

static uint32_t crc32(const uint8_t *data, size_t size)
{
    uint32_t crc = 0xFFFFFFFF;

    for (size_t i = 0; i < size; i++) {
        crc ^= data[i];

        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^
                  (0xEDB88320 & (-(crc & 1)));
        }
    }

    return ~crc;
}

static void sanitize(uint8_t *buf, size_t len)
{
    if (len < 8)
        return;

    /* Fix version */
    buf[4] = 0x01;
    buf[5] = 0x00;

    /* Keep flags mostly intact */
    buf[6] &= 0x7F;

    size_t off = 8;

    while (off + 3 <= len) {

        uint16_t chunk_len =
            ((uint16_t)buf[off + 1] << 8) |
            buf[off + 2];

        /* Fix absurd lengths */
        if (chunk_len > 1024) {
            chunk_len = 1024;

            buf[off + 1] = (chunk_len >> 8) & 0xff;
            buf[off + 2] = chunk_len & 0xff;
        }

        /* Repair lengths that would run past EOF */
        if (off + 3 + chunk_len > len) {

            chunk_len = (uint16_t)(len - off - 3);

            buf[off + 1] = (chunk_len >> 8) & 0xff;
            buf[off + 2] = chunk_len & 0xff;
        }

        if (chunk_len == 0)
            break;

        off += 3 + chunk_len;
    }
}

int main(int argc, char **argv)
{
    if (argc < 2)
        return 0;

    FILE *f = fopen(argv[1], "rb");
    if (!f)
        return 0;

    uint8_t buf[MAX_SIZE];

    size_t len = fread(buf, 1, sizeof(buf), f);

    fclose(f);

    if (len < 8)
        return 0;

    sanitize(buf, len);

    /* Repair CRC after all mutations */
    uint32_t crc = crc32(buf + 4, len - 4);

    buf[0] = (crc >> 24) & 0xff;
    buf[1] = (crc >> 16) & 0xff;
    buf[2] = (crc >> 8) & 0xff;
    buf[3] = crc & 0xff;

    if (!init_license_system())
        return 0;

    validate_license(buf, len);

    cleanup_license_system();

    return 0;
}