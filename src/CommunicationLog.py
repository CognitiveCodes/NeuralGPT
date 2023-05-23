class CommunicationLog:
    def __init__(self):
        self.logs = []

    def add_log(self, message, timestamp, error=None):
        log = {
            'message': message,
            'timestamp': timestamp,
            'error': error
        }
        self.logs.append(log)

    def get_logs(self):
        return self.logs