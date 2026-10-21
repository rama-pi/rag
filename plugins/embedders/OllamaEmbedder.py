import os, sys, json, re, string
from datetime import datetime

from framework.base_classes import Embedder
import ollama


class Ollama_Embedder(Embedder, embed_model="nomic-embed-text"):
    def __init__(self, embed_model):
        pass
    def embed(self, chunk: str):
        response = ollama.embed(
                model="nomic-embed-text",
                input=chunk
            )

        if not response.embeddings or not response.embeddings[0]:
            raise ValueError(
                    f"Ollama returned an empty embedding for chunk: {chunk!r}"
                    )
        return response
