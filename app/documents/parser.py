import re

def parse_12th_marksheet(text: str):
    """
    Parse 12th marksheet text extracted from OCR.
    Returns structured data that will be stored in the profile.
    """
    if not text:
        return {}
    t = text.upper()

    data = {
        "board": None,
        "year": None,
        "total_marks": None,
        "max_marks": 500,
        "percentage": None,
        "result": None,
        "division": None,
    }

    # Board
    if "UTTAR PRADESH" in t or "UP BOARD" in t:
        data["board"] = "UP Board"

    # Year
    elif "CBSE" in t:
        data["board"] = "CBSE"
    elif "ICSE" in t:
        data["board"] = "ICSE"
    elif "BIHAR" in t:
        data["board"] = "Bihar Board"
    year_match = re.search(r"20\d{2}", t)
    if year_match:
        data["year"] = int(year_match.group())

    # Total marks
    total_match = re.search(r"(\d{3})\s*/\s*(\d{3})", t)
    if total_match:
        data["total_marks"] = int(total_match.group(1))
        
        max_marks = int(total_match.group(2))
        data["max_marks"] = max_marks
        data["percentage"] = round((data["total_marks"] / max_marks) * 100, 2)

    if not data["percentage"]:
        perc_match = re.search(r"(\d{2}\.\d{1,2})\s*%", t)
        if perc_match:
            data["percentage"] = float(perc_match.group(1))
    
    if "PASSED" in t or "PASS" in t:
        data["result"] = "PASSED"
    elif "FAILED" in t or "FAIL" in t:
        data["result"] = "FAILED"

    # Division
    if "FIRST" in t:
        data["division"] = "FIRST"
    elif "SECOND" in t:
        data["division"] = "SECOND"
    elif "THIRD" in t:
        data["division"] = "THIRD"

    print(f"DEBUG - Parsed marksheet data: {data}")
    return data
