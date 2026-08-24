import ollama


class Ollama_Embedder(Embedder, embed_model="ollama_embedder"):
    def __init__(self, embed_model):
        pass
    def embed(self, text: str):
        response = ollama.embed(
                model="nomic-embed-text",
                input=text
            )
