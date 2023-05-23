import ftplib

class FileTransfer:
    def __init__(self, ftp_host, ftp_user, ftp_password):
        self.ftp_host = ftp_host
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password

    def upload_file(self, local_file_path, remote_file_path):
        with ftplib.FTP(self.ftp_host, self.ftp_user, self.ftp_password) as ftp:
            with open(local_file_path, 'rb') as f:
                ftp.storbinary('STOR ' + remote_file_path, f)

    def download_file(self, remote_file_path, local_file_path):
        with ftplib.FTP(self.ftp_host, self.ftp_user, self.ftp_password) as ftp:
            with open(local_file_path, 'wb') as f:
                ftp.retrbinary('RETR ' + remote_file_path, f.write)