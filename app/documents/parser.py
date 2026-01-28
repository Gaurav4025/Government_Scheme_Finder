import re

def parse_12th_marksheet(text: str):
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
    if "UTTAR PRADESH" in t:
        data["board"] = "UP Board"

    # Year
    year_match = re.search(r"20\d{2}", t)
    if year_match:
        data["year"] = int(year_match.group())

    # Total marks
    total_match = re.search(r"(\d{3})\s*/\s*500", t)
    if total_match:
        data["total_marks"] = int(total_match.group(1))
        data["percentage"] = round((data["total_marks"] / 500) * 100, 2)

    # Result
    if "PASSED" in t:
        data["result"] = "PASSED"

    # Division
    if "FIRST" in t:
        data["division"] = "FIRST"
    elif "SECOND" in t:
        data["division"] = "SECOND"
    elif "THIRD" in t:
        data["division"] = "THIRD"

    return data
