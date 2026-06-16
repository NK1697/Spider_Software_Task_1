#include <json-c/json.h>
#include <unistd.h>

#define MAX 8192

int main() {
    char buf[MAX];

    while (__AFL_LOOP(1000)) {
        ssize_t len = read(0, buf, MAX - 1);
        if (len <= 0) continue;

        buf[len] = '\0';

        struct json_object *obj = json_tokener_parse(buf);
        if (obj) json_object_put(obj);
    }
}