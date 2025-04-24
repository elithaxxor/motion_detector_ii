// ROI selection using OpenCV mouse callback
#include "roi_select.h"
#include <opencv2/opencv.hpp>

static cv::Rect roi_rect;
static bool drawing = false;
static cv::Point pt1, pt2;

void mouse_callback(int event, int x, int y, int, void*) {
    if (event == cv::EVENT_LBUTTONDOWN) {
        drawing = true;
        pt1 = cv::Point(x, y);
        pt2 = pt1;
    } else if (event == cv::EVENT_MOUSEMOVE && drawing) {
        pt2 = cv::Point(x, y);
    } else if (event == cv::EVENT_LBUTTONUP) {
        drawing = false;
        pt2 = cv::Point(x, y);
        roi_rect = cv::Rect(pt1, pt2);
    }
}

cv::Rect select_roi(cv::Mat &frame) {
    roi_rect = cv::Rect();
    cv::namedWindow("Select ROI");
    cv::setMouseCallback("Select ROI", mouse_callback);
    cv::Mat temp;
    while (true) {
        frame.copyTo(temp);
        if (drawing)
            cv::rectangle(temp, pt1, pt2, cv::Scalar(0,255,0), 2);
        cv::imshow("Select ROI", temp);
        int key = cv::waitKey(30);
        if (!drawing && roi_rect.area() > 0) break;
        if (key == 27) break; // ESC
    }
    cv::destroyWindow("Select ROI");
    return roi_rect;
}
