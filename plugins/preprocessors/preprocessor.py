from framework.base_classes import PreProcessor
from framework.helpers import remove_unwanted


class Pre_Processor(PreProcessor, preprocessor_type="preprocess"):
    def __init__(self, preprocessor_type):
        pass
    def preprocess(self, chunk: str):
        t = remove_unwanted(chunk, "")
        # make str back
        s = " ".join(t[0])
        return s


