// Simple HTTP file upload using libcurl
#include "http_upload.h"
#include <curl/curl.h>
#include <stdio.h>

int upload_file_http(const char *file_path, const char *url) {
    CURL *curl;
    CURLcode res;
    FILE *fd = fopen(file_path, "rb");
    if (!fd) {
        fprintf(stderr, "Failed to open file %s\n", file_path);
        return 0;
    }
    curl = curl_easy_init();
    if (!curl) {
        fclose(fd);
        fprintf(stderr, "Failed to init curl\n");
        return 0;
    }
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);
    curl_easy_setopt(curl, CURLOPT_READDATA, fd);
    curl_easy_setopt(curl, CURLOPT_INFILESIZE_LARGE, (curl_off_t)0); // autodetect size
    res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    fclose(fd);
    if (res != CURLE_OK) {
        fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        return 0;
    }
    return 1;
}
