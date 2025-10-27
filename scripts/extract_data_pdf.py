
from components.PdfMemberExtractor import PdfMemberExtractor
import pandas as pd



extractor = PdfMemberExtractor()
df_pdf = extractor.extract(pdf_path="../data/ERC-2025-StG-panel-members.pdf")
df_pdf['ERC-Date'] = df_pdf['ERC-Date'].astype(int)
erc_date = int(df_pdf['ERC-Date'].unique()[0])

print("\n##########"*5)
print("PDF DataFrame:")
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

# print only the rows where year == erc_date
df_excel = df_excel[df_excel['year'] == erc_date]

# strip whitespace from Name column
df_excel['Name'] = df_excel['Name'].str.strip()


print("\n##########"*5)
print("PDF DataFrame:")
print(df_excel.head())


for chair in df_pdf['Chair'].unique():
    df_pdf_chair = df_pdf[df_pdf['Chair'] == chair]
    chair_review_panel = df_excel.loc[df_excel['Name'] == chair]['review_panel'].values[0]
    df_pdf.loc[df_pdf['Chair'] == chair, 'review_panel'] = chair_review_panel

for chair in df_pdf['Chair'].unique():
    df_pdf_chair = df_pdf[df_pdf['Chair'] == chair]
    print(df_pdf_chair)


df_pdf = df_pdf.melt(
    id_vars=['ERC-Date', 'review_panel'],
    value_vars=['Chair', 'Member'],
    var_name='function',
    value_name='name'
)

df_pdf['function'] = df_pdf['function'].str.lower()        # "chair" / "member"
df_pdf['name'] = df_pdf['name'].astype(str).str.strip()
df_pdf = df_pdf[df_pdf['name'] != ''].reset_index(drop=True)

# Spalten umbenennen / anordnen

df_pdf = df_pdf[['name', 'function', 'ERC-Date', 'review_panel']]
df_pdf = df_pdf.drop_duplicates().reset_index(drop=True)




df_merged = pd.merge(df_pdf, df_excel, left_on='name', right_on='Name', how='left', indicator=True, suffixes=('_pdf', '_excel'))

funding_scheme_name = df_merged.loc[df_merged["funding_scheme"].notnull()]["funding_scheme"].unique()[0]

# fill NaN in funding_scheme with the unique value
df_merged['funding_scheme'] = df_merged['funding_scheme'].fillna(funding_scheme_name)




df = df_merged.loc[:, ['name', 'function', "ERC-Date", "review_panel_pdf", "funding_scheme"]].rename(columns={"review_panel_pdf": "panel", "ERC-Date": "year"})
df["call"] = df["funding_scheme"] + " " + df["year"].astype(str)

# get from panel the first word (e.g "PE1" -> "PE")
df["domain"] = df["panel"].str.split().str[0].str[:-1]

df.drop(columns=["year", "funding_scheme"], inplace=True)


# split name into first_name and last_name
df[['first name', 'last name']] = df['name'].str.rsplit(' ', n=1, expand=True)
df.drop(columns=['name'], inplace=True)

print("\n##########"*5)
print("Merged Dataframe:")
print(df.head())


