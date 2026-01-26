import easyocr
reader = easyocr.Reader(["en"])

def extract_text(path):
    result = reader.readtext(path)
    return " ".join([r[1] for r in result])
