CC=g++
CFLAGS=`pkg-config --cflags opencv4 libcurl` -pthread
LDFLAGS=`pkg-config --libs opencv4 libcurl` -pthread

SRC=YOLO_EMBEDDED/c_motion_detector.c YOLO_EMBEDDED/http_upload.c YOLO_EMBEDDED/sftp_upload.c YOLO_EMBEDDED/mqtt_publish.c YOLO_EMBEDDED/roi_select.cpp YOLO_EMBEDDED/daemon_utils.c
OBJ=$(SRC:.c=.o)
OBJ+=$(SRC:.cpp=.o)

all: c_motion_detector

c_motion_detector: $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f YOLO_EMBEDDED/*.o c_motion_detector
