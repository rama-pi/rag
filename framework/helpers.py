import os, sys, json, re, string
import importlib
from pathlib import Path

ignore_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "of",
        "to",
        "for",
        "in",
        "on",
        "at",
        "what",
        "how",
        "why",
        "explain",
        "give"
        }

def remove_unwanted(past_q, curr_q):
    # normalize whitespaces
    past_q = " ".join(past_q.split())
    curr_q = " ".join(curr_q.split())
    # lowercase, remove punctuation
    past_q_w = {w.strip(string.punctuation) for w in past_q.lower().split()}
    curr_q_w = {w.strip(string.punctuation) for w in curr_q.lower().split()}
    # remove stop words
    past_q_w = {w for w in past_q_w if w not in ignore_words}
    curr_q_w = {w for w in curr_q_w if w not in ignore_words}
    # return lists of words
    return (past_q_w, curr_q_w)

"""
    Dynamically loads all Python modules in a given plugins subfolder.
    Example: discover("plugins/models")
"""
def discover(plugin_subfolder: str):
    # 1. Convert the folder path to a proper path object relative to project root
    base_path = Path(plugin_subfolder)
    if not base_path.exists():
        print(f"[Framework Warning] Plugin directory {plugin_subfolder} not found.")
        return

    # 2. Convert the folder path structure to a Python module path notation
    # e.g., "plugins/models" becomes "plugins.models"
    package_prefix = plugin_subfolder.replace("/", ".").strip(".")

    # 3. Iterate over every entry in the directory
    for entry in os.listdir(base_path):
        # Skip hidden files (like .DS_Store), private files (__init__.py), and directories
        if entry.startswith('.') or entry.startswith('__') or not entry.endswith('.py'):
            continue

        # Strip the '.py' extension to get the module name
        module_file_name = entry[:-3]

        # Construct the absolute import module path string (e.g., "plugins.models.llama_model")
        full_module_name = f"{package_prefix}.{module_file_name}"

        try:
            print(f"[Framework] Dynamically loading plugin: {full_module_name}")
            # The python equivalent of a dynamic dlopen()
            importlib.import_module(full_module_name)
        except Exception as e:
            print(f"[Framework Error] Failed to load plugin {full_module_name}: {e}")



