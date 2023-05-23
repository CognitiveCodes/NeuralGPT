import time
import requests

class Communication:
  def __init__(self, protocol, message_format, timeout, retry_limit):
    self.protocol = protocol
    self.message_format = message_format
    self.timeout = timeout
    self.retry_limit = retry_limit

  def send_message(self, message):
    retries = 0
    while retries < self.retry_limit:
      try:
        response = requests.post(self.protocol, data=message, timeout=self.timeout)
        return response
      except requests.exceptions.Timeout:
        retries += 1
        print("Timeout occurred. Retrying...")
        time.sleep(1)
      except requests.exceptions.RequestException as e:
        print("Error occurred: ", e)
        break
    return None

  def receive_message(self):
    retries = 0
    while retries < self.retry_limit:
      try:
        response = requests.get(self.protocol, timeout=self.timeout)
        return response
      except requests.exceptions.Timeout:
        retries += 1
        print("Timeout occurred. Retrying...")
        time.sleep(1)
      except requests.exceptions.RequestException as e:
        print("Error occurred: ", e)
        break
    return None
