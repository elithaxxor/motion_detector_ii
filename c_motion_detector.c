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
#include "sftp_upload.h"
#include "mqtt_publish.h"
#include "roi_select.h"
#include "daemon_utils.h"

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
    char upload_method[16];
    char upload_url[MAX_PATH];
    char sftp_host[MAX_PATH];
    char sftp_user[64];
    char sftp_pass[64];
    char sftp_remote_path[MAX_PATH];
    char mqtt_broker[MAX_PATH];
    char mqtt_topic[128];
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
        else if (strstr(line, "method")) sscanf(line, "method = %s", cfg->upload_method);
        else if (strstr(line, "url")) sscanf(line, "url = %s", cfg->upload_url);
        else if (strstr(line, "sftp_host")) sscanf(line, "sftp_host = %s", cfg->sftp_host);
        else if (strstr(line, "sftp_user")) sscanf(line, "sftp_user = %s", cfg->sftp_user);
        else if (strstr(line, "sftp_pass")) sscanf(line, "sftp_pass = %s", cfg->sftp_pass);
        else if (strstr(line, "sftp_remote_path")) sscanf(line, "sftp_remote_path = %s", cfg->sftp_remote_path);
        else if (strstr(line, "broker")) sscanf(line, "broker = %s", cfg->mqtt_broker);
        else if (strstr(line, "topic")) sscanf(line, "topic = %s", cfg->mqtt_topic);
    }
    fclose(f);
}

void *upload_thread(void *arg) {
    struct {
        char *file_path;
        struct Config *cfg;
    } *data = (decltype(data))arg;
    log_event("Uploading motion snapshot...");
    if (strcmp(data->cfg->upload_method, "sftp") == 0) {
        upload_file_sftp(data->file_path, data->cfg->sftp_host, data->cfg->sftp_user, data->cfg->sftp_pass, data->cfg->sftp_remote_path);
    } else {
        upload_file_http(data->file_path, data->cfg->upload_url);
    }
    remove(data->file_path);
    free(data->file_path);
    free(data);
    pthread_exit(NULL);
}

int main(int argc, char** argv) {
    int daemon_mode = 0;
    const char *pidfile = "/tmp/c_motion_detector.pid";
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--daemon") == 0) daemon_mode = 1;
    }
    if (daemon_mode) daemonize(pidfile);
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    struct Config cfg = {800, 25, 0, "0", "", "http", "http://example.com/upload", "", "", "", "", "localhost", "motion"};
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
    cv::Rect roi;
    if (strlen(cfg.roi) == 0 && !headless) {
        cap.read(frame);
        roi = select_roi(frame);
        snprintf(cfg.roi, sizeof(cfg.roi), "%d,%d,%d,%d", roi.x, roi.y, roi.width, roi.height);
    } else if (strlen(cfg.roi) > 0) {
        int x, y, w, h;
        sscanf(cfg.roi, "%d,%d,%d,%d", &x, &y, &w, &h);
        roi = cv::Rect(x, y, w, h);
    }
    while (running) {
        if (!cap.read(frame)) break;
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
        cv::GaussianBlur(gray, blur, cv::Size(21, 21), 0);
        cv::Mat roi_blur = blur;
        if (roi.area() > 0) roi_blur = blur(roi);
        if (first || reset_reference) {
            roi_blur.copyTo(firstFrame);
            first = false;
            reset_reference = 0;
            log_event("Reference frame reset.");
            continue;
        }
        cv::absdiff(firstFrame, roi_blur, frameDelta);
        cv::threshold(frameDelta, thresh, threshold, 255, cv::THRESH_BINARY);
        cv::dilate(thresh, thresh, cv::Mat(), cv::Point(-1, -1), 2);
        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(thresh, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
        int motion = 0;
        for (size_t i = 0; i < contours.size(); i++) {
            if (cv::contourArea(contours[i]) > min_area) {
                cv::Rect box = cv::boundingRect(contours[i]);
                if (roi.area() > 0) {
                    box.x += roi.x; box.y += roi.y;
                }
                cv::rectangle(frame, box, cv::Scalar(0, 255, 0), 2);
                motion = 1;
            }
        }
        if (motion) {
            log_event("Motion detected!");
            char *snap_name = (char*)malloc(64);
            snprintf(snap_name, 64, "motion_%ld.jpg", time(NULL));
            cv::imwrite(snap_name, frame);
            publish_motion_event(cfg.mqtt_broker, cfg.mqtt_topic, "motion detected");
            auto *data = (decltype(data))malloc(sizeof(*data));
            data->file_path = snap_name;
            data->cfg = &cfg;
            pthread_t tid;
            pthread_create(&tid, NULL, upload_thread, data);
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
