// Minimal C prototype for motion detection using OpenCV
// Compile with: gcc c_motion_detector.c -o c_motion_detector `pkg-config --cflags --libs opencv4`
#include <opencv2/opencv.hpp>
#include <stdio.h>

int main(int argc, char** argv) {
    cv::VideoCapture cap;
    if (argc > 1) {
        cap.open(argv[1]); // Open video file
    } else {
        cap.open(0); // Open default camera
    }
    if (!cap.isOpened()) {
        printf("[ERROR] Could not open video source.\n");
        return -1;
    }
    cv::Mat frame, gray, blur, firstFrame, frameDelta, thresh;
    bool first = true;
    while (true) {
        if (!cap.read(frame)) break;
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
        cv::GaussianBlur(gray, blur, cv::Size(21, 21), 0);
        if (first) {
            blur.copyTo(firstFrame);
            first = false;
            continue;
        }
        cv::absdiff(firstFrame, blur, frameDelta);
        cv::threshold(frameDelta, thresh, 25, 255, cv::THRESH_BINARY);
        cv::dilate(thresh, thresh, cv::Mat(), cv::Point(-1, -1), 2);
        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(thresh, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
        for (size_t i = 0; i < contours.size(); i++) {
            if (cv::contourArea(contours[i]) > 800) {
                cv::Rect box = cv::boundingRect(contours[i]);
                cv::rectangle(frame, box, cv::Scalar(0, 255, 0), 2);
            }
        }
        cv::imshow("Motion Detection", frame);
        if (cv::waitKey(30) == 27) break; // ESC to quit
    }
    cap.release();
    cv::destroyAllWindows();
    return 0;
}
