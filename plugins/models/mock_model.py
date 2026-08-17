from abc import ABC, abstractmethod

'''
from model import Model
'''
from framework.base_classes import Model

class MockModel(Model, model_name="mock", model_modes=['None']):
# model adapter 
    #stateless
    def __init__(self):
        pass
    def ask(self, messages):
        return f"I have been asked a topic {question}, working on it FYI i am {self.model_name} model"
