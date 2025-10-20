import pdfplumber
import re
from pprint import pprint
import pandas as pd

# Read data from pdf

pdf_file = '../data/ERC-2024-AdG-panel-members.pdf'







print("\n\n--- Alternative Methode mit pdfplumber ---\n\n")



# PDF öffnen
with pdfplumber.open(pdf_file) as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"

# Regex: Bereich + Name
pattern = r"(PE\d+|LS\d+|SH\d+)\s+(.*?)\s+Prof\.\s+(.+)"
matches = re.findall(pattern, text)

results = []
for code, field, name in matches:
    if code.startswith("PE"):
        domain = "PHYSICAL SCIENCES AND ENGINEERING"
    elif code.startswith("LS"):
        domain = "LIFE SCIENCES"
    else:
        domain = "SOCIAL SCIENCES AND HUMANITIES"
    results.append({
        "Code": code,
        "Field": field.strip(),
        "Name": name.strip(),
        "Domain": domain
    })

# Ausgabe
# for r in results:
#     pprint(r)

# convert to dataframe

df = pd.DataFrame(results)
pprint(df)