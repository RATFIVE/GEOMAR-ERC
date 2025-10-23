from pdfminer.high_level import extract_text
import re
import pandas as pd
from nameparser import HumanName
from tqdm import tqdm
from pathlib import Path
import os
import re
from collections import defaultdict












class PdfMemberExtractor:
    
    def __init__(self):
        pass

    def filter_df(self, df:pd.DataFrame):

        filter_list = ['Biological', ' Biology', 'Physiology', 'Environment', 'Governance', 'Organisations', 'Biotechnology', 'Engineering', 
                       'ERC-', 'Chemistry', 'Communication', 'Synthetic', 'Materials', 'Systems', 'Computation', 'Informatics', 'Diagnosis',
                       'Infection', 'Diagnosis', 'Prevention', 'Neuroscience']
        
        for term in filter_list:
            df = df[~df['Member'].str.contains(term, na=False)]
        
        return df
    
    def check_misspelled_names(self, df:pd.DataFrame):
        # Correct e.g. FrankVerstraete to Frank Verstraete pattern
        df['Member'] = df['Member'].str.replace(r'([a-z])([A-Z])', r'\1 \2', regex=True) 
        return df
    
    def save_csv(self, df:pd.DataFrame, output_path:str, filename:str):
        # Ensure output directory exists
        Path(output_path).mkdir(parents=True, exist_ok=True)
        csv_path = os.path.join(output_path, filename)
        df.to_csv(csv_path, index=False)
        print(f"CSV saved to: {csv_path}")

    def extract(self, pdf_path:str=None, 
                     print_cmd:bool=False, 
                     save_csv:bool=False,
                     output_path:str="../data/output/"
                     ) -> pd.DataFrame:
        
        if not pdf_path:
            raise ValueError("pdf_path must be provided.")

        
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

            # finde the date in ERC-date format
            erc_date_match = re.search(r"ERC-(\d{4})", line)
            erc_date_list = []
            if erc_date_match:
                erc_date = erc_date_match.group(1)
                
                erc_date_list.append(erc_date)

        # DataFrame erstellen
        df = pd.DataFrame(rows)
        df['ERC-Date'] = erc_date_list[0] if erc_date_list else None

    
        df = self.filter_df(df)
        df = self.check_misspelled_names(df)

        # Ausgabe
        
        for chair in df['Chair'].unique():
            df_chair = df[df['Chair'] == chair]
            print("\n" + "-"*40 + "\n")
            print(df_chair)
            print("\n" + "-"*40 + "\n")
            
        if save_csv:
            self.save_csv(df, output_path, f"ERC_{erc_date}_panel_members.csv" if erc_date else "ERC_panel_members.csv")
        return df



if __name__ == "__main__":
     

    extractor = PdfMemberExtractor()
    df = extractor.extract(pdf_path="../data/ERC-2025-StG-panel-members.pdf", 
                           print_cmd=True, 
                           save_csv=True)
    
