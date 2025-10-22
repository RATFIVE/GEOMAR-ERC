from pdfminer.high_level import extract_text
import re
import pandas as pd
from nameparser import HumanName
from tqdm import tqdm
from pathlib import Path
import os
import re
from collections import defaultdict


pdf_path = "../data/ERC-2024-AdG-panel-members.pdf"
text = extract_text(pdf_path)
lines = [l.strip() for l in text.split("\n") if l.strip()]
#print(lines)  # Debug: show first 10 lines


# Regex für Chair-Zeile
chair_pattern = re.compile(r'^(.*) \(Panel Chair\)$')

# Ergebnisliste
rows = []
current_chair = None

for line in lines:
    line = line.strip()
    if not line:
        continue

    chair_match = chair_pattern.match(line)
    if chair_match:
        current_chair = chair_match.group(1)
    elif current_chair and not line.endswith(')'):  # keine neue Section oder Panel
        rows.append({'Chair': current_chair, 'Member': line})

# DataFrame erstellen
df = pd.DataFrame(rows)

# Ausgabe
print(df)

print(df['Chair'].unique())  # Einzigartige Chairs anzeigen




