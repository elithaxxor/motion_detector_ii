// Minimal C prototype for motion detection using OpenCV
// Now with integration, usability, and performance features
// Compile with: make
#include <opencv2/opencv.hpp>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <signal.h>
#include "http_upload.h"

#define CONFIG_FILE "config.ini"
#define LOG_FILE "motion.log"
#define MAX_PATH 512

// Global flags for hotkeys and threads
volatile int running = 1;
volatile int save_snapshot = 0;
volatile int reset_reference = 0;

void handle_signal(int sig) { running = 0; }

void log_event(const char *msg) {
    FILE *f = fopen(LOG_FILE, "a");
    if (f) {
        fprintf(f, "%s\n", msg);
        fclose(f);
    }
}

// Config struct
struct Config {
    int min_area;
    int threshold;
    int headless;
    char input[MAX_PATH];
    char roi[64];
    char upload_url[MAX_PATH];
};

void load_config(struct Config *cfg) {
    FILE *f = fopen(CONFIG_FILE, "r");
    if (!f) return;
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strstr(line, "min_area")) sscanf(line, "min_area = %d", &cfg->min_area);
        else if (strstr(line, "threshold")) sscanf(line, "threshold = %d", &cfg->threshold);
        else if (strstr(line, "headless")) sscanf(line, "headless = %d", &cfg->headless);
        else if (strstr(line, "input")) sscanf(line, "input = %s", cfg->input);
        else if (strstr(line, "roi")) sscanf(line, "roi = %s", cfg->roi);
        else if (strstr(line, "url")) sscanf(line, "url = %s", cfg->upload_url);
    }
    fclose(f);
}

void *upload_thread(void *arg) {
    char *file_path = (char *)arg;
    log_event("Uploading motion snapshot...");
    upload_file_http(file_path, "http://example.com/upload"); // Replace with config if needed
    remove(file_path);
    free(file_path);
    pthread_exit(NULL);
}

int main(int argc, char** argv) {
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    struct Config cfg = {800, 25, 0, "0", "", "http://example.com/upload"};
    load_config(&cfg);
    int min_area = cfg.min_area;
    int threshold = cfg.threshold;
    int headless = cfg.headless;
    char *input = cfg.input;
    cv::VideoCapture cap;
    if (argc > 1 && argv[1][0] != '-') {
        cap.open(argv[1]);
    } else if (strcmp(input, "0") == 0) {
        cap.open(0);
    } else {
        cap.open(input);
    }
    if (!cap.isOpened()) {
        printf("[ERROR] Could not open video source.\n");
        log_event("Could not open video source.");
        return -1;
    }
    cv::Mat frame, gray, blur, firstFrame, frameDelta, thresh;
    bool first = true;
    while (running) {
        if (!cap.read(frame)) break;
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
        cv::GaussianBlur(gray, blur, cv::Size(21, 21), 0);
        if (first || reset_reference) {
            blur.copyTo(firstFrame);
            first = false;
            reset_reference = 0;
            log_event("Reference frame reset.");
            continue;
        }
        cv::absdiff(firstFrame, blur, frameDelta);
        cv::threshold(frameDelta, thresh, threshold, 255, cv::THRESH_BINARY);
        cv::dilate(thresh, thresh, cv::Mat(), cv::Point(-1, -1), 2);
        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(thresh, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
        int motion = 0;
        for (size_t i = 0; i < contours.size(); i++) {
            if (cv::contourArea(contours[i]) > min_area) {
                cv::Rect box = cv::boundingRect(contours[i]);
                cv::rectangle(frame, box, cv::Scalar(0, 255, 0), 2);
                motion = 1;
            }
        }
        if (motion) {
            log_event("Motion detected!");
            char *snap_name = (char*)malloc(64);
            snprintf(snap_name, 64, "motion_%ld.jpg", time(NULL));
            cv::imwrite(snap_name, frame);
            pthread_t tid;
            pthread_create(&tid, NULL, upload_thread, snap_name);
            pthread_detach(tid);
        }
        if (!headless) {
            cv::imshow("Motion Detection", frame);
            int key = cv::waitKey(30);
            if (key == 'q') running = 0;
            else if (key == 's') save_snapshot = 1;
            else if (key == 'r') reset_reference = 1;
        }
        if (save_snapshot) {
            char fname[64];
            snprintf(fname, 64, "snapshot_%ld.jpg", time(NULL));
            cv::imwrite(fname, frame);
            log_event("Snapshot saved.");
            save_snapshot = 0;
        }
    }
    cap.release();
    cv::destroyAllWindows();
    log_event("Motion detector stopped.");
    return 0;
}
