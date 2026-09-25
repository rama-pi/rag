from framework.base_classes import PreProcessor
from framework.helpers import remove_unwanted


class Pre_Processor(PreProcessor, preprocessor_type="preprocess"):
    def __init__(self, preprocessor_type):
        pass
    def preprocess(self, chunk: str):
        return remove_unwanted(chunk)

