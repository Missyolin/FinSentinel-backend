from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from scraper import discover_entities, build_training_data
from model import train_model, predict_entity
from data_store import save_data, get_data

import threading 
import time

global_data = []

app = FastAPI()

print("Training model...")

entities = discover_entities()
texts, labels = build_training_data(entities)

# 🔥 tambah data dari user feedback
stored = get_data()
if stored:
    texts.extend([d["text"] for d in stored])
    labels.extend([d["label"] for d in stored])

model, vectorizer = train_model(texts, labels)

print("Model ready!")
global_data = discover_entities()
print("INIT DATA:", len(global_data))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "FinSentinel API running"}


@app.get("/discover")
def discover():
    global global_data

    data = global_data  # 🔥 pakai yang sama

    results = []

    for item in data:
        score = predict_entity(item, model, vectorizer)

        if score >= 0.7:
            label = "ILLEGAL"
        elif score >= 0.4:
            label = "SUSPICIOUS"
        else:
            label = "LOW"

        results.append({
            "name": item["name"],
            "source": item["source"],
            "label": label,
            "risk": round(score * 100, 2),
            "evidence_count": len(item["texts"]),
            "evidence": item["texts"],
            "timestamp": datetime.now().isoformat()
        })

    results.sort(key=lambda x: x["risk"], reverse=True)

    return {
        "total_discovered": len(results),
        "entities": results
    }


@app.get("/summary")
def summary():
    global global_data

    data = global_data

    illegal, suspicious, low = 0, 0, 0

    for item in data:
        score = predict_entity(item, model, vectorizer)

        if score >= 0.7:
            illegal += 1
        elif score >= 0.4:
            suspicious += 1
        else:
            low += 1

    return {
        "total": len(data),
        "illegal": illegal,
        "suspicious": suspicious,
        "low": low
    }


@app.get("/alerts")
def alerts():
    global global_data

    data = global_data

    alerts = []  # 🔥 TAMBAH INI

    for item in data:
        score = predict_entity(item, model, vectorizer)

        if score >= 0.7:
            alerts.append({
                "name": item["name"],
                "source": item["source"],
                "risk": round(score * 100, 2),
                "evidence_count": len(item["texts"])
            })

    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }

def auto_refresh():
    global global_data
    while True:
        time.sleep(15)
        global_data = discover_entities()
        print("DATA REFRESHED:", len(global_data))

threading.Thread(target=auto_refresh, daemon=True).start()