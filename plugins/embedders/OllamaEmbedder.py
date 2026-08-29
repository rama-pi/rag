import os, sys, json, re, string
from datetime import datetime

from framework.base_classes import Embedder
import ollama


class Ollama_Embedder(Embedder, embed_model="nomic-embed-text"):
    def __init__(self, embed_model):
        pass
    def embed(self, chunks: list):
        response = ollama.embed(
                model="nomic-embed-text",
                input=chunks
            )
        return response
