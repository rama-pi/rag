import os, sys, json, re, string
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
import pdfplumber
from pdfplumber.page import Page as pdfPage

from framework.base_classes import Loader
from framework.base_classes import Page

class PdfLoader(Loader, loader_type="pdf"):
    def __init__(self, loader_type):
        pass
    def load(self, file_path: str | Path) -> dict:
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for pg in pdf.pages:
                page = Page()
                page.page_number = pg.page_number
                page.width       = pg.width
                page.height      = pg.height
                page.rotation    = pg.rotation
                page.words   = pg.extract_words()
                page.text    = pg.extract_text()
                page.images  = None
                page.tables  = pg.extract_tables()
                page.annotations = pg.annots
                page.metadata = pdf.metadata
                for img_meta in pg.images:
                    # pg.images is a list of metadata dictionaries
                    for img_meta in pg.images:
                        # Crop the page view strictly down to the image boundarie
                        cropped_page = pg.crop((img_meta["x0"],
                                                img_meta["top"],
                                                img_meta["x1"],
                                                img_meta["bottom"]
                                                )
                                               )
                        # Render the cropped view into a high-res PNG object
                        rendered_image = cropped_page.to_image(resolution=150)
                        page.images.append(rendered_image)
                pages.append(page)
        return pages

