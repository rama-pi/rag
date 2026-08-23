import os, sys, json, re, string
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import importlib

from framework.base_classes import Model, Retriever
from framework.helpers import remove_unwanted, discover


config = {
    "wanted_model": "llama3.2",
    "wanted_mode" : "stream",
    "history_file": "history.json",
    "conversation_size": 10,
    "search_type" : "re",
}

def load_config():
    global config
    try:
        with open("config.json", 'r') as cf:
            config = json.load(cf)
    except FileNotFoundError:
        with open("config.json", 'w') as cf:
            json.dump(config, cf, indent=4)
        print("""
              No configuration file found.
              Created config.json using default settings.
              Please review the file and run the program again.
              """)
        sys.exit(1)
    except:
        print(f"An error occurred:")
        sys.exit(1)

class ConversationBuilder():
    def __init__(self, retriever):
        self.retriever = retriever
    def build(self, history, question, last):
        temp_list = []
        messages = []
        hist_sorted = dict(sorted(history.items()))
        for k,v in hist_sorted.items():
            score = self.retriever.retrieve(" ".join((v["question"], v["answer"])), question)
            if score and score["score"]:
                temp_list.append((k, v, score["score"]))
        temp_list.sort(key=lambda item: item[2])
        new_hist = {k:v for k,v,s in temp_list}
        if new_hist:
            for v in list(new_hist.values())[-last:]:
                messages.append({"role":"user", "content":v['question']})
                messages.append({"role":"assistant", "content":v['answer']})
        messages.append({"role":"user", "content":question})
        return messages


#The Agent owns memory.
#The Model owns intelligence.
#The Agent constructs context.
#The Model reasons over that context.
class Agent():
    #stateful (remember past)
    def __init__(self,model):
        self.model = model
        self.history = {}
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self._load_history()
        self._build_cache()
        cls =  Retriever.registry.get(config['search_type'])
        if cls:
            retriever = Retriever.registry.get(config['search_type'])(cls.retriever_name)
        if retriever:
            self.conv_builder = ConversationBuilder(retriever)
        else:
            raise Exception("wanted search type not found")
    def ask(self,question: str):
        if question in self.cache:
            # full match
            self.cache_hits += 1
            print(self.cache[question])
            return
        else:
            self.cache_misses += 1
            # try part match
            part_question_match = self._find_similar_questions(question)
            if part_question_match:
                print("\n Found these from earlier ask \n")
                for q in part_question_match:
                    print(q)
                return
        conv = self.conv_builder.build(self.history, question, config["conversation_size"])
        answer = self.model.ask(conv)
        self.history[datetime.now().isoformat()]={'question': question, 'answer': answer}
        self._save_history()
        self.cache[question] = answer
        return answer
    def _save_history(self):
        with open(config["history_file"], "w") as f:
            json.dump(self.history,f,indent=4)
    def _load_history(self):
        try:
            with open(config["history_file"], "r") as f:
                self.history = json.load(f)
        except FileNotFoundError:
            pass
    def _build_cache(self):
        for v in self.history.values():
            self.cache[v['question']] = v['answer']
    def _find_similar_questions(self, question):
        similar_questions = []
        for k in self.cache.keys():
            if re.search(re.escape(question), k, re.IGNORECASE):
                similar_questions.append(k)
        return similar_questions
    def show_history(self):
        for k,v in self.history.items():
            print(f"{k} {v['question']} {v['answer']}")
    def show_stats(self):
        print(f"Cache hits: {self.cache_hits} Cache misses: {self.cache_misses}")


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

    load_config()
    model =  Model.registry.get(config["wanted_model"])
    if not model:
        raise Exception("wanted model not found")
    mode = config["wanted_mode"]
    if mode not in model.model_modes:
        raise Exception("wanted mode not found")

    m = model(config["wanted_model"], config["wanted_mode"])
    a = Agent(m)
    a.ask("Explain slicing.?")
    a.ask("what is ndarray?")
    a.ask("give me another example and put a marker like %%%%%")
    a.ask("Explain difference between ndarray indexing and slicing.?")
    a.ask("Explain ndarray indexing.?")
    a.ask(" ndarray")
    a.ask("what major events happened in 1947")
    a.ask(" give me RE example")
    a.ask(" how long a moon spens in each Nakshatra")
    a.ask(" not 13 days and 20 hours rather it is 13 degress 20 minutes, please correct your previous answer")

    a.show_stats()
    '''
    #a.show_history()
    '''

if __name__ == "__main__":
    main()

