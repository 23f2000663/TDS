import re
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentimentRequest(BaseModel):
    sentences: List[str]


happy_words = {
    "love", "loved", "lovely", "like", "liked", "enjoy", "enjoyed",
    "happy", "happier", "happiest", "great", "good", "excellent",
    "amazing", "awesome", "wonderful", "fantastic", "best", "perfect",
    "excited", "glad", "delighted", "pleased", "joy", "joyful",
    "satisfied", "brilliant", "nice", "fun", "smile", "smiling",
    "success", "successful", "win", "winning", "beautiful",
    "positive", "impressive", "recommend", "recommended", "favorite",
    "favourite", "outstanding", "superb", "enjoyable", "cheerful",
    "thrilled", "grateful", "thankful", "comforting", "delicious"
}

sad_words = {
    "sad", "unhappy", "terrible", "bad", "awful", "hate", "hated",
    "horrible", "worst", "angry", "upset", "disappointed",
    "disappointing", "pain", "painful", "poor", "broken", "annoying",
    "depressed", "depressing", "miserable", "frustrated", "frustrating",
    "failure", "fail", "failed", "losing", "lost", "cry", "crying",
    "sorry", "regret", "regretful", "dislike", "disliked", "boring",
    "sucks", "suck", "useless", "waste", "problem", "problems",
    "negative", "disaster", "disastrous", "unpleasant", "annoyed",
    "furious", "heartbroken", "lonely", "worried", "worry", "fear",
    "scared", "disgusting", "disgusted", "difficult", "damaged",
    "slow", "rude", "refund", "complaint"
}

happy_phrases = {
    "very happy",
    "so happy",
    "really happy",
    "really good",
    "really great",
    "very good",
    "very great",
    "love it",
    "love this",
    "made my day",
    "highly recommend",
    "works perfectly",
    "works great",
    "very satisfied",
    "couldn't be happier",
    "could not be happier",
    "exceeded my expectations"
}

sad_phrases = {
    "very sad",
    "so sad",
    "really sad",
    "really bad",
    "really terrible",
    "hate it",
    "hate this",
    "not good",
    "not happy",
    "not satisfied",
    "very disappointed",
    "waste of money",
    "doesn't work",
    "does not work",
    "didn't work",
    "did not work",
    "never works",
    "poor quality",
    "very poor",
    "not worth",
    "do not recommend",
    "don't recommend"
}


def classify_sentiment(text: str) -> str:
    t = text.lower().strip()

    # Strong phrase matches first
    for phrase in sad_phrases:
        if phrase in t:
            return "sad"

    for phrase in happy_phrases:
        if phrase in t:
            return "happy"

    # Extract words
    words = re.findall(r"[a-z']+", t)

    happy_score = 0
    sad_score = 0

    for word in words:
        if word in happy_words:
            happy_score += 1
        if word in sad_words:
            sad_score += 1

    # Handle basic negation
    negations = {"not", "never", "no", "don't", "dont", "didn't", "didnt"}

    for i in range(len(words) - 1):
        if words[i] in negations:
            next_word = words[i + 1]

            if next_word in happy_words:
                happy_score -= 1
                sad_score += 2

            if next_word in sad_words:
                sad_score -= 1
                happy_score += 1

    if happy_score > sad_score:
        return "happy"

    if sad_score > happy_score:
        return "sad"

    return "neutral"


@app.post("/sentiment")
def sentiment(request: SentimentRequest):
    return {
        "results": [
            {
                "sentence": sentence,
                "sentiment": classify_sentiment(sentence)
            }
            for sentence in request.sentences
        ]
    }


@app.get("/")
def home():
    return {"status": "ok"}