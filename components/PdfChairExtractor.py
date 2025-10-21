from pdfminer.high_level import extract_text
import re
import pandas as pd
from nameparser import HumanName
from tqdm import tqdm
from pathlib import Path
import os


class PdfChairExtractor:
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
                     output_path:str="../data/output/"
                     ) -> pd.DataFrame:
        """
        Extrahiert Text aus einer ERC Panel Chairs PDF-Datei und konvertiert 
        ihn in eine strukturierte Pandas DataFrame-Tabelle.

        Dieser Extractor ist speziell für PDFs im Format:
        "PE1 Mathematics
         Prof. Name1
         Prof. Name2"
        
        Args:
            pdf_path (str): Pfad zur PDF-Datei
            print_cmd (bool): Debug-Ausgaben anzeigen
            save_csv (bool): Ergebnis als CSV speichern
            output_path (str): Zielordner für CSV

        Returns:
            pd.DataFrame mit Spalten: Lastname, Forename, Subdomain, Type, ERC-Date
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

    pdf_path = "../data/Panel_Chairs_ERC_Starting_Grant_2026.pdf"
    extractor = PdfChairExtractor()
    df = extractor.extract_text(pdf_path=pdf_path, print_cmd=True, save_csv=True)
