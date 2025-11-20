import requests
# import ollama
import pycountry

# Driver for Firefox, Chrome, Edge, etc.

# Mode of locating html elements: ID, CSS_SELECTOR, XPATH, ...

# Using specific keyboard keys like ENTER, ESCAPE, ...

# Methods for dropdown

# eigene Module
from ORCIDClient import ORCIDClient
# -----------------------------
# Hilfsfunktionen
# -----------------------------
def fetch_openalex_id(name: str) -> dict | None:
    search_name = name.replace(" ", "+")
    base_url = f"https://api.openalex.org/authors?filter=display_name.search:{search_name}"
    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()
        results_list = data.get('results', [])
        
        if not results_list:
            #st.warning(f"⚠️ Keine Ergebnisse für {name}")
            return None

        first_result = results_list[0]
        #pprint(first_result)
        topics = first_result.get('topics', [])
        sorted_topics = sorted(topics, key=lambda x: x.get('count', 0), reverse=True)
        top_topics = [t['display_name'] for t in sorted_topics[:4]]

        affiliations = first_result.get('affiliations', [])
        
        # Funktion, um die aktuellste Institution zu finden
        def get_most_recent_affiliation(affiliations):
            if not affiliations:
                return None
            # Sortiere nach dem höchsten Jahr in der `years`-Liste
            most_recent = max(affiliations, key=lambda x: max(x.get('years', [0])))
            return most_recent['institution']

        # Aktuellste Institution abrufen
        most_recent_affiliation = get_most_recent_affiliation(affiliations)
        x_concepts = first_result.get('x_concepts', [])
        x_concepts_fields_list = [
            concept['display_name'] for concept in x_concepts if concept.get("score", 0) >= 90
        ]

        return {
            "Name": name,
            "topics": top_topics,
            "affiliation": most_recent_affiliation['display_name'] if most_recent_affiliation else None,
            "x_concepts": x_concepts_fields_list
        }

    else:
        #st.error(f"⚠️ Fehler bei Anfrage: {response.status_code}")
        return None


# def process_researcher_profile(results: dict, model: str = "deepseek-r1:1.5b") -> str:
#     prompt = f"""
#     You are a scientific summarizer. Based on the following structured information about a researcher, 
#     summarize the following text in bullet points and concisely. Use semicolons (;) to separate the points, not complete sentences. This should highlight key topics or content.
#     Input data:
#     {results}
#     """

#     response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
#     return response["message"]["content"] if "message" in response else str(response)

# Funktion, um den ISO-Alpha-2-Code zu bekommen
def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_2
    except LookupError:
        return None  # Falls kein Land gefunden wird

def fetch_openalex_orcid_only(name: str) -> str | None:
    """
    Holt nur die ORCID-ID von OpenAlex.
    
    Args:
        name: Vollständiger Name des Forschers
        
    Returns:
        ORCID-ID als String oder None
    """
    search_name = name.replace(" ", "+")
    base_url = f"https://api.openalex.org/authors?filter=display_name.search:{search_name}"
    
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results_list = data.get('results', [])
        
        if not results_list:
            print(f"⚠️ Keine OpenAlex-Ergebnisse für '{name}'")
            return None
        
        first_result = results_list[0]
        orcid = first_result.get('orcid')
        
        if orcid:
            # ORCID ID extrahieren (URL → ID)
            orcid_id = orcid.split('/')[-1] if '/' in orcid else orcid
            return orcid_id
        
        print(f"⚠️ Keine ORCID gefunden für '{name}'")
        return None
    
    except Exception as e:
        print(f"❌ Fehler für '{name}': {e}")
        return None


def fetch_researcher_info_orcid_first(name: str) -> dict | None:
    """
    Holt ORCID von OpenAlex und alle Daten (inkl. Affiliation) von ORCID.
    
    Args:
        name: Vollständiger Name des Forschers
        
    Returns:
        Dictionary mit allen Forscherdaten oder None
    """
    print(f"🔍 Suche ORCID für: {name}")
    
    # 1. ORCID von OpenAlex holen
    orcid_id = fetch_openalex_orcid_only(name)
    
    if not orcid_id:
        print(f"❌ Keine ORCID gefunden für '{name}'")
        return None
    
    print(f"✅ ORCID gefunden: {orcid_id}")
    
    # 2. Alle Daten von ORCID holen
    orcid_data = ORCIDClient.get_research_info(orcid_id)
    
    if not orcid_data:
        print("⚠️ ORCID-Daten konnten nicht abgerufen werden")
        return None
    
    # 3. Ergebnis zusammenstellen
    return {
        "name": name,
        "orcid": orcid_id,
        "affiliation": orcid_data.get('affiliation'),
        "topics": orcid_data.get('keywords', []),  # Alle Keywords
        "biography": orcid_data.get('biography'),
        "works_count": orcid_data.get('works_count', 0)
    }


def highlight_continuous_members(df):
    """
    Markiere Mitglieder die 4 mal aufeinander im Panel waren.
    Dabei wird eine neue Spalte 'Continuous_Member' hinzugefügt, die True für kontinuierliche Mitglieder und False für andere Mitglieder enthält.
    Hier wird nur das Jahr True markiert, in dem das Mitglied zum 4. Mal in Folge teilgenommen hat.
    Wenn ein Mitglied z.B. 2015, 2016, 2017, 2018 teilgenommen hat, wird nur 2018 als True markiert. Wenn das Mitglied wieder 2020 teilnimmt, wird 2020 nicht markiert, da die Teilnahme nicht kontinuierlich ist.

    Args:
        df (pd.DataFrame): _DataFrame mit Panel-Mitgliedern und deren Teilnahmejahren_
    Returns:
        pd.DataFrame: _DataFrame mit zusätzlicher Spalte 'Continuous_Member'_
    """

    # # add beispiel daten
    # print(df.shape)
    # df = pd.concat([df, pd.DataFrame(
    #     {
    #     "First name": ["Alice", "Alice", "Alice", "Alice", "Alice"],
    #     "Last name": ["Adam", "Adam", "Adam", "Adam", "Adam"],
    #     "Call": ["Panel 2015", "Panel 2016", "Panel 2017", "Panel 2018", "Panel 2019"],
    #     })
    #     ], 
    # ignore_index=True,)
    # print(df.shape)

    
    
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True) # Spaltennamen bereinigen
    df["Name"] = df["First name"] + " " + df["Last name"]
    df["Year"] = df["Call"].str.extract(r'(\d{4})').astype(int)
    df = df.sort_values(by=["Name", "Year"])
    df["4x Continuous Member"] = False
    for name, group in df.groupby("Name"):
        years = group["Year"].values
        count = 1
        for i in range(1, len(years)): # Starte bei 1, da wir das vorherige Jahr vergleichen
            if years[i] == years[i-1] + 1: # Überprüfe ob das Jahr auf das vorherige Jahr folgt
                count += 1 # Erhöhe den Zähler für aufeinanderfolgende Jahre
                if count >= 4: # Wenn der Zähler 4 erreicht, markiere das Jahr als kontinuierlich
                    df.loc[(df["Name"] == name) & (df["Year"] == years[i]), "4x Continuous Member"] = True
            else:
                count = 1
    df.drop(columns=["Name", "Year"], inplace=True)
    return df