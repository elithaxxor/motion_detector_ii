import os
from ftplib import FTP
try:
    import paramiko
except ImportError:
    paramiko = None

def upload_via_ftp(local_path, remote_filename=None, log_path=None, retries=2):
    """
    Upload a file to an FTP or SFTP server using environment variables for configuration.
    Optionally log the result to a log file.
    """
    from dotenv import load_dotenv
    import time
    load_dotenv()
    host = os.getenv('FTP_HOST')
    port = int(os.getenv('FTP_PORT', 21))
    user = os.getenv('FTP_USER')
    passwd = os.getenv('FTP_PASS')
    remote_dir = os.getenv('FTP_REMOTE_DIR', '/')
    use_sftp = os.getenv('FTP_USE_SFTP', 'false').lower() == 'true'

    if not remote_filename:
        remote_filename = os.path.basename(local_path)

    attempt = 0
    while attempt <= retries:
        try:
            if use_sftp:
                if paramiko is None:
                    raise ImportError("paramiko is required for SFTP support. Please install it via 'pip install paramiko'.")
                transport = paramiko.Transport((host, port if port else 22))
                transport.connect(username=user, password=passwd)
                sftp = paramiko.SFTPClient.from_transport(transport)
                try:
                    sftp.chdir(remote_dir)
                except IOError:
                    sftp.mkdir(remote_dir)
                    sftp.chdir(remote_dir)
                sftp.put(local_path, os.path.join(remote_dir, remote_filename))
                sftp.close()
                transport.close()
            else:
                ftp = FTP()
                ftp.connect(host, port)
                ftp.login(user, passwd)
                try:
                    ftp.cwd(remote_dir)
                except Exception:
                    ftp.mkd(remote_dir)
                    ftp.cwd(remote_dir)
                with open(local_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_filename}', f)
                ftp.quit()
            msg = f"[FTP_UPLOAD] {time.strftime('%Y-%m-%d %H:%M:%S')} SUCCESS {local_path} -> {remote_filename}"
            if log_path:
                with open(log_path, 'a') as logf:
                    logf.write(msg + '\n')
            return True
        except Exception as e:
            msg = f"[FTP_UPLOAD] {time.strftime('%Y-%m-%d %H:%M:%S')} FAIL {local_path} -> {remote_filename} : {e}"
            if log_path:
                with open(log_path, 'a') as logf:
                    logf.write(msg + '\n')
            if attempt == retries:
                raise
            time.sleep(2)
            attempt += 1
    return False
