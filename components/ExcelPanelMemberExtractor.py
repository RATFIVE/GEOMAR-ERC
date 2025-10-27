import pandas as pd


class ExcelPanelMemberExtractor:
    """
    Extrahiert ERC Panel-Mitglieder aus einer Excel-Datei 
    und konvertiert sie in eine strukturierte Pandas DataFrame.

    Diese Klasse wurde speziell für die Excel-Datei 
    „panel-members-excel.xls“ entwickelt. 
    Sie liest die Datei ein und erstellt eine DataFrame mit den Spalten:
    ['Name', 'review_panel', 'year'].

    Beispiel:
        >>> extractor = ExcelPanelMemberExtractor()
        >>> df = extractor.extract(excel_path="../data/panel-members-excel.xls")
        >>> print(df.head())
    """

    def __init__(self):
        pass
       
    def extract(self, excel_path:str=None, year:int=None) -> pd.DataFrame:
        """
        Liest eine ERC Panel Excel-Datei ein und erstellt 
        eine strukturierte DataFrame-Tabelle mit Panel-Mitgliedern.

        Args:
            excel_path (str): Pfad zur Excel-Datei.

        Returns:
            pd.DataFrame: Eine DataFrame mit den Spalten:
            - 'Name': Name des Panel-Mitglieds
            - 'review_panel': Name des Review-Panels
            - 'year': Jahr der ERC-Publikation
        """

        # Read panel-members-excel.xls
        df_excel = pd.read_excel(excel_path, engine='openpyxl')

        # split column year at "," and copy the row for each year
        df_excel = df_excel.assign(year=df_excel['year'].astype(str).str.split(',')).explode('year')

        # strip whitespace und entferne leere/ungültige Einträge (nur 4-stellige Jahreszahlen)
        df_excel['year'] = df_excel['year'].str.strip()
        df_excel = df_excel[df_excel['year'].str.match(r'^\s*\d{4}\s*$', na=False)].copy()

        # year in int konvertieren
        df_excel['year'] = df_excel['year'].astype(int)

        # print only the rows where year == erc_date
        df_excel = df_excel[df_excel['year'] == year]

        # strip whitespace from Name column
        df_excel['Name'] = df_excel['Name'].str.strip()



        return df_excel
    
if __name__ == "__main__":
    extractor = ExcelPanelMemberExtractor()
    df = extractor.extract(excel_path="../data/panel-members-excel.xls", year=2024)