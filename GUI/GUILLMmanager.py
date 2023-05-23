import os
import subprocess
import threading

class LLMManager:
    def __init__(self):
        self.llm_list = []
        self.current_llm = None
        self.llm_thread = None

    def add_llm(self, llm_path):
        if os.path.exists(llm_path):
            self.llm_list.append(llm_path)

    def remove_llm(self, llm_path):
        if llm_path in self.llm_list:
            self.llm_list.remove(llm_path)

    def list_llms(self):
        return self.llm_list

    def set_current_llm(self, llm_path):
        if llm_path in self.llm_list:
            self.current_llm = llm_path

    def start_llm(self):
        if self.current_llm is not None:
            self.llm_thread = threading.Thread(target=self._run_llm)
            self.llm_thread.start()

    def stop_llm(self):
        if self.llm_thread is not None:
            self.llm_thread.stop()

    def _run_llm(self):
        subprocess.call([self.current_llm])

    def get_llm_status(self):
        if self.llm_thread is not None:
            return self.llm_thread.is_alive()
        else:
            return False