import os, sys, json, re, string
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import importlib

from framework.test_classes import Test
from framework.helpers import remove_unwanted, discover



# Main
#user / Composition Root / Main
def main():
    #discover plugins
    discover("plugins/models/")
    discover("plugins/documents/")
    discover("plugins/loaders/")
    discover("plugins/parsers/")
    discover("plugins/retrievers/")
    discover("plugins/chunkers/")
    discover("plugins/preprocessors/")

    discover("plugins_tests/retrievers/")

    for v in Test.registry.values():
        t = v()
        t.test()

if __name__ == "__main__":
    main()


