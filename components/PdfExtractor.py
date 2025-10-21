from pdfminer.high_level import extract_text
import re
import pandas as pd
from nameparser import HumanName
from tqdm import tqdm
from pathlib import Path
import os


class PdfExtractor:
    """
    Eine Klasse zum Extrahieren und Strukturieren von ERC Panel-Mitgliedern 
    aus PDF-Dokumenten mithilfe von pdfminer.

    Die Klasse liest PDF-Dateien (z. B. 'ERC-2024-AdG-panel-members.pdf'), 
    extrahiert relevante Textinformationen und erstellt daraus eine 
    strukturierte Tabelle mit Domain, Subdomain, Vorname, Nachname, 
    vollständigem Namen und Position (Chair oder Member).
    """

    def __init__(self):
        pass
       

    def extract_text(self, pdf_path:str=None, 
                     print_cmd:bool=False, 
                     save_csv:bool=False,
                     output_path:str="../data/"
                     ) -> pd.DataFrame:
        """
        Extrahiert Text aus einer ERC Panel Members PDF-Datei und konvertiert 
        ihn in eine strukturierte Pandas DataFrame-Tabelle mit den Spalten:
        Domain, Subdomain, Forename, Lastname, Fullname und Type (Chair/Member).

        Der Algorithmus:
        - Liest den gesamten Text aus dem PDF mit `pdfminer`.
        - Erkennt automatisch Domains (PE, LS, SH) und zugehörige Subdomains.
        - Identifiziert Panel Chairs und Mitglieder (Members).
        - Bereinigt den Text von irrelevanten Zeilen (z. B. Seitenzahlen oder Metadaten).
        - Gibt die extrahierten Daten als DataFrame zurück.
        - Optional: Speichert das Ergebnis als CSV-Datei.

        Args:
            pdf_path (str, optional): 
                Pfad zur PDF-Datei, aus der der Text extrahiert werden soll. 
                Beispiel: "../data/ERC-2024-AdG-panel-members.pdf".
                Defaults to None.
            print_cmd (bool, optional): 
                Wenn True, werden Zwischenergebnisse (bereinigte Zeilen, 
                Filter-Vorschau etc.) in der Konsole angezeigt.
                Defaults to False.
            save_csv (bool, optional): 
                Wenn True, wird die bereinigte Tabelle als CSV-Datei gespeichert.
                Defaults to False.
            output_path (str, optional): 
                Pfad zum Zielordner für die CSV-Datei.
                Defaults to "../data/".

        Returns:
            pd.DataFrame:
                DataFrame mit folgenden Spalten:
                - **Domain** (str): Hauptbereich (PE, LS oder SH)
                - **Subdomain** (str): Unterbereich, z. B. "Mathematics (PE1)"
                - **Forename** (str): Vorname der Person
                - **Lastname** (str): Nachname der Person
                - **Fullname** (str): Vollständiger Name (wie im PDF)
                - **Type** (str): "Chair" oder "Member"

        Example:
            >>> extractor = PdfExtractor()
            >>> df = extractor.extract_text(
            ...     pdf_path="../data/ERC-2024-AdG-panel-members.pdf",
            ...     print_cmd=True,
            ...     save_csv=True
            ... )
            >>> print(df.head())

        Output Example:
                Forename     Lastname           Fullname           Type
            0       Sara  van de Geer   Sara van de Geer          Chair
            1  Elisabeth     Bouscaren  Elisabeth Bouscaren       Member
            2      Lucia      Caporaso       Lucia Caporaso       Member
            3 Alessandra      Celletti  Alessandra Celletti      Member
        """

        text = extract_text(pdf_path)
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        results = []
        current_domain = None
        current_subdomain = None
        release_date = None
        erc_date = None
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

            # extract the release date from ERC-2024-AdG Panel Members List – Release date: 18/09/2025 – p.8/8
            date_match = re.search(r"Release date: (\d{2}/\d{2}/\d{4})", line)
            if date_match and not release_date:
                release_date = date_match.group(1)

            # extract the ERC-date from ERC-2024-AdG Panel Members List – Release date: 18/09/2025 – p.8/8
            erc_date_match = re.search(r"ERC-(\d{4})", line)
            if erc_date_match and not erc_date:
                erc_date = erc_date_match.group(1)

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
        if print_cmd:
            print("\n", "##########"*5, "Removing the following rows:", "##########"*5)
            print(df[bad_mask].loc[:, ['Forename', 'Lastname', 'Fullname', 'Type']])

        # tatsächliches Entfernen
        df = df[~bad_mask].reset_index(drop=True)

        # Testausgabe
        df_filter = df.loc[:, ['Forename', 'Lastname', 'Fullname', 'Type']]
        if print_cmd:
            print("\n", "##########"*5, "Filtered Dataframe:", "##########"*5)
            print(df_filter.head(20))
            print(df_filter.tail(20))

        if save_csv:
            os.makedirs(output_path, exist_ok=True) # make sure output directory exists

            output_name = f"ERC_{erc_date}_panel_members_chairs.csv" if erc_date else "ERC_panel_members_chairs.csv"
            # save as CSV
            output_path = Path("../data").joinpath(output_name)
            print(f"\nSaving filtered DataFrame to {output_path}")
            df_filter.to_csv(output_path, index=False)

        return df_filter
    




if __name__ == "__main__":

    pdf_path = "../data/ERC-2024-AdG-panel-members.pdf"
    extractor = PdfExtractor()
    df = extractor.extract_text(pdf_path=pdf_path, print_cmd=True, save_csv=True)
