CC=g++
CFLAGS=`pkg-config --cflags opencv4 libcurl` -pthread
LDFLAGS=`pkg-config --libs opencv4 libcurl` -pthread

SRC=c_motion_detector.c http_upload.c sftp_upload.c mqtt_publish.c roi_select.cpp daemon_utils.c
OBJ=$(SRC:.c=.o)
OBJ+=$(SRC:.cpp=.o)

all: c_motion_detector

c_motion_detector: $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f *.o c_motion_detector
