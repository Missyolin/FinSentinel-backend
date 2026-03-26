data_log = []


def save_data(text, label):
    data_log.append({
        "text": text,
        "label": label
    })


def get_data():
    return data_log