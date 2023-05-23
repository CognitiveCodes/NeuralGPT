import os
import requests

class LLM:
    def __init__(self, name, bin_file_path):
        self.name = name
        self.bin_file_path = bin_file_path

class LLMManager:
    def __init__(self, local_storage_path):
        self.local_storage_path = local_storage_path
        self.llms = []
    
    def add_llm(self, llm):
        self.llms.append(llm)
    
    def remove_llm(self, llm_name):
        for llm in self.llms:
            if llm.name == llm_name:
                self.llms.remove(llm)
    
    def download_llm(self, url):
        response = requests.get(url)
        llm_name = os.path.basename(url)
        llm_file_path = os.path.join(self.local_storage_path, llm_name)
        with open(llm_file_path, 'wb') as f:
            f.write(response.content)
        llm = LLM(llm_name, llm_file_path)
        self.add_llm(llm)
    
    def upload_llm(self, llm_file_path):
        llm_name = os.path.basename(llm_file_path)
        llm = LLM(llm_name, llm_file_path)
        self.add_llm(llm)
    
    def connect_llm(self, llm_name):
        for llm in self.llms:
            if llm.name == llm_name:
                # connect the llm
                pass
    
    def disconnect_llm(self, llm_name):
        for llm in self.llms:
            if llm.name == llm_name:
                # disconnect the llm
                pass