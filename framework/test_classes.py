from abc import ABC, abstractmethod
from pathlib import Path

class Test(ABC):
    registry = {}

    @abstractmethod
    def test(self):
        pass
    def __init_subclass__(cls, test_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.test_name = test_name
        Test.registry[test_name]=cls



