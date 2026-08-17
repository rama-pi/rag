import json
from abc import ABC, abstractmethod

from framework.base_classes import Parser
from framework.base_classes import Page

class PdfParser(Parser, parser_type="pdf"):
    def __init__(self, parser_type):
        pass
    @staticmethod
    def build_lines(page: Page):
        y = 0
        line = ''
        lines = {}
        for word in page.words:
            current_y = round(word['top'], 2)
            if y == 0:
                y = current_y
                line += word['text']
            elif y == current_y:
                line += " " + word['text']
            else:
                lines[y] = line.replace("(cid:127)", "•")
                y = current_y
                line = word['text']
        if line:
            lines[y] = line.replace("(cid:127)", "•")
        return lines
    @staticmethod
    def build_paras(page: Page):
        lines = PdfParser.build_lines(page)

        GAP_THRESHOLD = 20.0
        paras = []
        current_para = ""
        previous_y = None
        sorted_y = sorted(lines.keys())

        for y in sorted_y:
            line = lines[y]

            if previous_y is None:
                current_para = line
            else:
                gap = y - previous_y

                if gap > GAP_THRESHOLD:
                    paras.append(current_para)
                    current_para = line
                else:
                    current_para += " " + line
            previous_y = y

        if current_para:
            paras.append(current_para)
        return paras
    def parse_words(self, page:Page):
        return page.words
    def dump_words(self, page: Page):
        for word in page.words:
            print(word['text'])
    def parse_lines(self, words_list: list):
        return PdfParser.build_lines(page)
    def dump_lines(self, page: Page):
        lines = self.build_lines(page)
        js = json.dumps(lines, indent=4, sort_keys=True)
        print(js)
    def parse_paras(self, page:Page):
        return PdfParser.build_paras(page)
    def dump_paras(self, page:Page):
        paras = PdfParser.build_paras(page)
        for l in paras:
            print(f"{l}\n")
    def dump_pages(self, pages: list[Page]):
        for page in pages:
            print(page.page_number)


