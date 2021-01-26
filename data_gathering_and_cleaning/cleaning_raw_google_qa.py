import json
from io import StringIO
from html.parser import HTMLParser
from nltk.tokenize.treebank import TreebankWordDetokenizer
import nltk
from timeit import default_timer as timer
import random

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def update_timer(last_update_time, counter, max_counter=None, start_time=None, runtime=None):
    now = timer()

    # If last update was less than {float}s ago, dont update
    if now-last_update_time < 0.25:
        return last_update_time
    
    if start_time and max_counter:
        seconds_left = ((now - start_time)/counter)*(max_counter-counter)
        hours = int(seconds_left / 3600)
        minutes = int((seconds_left/60) % 60)
        seconds = int(seconds_left%60)
        print(f'Done: {counter:,}/{max_counter:,} iterations, finishing in: {hours:02d}:{minutes:02d}:{seconds:02d}.', end="\r")

    elif start_time and runtime:
        seconds_left = max(runtime - (now - start_time), 0)
        hours = int(seconds_left / 3600)
        minutes = int((seconds_left/60) % 60)
        seconds = int(seconds_left%60)
        print(f'Done: {counter:,} iterations, finishing in: {hours:02d}:{minutes:02d}:{seconds:02d}.', end='\r')
    else:
        print(f'Done: {counter:,}/{max_counter:,} iterations')

    return now

def clean_text(text):
    # Remove html tags
    text_without_tags = strip_tags(text)
    # Tokenize (the text still has spaces in wrong places e.G " didn ' t ")
    tokenized = nltk.word_tokenize(text_without_tags)
    # Detokenize
    detokenized = TreebankWordDetokenizer().detokenize(tokenized)

    return detokenized

def extract_from_json(obj):
    question = obj["question_text"]
    text = obj["document_text"]
    
    # Long answer
    # Annotator chosen answer exists
    if obj["annotations"][0]["long_answer"]["candidate_index"] != -1:
        long_start_token = obj["annotations"][0]["long_answer"]["start_token"]
        long_end_token = obj["annotations"][0]["long_answer"]["end_token"]
    
    # Annotator has marked that question has no answer: choose random paragraph
    else:
        top_level_candidates = [o for o in obj["long_answer_candidates"] if o["top_level"]]
        # Top level answers are preferred (ones that are not contained in other answers)
        if len(top_level_candidates) > 0:
            canditate = random.choice(top_level_candidates)
        else:
            canditate = random.choice(obj["long_answer_candidates"])
        
        long_start_token = canditate["start_token"]
        long_end_token = canditate["end_token"]


    long_answer = " ".join(text.split(" ")[long_start_token:long_end_token])
    long_answer = clean_text(long_answer)

    # Short answer
    short_answers = obj["annotations"][0]["short_answers"]
    short_answer = ""
    if len(short_answers) > 0:
        short_start_token = short_answers[0]["start_token"]
        short_end_token = short_answers[0]["end_token"]
        short_answer = " ".join(text.split(" ")[short_start_token:short_end_token])
        short_answer = clean_text(short_answer)

    # Yes_no_answer
    yes_no_answer = obj["annotations"][0]["yes_no_answer"]

    new_obj = {
        "question": question,
        "long_answer": long_answer,
        "short_answer": short_answer,
        "yes_no_answer": yes_no_answer
    }

    return new_obj

filename = "data/simplified-nq-train.jsonl"
results = []

counter = 0
print("Hakkan avama")
with open(filename, "r", encoding="utf-8") as f:
    print("Avamine õnnestus")
    
    start_time = timer()
    last_update_time = timer()
    
    for line in f:
        obj = json.loads(line)
        new_obj = extract_from_json(obj)
        
        results.append(new_obj)
        
        last_update_time = update_timer(last_update_time, counter, max_counter=307373, start_time=start_time)
        counter += 1
        
print()

with open('data/google_qa_cleaned.json','w') as f:
    json.dump(results,f)

print("Lõpetasin")
