CC=gcc
CFLAGS=`pkg-config --cflags opencv4 libcurl`
LDFLAGS=`pkg-config --libs opencv4 libcurl`

SRC=c_motion_detector.c http_upload.c
OBJ=$(SRC:.c=.o)

all: c_motion_detector

c_motion_detector: $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f *.o c_motion_detector
