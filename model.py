import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text


RED_FLAGS = [
    "tanpa ktp",
    "akses kontak",
    "debt collector",
    "bunga tinggi",
    "pinjol ilegal",
    "tanpa bi checking",
    "langsung cair"
]


def keyword_boost(text):
    boost = 0
    for k in RED_FLAGS:
        if k in text:
            boost += 0.15
    return min(boost, 0.4)


def train_model(texts, labels):
    texts = [preprocess(t) for t in texts]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=3000,
        min_df=2
    )

    X = vectorizer.fit_transform(texts)

    model = LogisticRegression(
        class_weight='balanced',
        max_iter=1000
    )

    model.fit(X, labels)

    return model, vectorizer


def predict_text(text, model, vectorizer):
    clean = preprocess(text)
    X = vectorizer.transform([clean])

    prob = model.predict_proba(X)[0][1]
    prob += keyword_boost(clean)

    return min(prob, 1.0)


def predict_entity(entity, model, vectorizer):
    scores = []

    for text in entity["texts"]:
        scores.append(predict_text(text, model, vectorizer))

    return sum(scores) / len(scores) if scores else 0