#ifndef SFTP_UPLOAD_H
#define SFTP_UPLOAD_H

int upload_file_sftp(const char *file_path, const char *host, const char *user, const char *pass, const char *remote_path);

#endif // SFTP_UPLOAD_H
