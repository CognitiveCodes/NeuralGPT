class DualCoreLLM:
    def __init__(self, logical_LLM, direct_LLM):
        self.logical_LLM = logical_LLM
        self.direct_LLM = direct_LLM

    def think(self, input_data):
        return self.logical_LLM.process(input_data)

    def execute(self, input_data):
        return self.direct_LLM.process(input_data)