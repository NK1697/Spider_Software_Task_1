CC=afl-clang-fast
CFLAGS=-O2 -fno-omit-frame-pointer
LIBS=-lxml2
INCLUDES=-I/usr/include/libxml2

TARGET=fuzz_xml

all:
	$(CC) $(CFLAGS) fuzz_xml.c -o $(TARGET) $(INCLUDES) $(LIBS)

clean:
	rm -f $(TARGET)