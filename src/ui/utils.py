import json

def load_highscores(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    
    return sorted(data, key=lambda entry: entry["score"], reverse=True)

def ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = "TH"
    else:
        suffix = {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")
    return f"{n}{suffix}"

def save_highscores(filepath, pseudo, score):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append({"pseudo": pseudo, "score": score})

    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)