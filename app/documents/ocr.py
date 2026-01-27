import easyocr
from functools import lru_cache

@lru_cache(maxsize=1)
def get_reader():
    return easyocr.Reader(["en"], gpu=False)

def extract_text(image_path: str) -> str:
    reader = get_reader()
    results = reader.readtext(image_path)
    return " ".join(text for (_, text, _) in results)
