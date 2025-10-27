from pdfminer.high_level import extract_text
import re
import pandas as pd
from nameparser import HumanName
from tqdm import tqdm
from pathlib import Path
import os


class PdfChairExtractor:
    """
    Extrahiert ERC Panel-Mitglieder (z. B. Panel Chairs) aus PDF-Dokumenten 
    und konvertiert sie in eine strukturierte Pandas DataFrame.

    Diese Klasse wurde speziell für ERC-Panellisten wie 
    „ERC-2024-AdG-panel-members.pdf“ oder 
    „Panel_Chairs_ERC_Starting_Grant_2026.pdf“ entwickelt. 
    Sie erkennt automatisch Domains (PE, LS, SH), Panels (z. B. PE1 Mathematics),
    und ordnet die Namen der Professor:innen (Chairs) zu.

    Ablauf:
        1. Extrahiert Textinhalte aus der PDF mit pdfminer.
        2. Identifiziert ERC-Domains und zugehörige Panelcodes.
        3. Extrahiert Professorennamen (beginnend mit „Prof.“).
        4. Erstellt eine DataFrame mit den Spalten:
           ['Lastname', 'Forename', 'Subdomain', 'Type', 'ERC-Date', 'Panel'].

    Beispiel:
        >>> extractor = PdfChairExtractor()
        >>> df = extractor.extract_text(
        ...     pdf_path="../data/Panel_Chairs_ERC_Starting_Grant_2026.pdf",
        ...     print_cmd=True,
        ...     save_csv=True
        ... )
        >>> print(df.head())

    Erwartete Ausgabe:
        Lastname | Forename   | Subdomain          | Type  | ERC-Date
        ----------|------------|--------------------|-------|----------
        van de Geer | Sara     | Mathematics (PE1)  | Chair | 2024
        Bouscaren  | Elisabeth | Mathematics (PE1)  | Chair | 2024
    """

    def __init__(self):
        
        pass
       

    def extract_text(self, pdf_path:str=None, 
                     print_cmd:bool=False, 
                     save_csv:bool=False,
                     output_path:str="../data/output/"
                     ) -> pd.DataFrame:
        """
        Liest eine ERC Panel PDF-Datei ein, extrahiert Text und erstellt 
        eine strukturierte DataFrame-Tabelle mit Panel Chairs.

        Diese Methode ist optimiert für das typische ERC-Layout:
        ```
        PE1 Mathematics
        Prof. Name1
        Prof. Name2
        ...
        PE2 Physics
        Prof. Name3
        ```
        
        Ablauf:
            - Identifiziert die ERC-Domain (PE, LS, SH)
            - Extrahiert alle Panels und deren Namen
            - Liest die Namen der Panel Chairs („Prof. ...“)
            - Ordnet sie dem jeweiligen Panel zu
            - Gibt eine strukturierte Pandas DataFrame zurück

        Args:
            pdf_path (str): 
                Pfad zur zu verarbeitenden PDF-Datei.
            print_cmd (bool, optional): 
                Wenn True, werden Debug-Informationen und Vorschauen der Ergebnisse ausgegeben. 
                Standard: False.
            save_csv (bool, optional): 
                Wenn True, wird die extrahierte Tabelle als CSV im angegebenen Output-Ordner gespeichert. 
                Standard: False.
            output_path (str, optional): 
                Zielordner für die Ausgabe der CSV-Datei. 
                Standard: "../data/output/".

        Returns:
            pd.DataFrame: 
                Eine DataFrame mit den Spalten:
                - 'Lastname': Nachname der Person
                - 'Forename': Vorname der Person
                - 'Subdomain': Panelname inkl. Code (z. B. "Mathematics (PE1)")
                - 'Type': Position im Panel (z. B. "Chair")
                - 'ERC-Date': Jahr der ERC-Publikation (z. B. "2026")
                - 'Panel': Nur der Panelcode (z. B. "PE1")

        Raises:
            FileNotFoundError: Wenn die angegebene PDF-Datei nicht existiert.
            ValueError: Wenn kein Panel oder keine Chair-Einträge gefunden werden.

        Hinweise:
            - Diese Implementierung geht davon aus, dass alle Namen mit „Prof.“ beginnen.
            - Panels müssen mit „PE“, „LS“ oder „SH“ gekennzeichnet sein.
        """

        text = extract_text(pdf_path)
        #if print_cmd:
            #print(text)
        
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        results = []
        current_domain = None
        current_subdomain = None
        release_date = None
        erc_date = None
        panel_list = []  # Liste aller Panel-Codes und Namen

        # Phase 1: Sammle alle Panels
        for line in lines:
            # Domain erkennen
            if "PHYSICAL SCIENCES AND ENGINEERING" in line or "PHYSICAL SCIENCES & ENGINEERING" in line:
                current_domain = "PE"
                continue
            elif "LIFE SCIENCES" in line:
                current_domain = "LS"
                continue
            elif "SOCIAL SCIENCES" in line:
                current_domain = "SH"
                continue

            # Panel-Code und Name (z.B. "PE1 Mathematics")
            panel_match = re.match(r'^(PE|LS|SH)(\d+)\s+(.+)$', line)
            if panel_match and current_domain:
                code = panel_match.group(1) + panel_match.group(2)
                name = panel_match.group(3).strip()
                panel_list.append({
                    'code': code,
                    'name': f"{name} ({code})",
                    'domain': current_domain
                })
                continue

            # Extract release date
            date_match = re.search(r"Release date: (\d{2}/\d{2}/\d{4})", line)
            if date_match and not release_date:
                release_date = date_match.group(1)

            # Extract ERC year
            erc_date_match = re.search(r"ERC-(\d{4})", line)
            if erc_date_match and not erc_date:
                erc_date = erc_date_match.group(1)

        if print_cmd:
            print(f"\nFound {len(panel_list)} panels")
            print(f"ERC Date: {erc_date}")
            print(f"Release Date: {release_date}")

        # Phase 2: Extrahiere Professoren und ordne sie Panels zu
        # Jeder Prof. gehört zum nächsten Panel in der Liste
        panel_idx = 0
        for line in lines:
            # Überspringe Header/Footer/Metadaten
            if any(skip in line for skip in ['ERC Starting Grant', 'Panel Chairs', 'Release date', 
                                              'Helpdesk', 'Contact Points', 'transparency', 
                                              'confidentiality', 'Questions']):
                continue
            
            # Überspringe Domain-Header
            if line in ['PHYSICAL SCIENCES AND ENGINEERING', 'PHYSICAL SCIENCES & ENGINEERING',
                       'LIFE SCIENCES', 'SOCIAL SCIENCES & HUMANITIES', 
                       'SOCIAL SCIENCES AND HUMANITIES']:
                continue
            
            # Überspringe Panel-Definitionen (erkannt in Phase 1)
            if re.match(r'^(PE|LS|SH)\d+\s+', line):
                continue
            
            # Professor gefunden
            if line.startswith('Prof.'):
                name = line.replace('Prof.', '').strip()
                
                # Zuordnung zum aktuellen Panel
                if panel_idx < len(panel_list):
                    panel = panel_list[panel_idx]
                    
                    # Split name: Erstes Wort = Lastname, Rest = Forename
                    name_parts = name.split(' ', 1)
                    if len(name_parts) == 2:
                        lastname = name_parts[0]
                        forename = name_parts[1]
                    else:
                        lastname = name
                        forename = ""
                    
                    results.append({
                        "Lastname": lastname,
                        "Forename": forename,
                        "Subdomain": panel['name'],
                        "Type": "Chair",
                        "ERC-Date": erc_date
                    })
                    
                    panel_idx += 1

        df = pd.DataFrame(results)

        df['Panel'] = df['Subdomain'].str.split('(').str[-1].str.rstrip(')')

        if print_cmd:
            print("\n" + "="*80)
            print(f"Extracted {len(df)} Panel Chairs")
            print("="*80)
            print(df.head(10))
            print("...")
            print(df.tail(10))

        if save_csv:
            os.makedirs(output_path, exist_ok=True)
            output_name = f"ERC_{erc_date}_panel_chairs.csv" if erc_date else "ERC_panel_chairs.csv"
            output_file = Path(output_path).joinpath(output_name)
            print(f"\nSaving DataFrame to {output_file}")
            df.to_csv(output_file, index=False)

        return df
    




if __name__ == "__main__":

    pdf_path = "../data/Panel_Members_ERC_Advanced_Grants_2023.pdf"
    extractor = PdfChairExtractor()
    df = extractor.extract_text(pdf_path=pdf_path, print_cmd=True, save_csv=True)
