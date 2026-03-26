import requests
from bs4 import BeautifulSoup
import random

ILLEGAL_PATTERNS = [
    "pinjaman tanpa ktp",
    "tanpa bi checking",
    "langsung cair 5 menit",
    "akses kontak pengguna",
    "debt collector kasar",
    "bunga sangat tinggi",
    "penagihan ancaman",
    "pinjol ilegal"
]

LEGAL_PATTERNS = [
    "terdaftar OJK",
    "pinjaman resmi bank",
    "bunga transparan",
    "bunga rendah",
    "aman dan terpercaya",
    "proses sesuai regulasi"
]


def add_noise(text):
    variations = [
        text,
        text.lower(),
        text.upper(),
        text + "!!!",
        text.replace("a", "@").replace("i", "1"),
    ]
    return random.choice(variations)


def scrape_news():
    url = "https://example.com"

    try:
        res = requests.get(url, timeout=2)  # 🔥 lebih cepat
        soup = BeautifulSoup(res.text, "html.parser")

        texts = [p.text.strip() for p in soup.find_all("p")[:5] if p.text.strip()]

        return [{
            "name": "News Entity",
            "texts": texts,
            "source": "news",
            "label": None
        }]

    except Exception:
        return []


def scrape_social_simulation():
    base_data = [
        ("DanaCepat", 0),
        ("UangNow", 1),
        ("NetizenPost", 1),
        ("PinjamYuk", 1),
        ("DanaAman", 0),
    ]

    data = []

    for name, is_illegal in base_data:
        patterns = ILLEGAL_PATTERNS if is_illegal else LEGAL_PATTERNS
        texts = [add_noise(t) for t in random.sample(patterns, 3)]

        data.append({
            "name": name,
            "texts": texts,
            "source": "social_media",
            "label": is_illegal
        })

    return data


def scrape_app_simulation():
    data = []

    for i in range(5):
        is_illegal = random.random() > 0.5
        patterns = ILLEGAL_PATTERNS if is_illegal else LEGAL_PATTERNS
        texts = [add_noise(t) for t in random.sample(patterns, 3)]

        data.append({
            "name": f"App_{i}",
            "texts": texts,
            "source": "app_store",
            "label": 1 if is_illegal else 0
        })

    return data


def scrape_user_reports():
    data = []

    for i in range(5):
        texts = random.sample(ILLEGAL_PATTERNS, 3)

        data.append({
            "name": f"Reported_{i}",
            "texts": texts,
            "source": "user_reports",
            "label": 1
        })

    return data


def discover_entities():
    results = []
    results.extend(scrape_social_simulation())
    results.extend(scrape_app_simulation())
    results.extend(scrape_user_reports())
    # results.extend(scrape_news())

    if len(results) > 3:
        duplicate = random.choice(results)
        results.append(duplicate)

    random.shuffle(results)
    return results


def build_training_data(entities):
    texts = []
    labels = []

    for e in entities:
        if e.get("label") is None:
            continue

        for t in e["texts"]:
            texts.append(t)
            labels.append(e["label"])

    return texts, labels