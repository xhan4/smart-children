# db/mongodb.py
from pymongo import MongoClient
import yaml

def get_db():
    with open("config/config.yaml", "r", encoding="utf8") as f:
        config = yaml.safe_load(f)
    client = MongoClient(config["mongodb"]["uri"])
    db = client[config["mongodb"]["db_name"]]
    return db

def log_interaction(question: str, answer: str):
    db = get_db()
    db.interactions.insert_one({"question": question, "answer": answer})
