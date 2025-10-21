from components import PdfExtractor
import pandas as pd


extractor = PdfExtractor()
df_pdf = extractor.extract_text(pdf_path="../data/ERC-2024-AdG-panel-members.pdf")
df_pdf['ERC-Date'] = df_pdf['ERC-Date'].astype(int)
erc_date = int(df_pdf['ERC-Date'].unique()[0])
print(f"ERC Date: {erc_date}")
print(df_pdf.head())





# Read panel-members-excel.xls


excel_path = "../data/panel-members-excel.xls"

df_excel = pd.read_excel(excel_path, engine='openpyxl')

# split column year at "," and copy the row for each year
df_excel = df_excel.assign(year=df_excel['year'].astype(str).str.split(',')).explode('year')

# strip whitespace und entferne leere/ungültige Einträge (nur 4-stellige Jahreszahlen)
df_excel['year'] = df_excel['year'].str.strip()
df_excel = df_excel[df_excel['year'].str.match(r'^\s*\d{4}\s*$', na=False)].copy()

# year in int konvertieren
df_excel['year'] = df_excel['year'].astype(int)

print(df_excel.info())

# number of occurrences of each name
print(df_excel['Name'].value_counts())

# display only the rows where year == erc_date
df_excel = df_excel[df_excel['year'] == erc_date]

# strip whitespace from Name column
df_excel['Name'] = df_excel['Name'].str.strip()



print(df_excel.head())

df_merged = pd.merge(df_pdf, df_excel, left_on='Fullname', right_on='Name', how='outer', indicator=True)

print(df_merged.info())
print(df_merged.head(20))