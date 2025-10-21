# This Script extracts the panel members and chairs from the given PDF and saves them into a DataFrame


from pdfminer.high_level import extract_text
import re
import pandas as pd
from nameparser import HumanName
from tqdm import tqdm


pdf_path = "../data/ERC-2024-AdG-panel-members.pdf"

text = extract_text(pdf_path)

lines = [l.strip() for l in text.split("\n") if l.strip()]

results = []
current_domain = None
current_subdomain = None
subdomain_queue = []

for line in tqdm(lines, desc='Processing', total=len(lines)):
    # Domain
    if "PHYSICAL SCIENCES AND ENGINEERING" in line:
        current_domain = "PE"
        continue
    elif "LIFE SCIENCES" in line:
        current_domain = "LS"
        continue
    elif "SOCIAL SCIENCES AND HUMANITIES" in line:
        current_domain = "SH"
        continue

    # Subdomain(s) erkennen (inkl. geschlossener Klammer)
    sub_matches = re.findall(r"([A-Za-z ,:'\-&]+?\((?:PE|LS|SH)\d+\))", line)
    if sub_matches:
        for sm in sub_matches:
            subdomain_queue.append(sm.strip())
        continue

    # Personen
    if "(Panel Chair)" in line:
        if subdomain_queue:
            current_subdomain = subdomain_queue.pop(0)
        name = line.replace("(Panel Chair)", "").strip()
        ptype = "Chair"
    else:
        name = line.strip()
        ptype = "Member"

    if current_domain and current_subdomain and name:
        hn = HumanName(name)
        results.append({
            "Domain": current_domain,
            "Subdomain": current_subdomain,
            "Forename": hn.first,
            "Lastname": hn.last,
            "Fullname": name,
            "Type": ptype
        })

df = pd.DataFrame(results)

# entferne Reihen, deren Fullname "ERC-" oder Seitenangaben wie "p.8/8" (oder generell "p.<num>/<num>") enthält
bad_mask = df['Fullname'].str.contains(r'ERC-|p\.\s*\d+/\d+', case=False, na=False, regex=True)

# optional: anzeigen, was entfernt würde
print("\n", "##########"*5, "Removing the following rows:", "##########"*5)
print(df[bad_mask].loc[:, ['Forename', 'Lastname', 'Fullname', 'Type']])

# tatsächliches Entfernen
df = df[~bad_mask].reset_index(drop=True)

# Testausgabe
df_filter = df.loc[:, ['Forename', 'Lastname', 'Fullname', 'Type']]
print("\n", "##########"*5, "Filtered Dataframe:", "##########"*5)
print(df_filter.head(20))
print(df_filter.tail(20))
# save as CSV
df.to_csv("../data/ERC_2024_panel_members_chairs.csv", index=False)

