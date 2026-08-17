import os, sys, json, re, string

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
    past_q_w = {w.strip(string.punctuation) for w in past_q.lower().split()}
    curr_q_w = {w.strip(string.punctuation) for w in curr_q.lower().split()}
    past_q_w = {w for w in past_q_w if w not in ignore_words}
    curr_q_w = {w for w in curr_q_w if w not in ignore_words}
    return (past_q_w, curr_q_w)

