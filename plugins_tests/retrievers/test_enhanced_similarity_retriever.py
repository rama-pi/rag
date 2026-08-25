from framework.test_classes import Test
from framework.base_classes import Retriever

class test_enhanced_similarity_retriever(Test, test_name="test_enhanced_similarity_retriever"):
    def __init__(self, test_name="test_enhanced_similarity_retriever"):
        pass
    def test(self):
        er = Retriever.registry.get("enhanced_similarity_retriever")
        if er:
            er = er()
        else:
            raise Exception("enhanced_similarity_retriever is not registered")
        text1 = 'text code write test repro'
        text2 = 'prod code write test repro'
        print(er.retrieve(text1, text2))

