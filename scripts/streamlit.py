import streamlit as st
import pandas as pd
import time
import requests
import ollama
import random
from pprint import pprint
import pycountry

# Driver for Firefox, Chrome, Edge, etc.
from selenium import webdriver
from random import uniform

# Mode of locating html elements: ID, CSS_SELECTOR, XPATH, ...
from selenium.webdriver.common.by import By               

# Using specific keyboard keys like ENTER, ESCAPE, ...
from selenium.webdriver.common.keys import Keys

# Methods for dropdown
from selenium.webdriver.support.select import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import uniform
from time import sleep
from pprint import pprint

import pandas as pd
from time import sleep
from pprint import pprint


import random
import tempfile
from selenium import webdriver

class RandomFirefoxProfile:
    """Erstellt zufällige Firefox-Profile."""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    LANGUAGES = ["en-US", "en-GB", "de-DE", "fr-FR", "es-ES"]
    
    SCREEN_RESOLUTIONS = [
        (1920, 1080),
        (1366, 768),
        (1440, 900),
        (1536, 864),
        (1280, 720),
    ]
    
    @staticmethod
    def create():
        """Erstellt ein zufälliges Firefox-Profil."""
        
        # Temporäres Profil
        temp_dir = tempfile.mkdtemp(prefix="firefox_")
        profile = webdriver.FirefoxProfile(temp_dir)
        
        # Zufälliger User-Agent
        user_agent = random.choice(RandomFirefoxProfile.USER_AGENTS)
        profile.set_preference("general.useragent.override", user_agent)
        
        # Zufällige Sprache
        language = random.choice(RandomFirefoxProfile.LANGUAGES)
        profile.set_preference("intl.accept_languages", language)
        
        # Download-Einstellungen
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", "/tmp")
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
        
        # Anti-Detection
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        profile.set_preference("privacy.trackingprotection.enabled", True)
        
        # Zufällige Viewport-Größe (simuliert verschiedene Bildschirme)
        width, height = random.choice(RandomFirefoxProfile.SCREEN_RESOLUTIONS)
        profile.set_preference("layout.css.devPixelsPerPx", str(random.uniform(0.9, 1.1)))
        
        # WebGL und Canvas Fingerprinting reduzieren
        profile.set_preference("webgl.disabled", random.choice([True, False]))
        profile.set_preference("privacy.resistFingerprinting", True)
        
        print("🎲 Zufälliges Profil erstellt:")
        print(f"   User-Agent: {user_agent[:50]}...")
        print(f"   Sprache: {language}")
        print(f"   Auflösung: {width}x{height}")
        
        return profile


class ResearchGateSelenium:

    def __init__(self, name: str = "Gregor-Anderluh", headless: bool = True):
        self.BASE_URL = 'https://www.researchgate.net/'
        self.name = name.replace(" ", "-")
        self.headless = headless
        self.driver = None
    
    def get_driver(self):
        """Initialisiert den Firefox WebDriver."""
        if self.driver is not None:
            return self.driver
        
        options = webdriver.FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")
        
        profile = RandomFirefoxProfile.create()
        options.profile = profile
        
        self.driver = webdriver.Firefox(options=options)
        return self.driver
    
    def close_driver(self):
        """Beendet den WebDriver sicher."""
        if self.driver is not None:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                print(f"⚠️ Fehler beim Schließen: {e}")
            finally:
                self.driver = None
    
    def random_sleep(self, min_seconds=1.0, max_seconds=3.0):
        """Zufällige Wartezeit."""
        sleep_time = uniform(min_seconds, max_seconds)
        sleep(sleep_time)
        return sleep_time
    
    def access_denied_check(self):
        """Prüft auf Access Denied."""
        try:
            page_html = self.driver.page_source
            if "<h1>Access denied</h1>" in page_html:
                print("⚠️ Access denied detected.")
                return True
            return False
        except Exception as e:
            print(f"⚠️ Fehler bei Access Check: {e}")
            return False
    
    def klick_privacy_accept(self):
        """Klickt auf Privacy-Accept-Button."""
        try:
            self.random_sleep(1, 2)
            wait = WebDriverWait(self.driver, 10)
            agree_button = wait.until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            agree_button.click()
            print("✅ Privacy-Banner akzeptiert")
        except Exception as e:
            print(f"ℹ️ Kein Privacy-Banner gefunden (bereits akzeptiert?)")
    
    def find_skills(self):
        """Extrahiert Skills vom ResearchGate-Profil."""
        
        # 1. Driver initialisieren
        self.get_driver()
        
        # 2. Zur Profilseite navigieren
        profile_url = f"{self.BASE_URL}profile/{self.name}"
        print(f"🌐 Öffne: {profile_url}")
        
        try:
            self.driver.get(profile_url)
            self.driver.implicitly_wait(10)
            
            # 3. Privacy-Banner akzeptieren
            self.klick_privacy_accept()
            self.random_sleep(2, 4)
            #self.driver.refresh()
            
            # 4. Access Denied prüfen
            if self.access_denied_check():
                
                self.close_driver()
                sleep_time = uniform(15, 20)
                print(f"⚠️ Zugriff verweigert. Warte {round(sleep_time, 1)} Sekunden...")
                sleep(sleep_time)
                return self.find_skills()  # Rekursiver Aufruf
            
            # 5. Skills-Element finden (mehrere Selektoren probieren)
            introduction = None
            
            selectors = [
                (By.CSS_SELECTOR, "div.nova-legacy-c-card:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)"),
                (By.XPATH, "/html/body/div[2]/main/section[3]/div/div[2]/div[2]/div/div"),
                (By.CSS_SELECTOR, "div.nova-legacy-c-card--spacing-xl div.nova-legacy-o-stack__item"),
            ]
            
            for by, selector in selectors:
                try:
                    introduction = self.driver.find_element(by, selector)
                    print(f"✅ Element gefunden mit: {by} - {selector[:50]}...")
                    break
                except Exception:
                    continue
            
            if not introduction:
                print("❌ Skills-Bereich nicht gefunden")
                return None
            
            # 6. Text extrahieren
            introduction_text = introduction.text
            
            # 7. In Liste konvertieren
            skills_list = [
                skill.strip() 
                for skill in introduction_text.split('\n') 
                if skill.strip() and skill.strip() != 'Skills and Expertise'
            ]
            
            print(f"✅ {len(skills_list)} Skills gefunden")
            return skills_list
        
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Skills: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            # 8. Driver schließen (immer!)
            self.close_driver()
    




class ORCIDClient:
    """Client für ORCID API."""
    
    BASE_URL = "https://pub.orcid.org/v3.0"
    
    @staticmethod
    def get_profile(orcid_id: str) -> dict | None:
        """Holt vollständiges ORCID-Profil."""
        url = f"{ORCIDClient.BASE_URL}/{orcid_id}"
        headers = {'Accept': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ ORCID API Fehler: {e}")
            return None
    
    @staticmethod
    def get_current_affiliation(orcid_id: str) -> str | None:
        """
        Holt die aktuelle Affiliation (neueste Employment oder Education).
        
        Returns:
            Name der Institution oder None
        """
        profile = ORCIDClient.get_profile(orcid_id)
        
        if not profile:
            return None
        
        try:
            activities = profile.get('activities-summary', {})
            

            # 1. Versuch: Employments (bevorzugt)
            employments = activities.get('employments', {})
            if employments:
                employment_groups = employments.get('affiliation-group', [])
                
                # Alle Employments mit End-Datum = None (aktuell) oder neuestes Jahr
                current_employments = []
                
                for group in employment_groups:
                    summaries = group.get('summaries', [])
                    for summary in summaries:
                        employment_summary = summary.get('employment-summary', {})
                        
                        # Prüfe ob aktuell (kein End-Datum)
                        end_date = employment_summary.get('end-date')
                        
                        if end_date is None:  # Aktuell
                            org_name = employment_summary.get('organization', {}).get('name')
                            if org_name:
                                return org_name
                        
                        # Sammle alle mit Datum für Fallback
                        start_date = employment_summary.get('start-date', {})
                        year = start_date.get('year', {}).get('value', 0) if start_date else 0
                        
                        current_employments.append({
                            'name': employment_summary.get('organization', {}).get('name'),
                            'year': year,
                            'end_date': end_date
                        })
                
                # Wenn kein aktuelles gefunden: Nimm das neueste
                if current_employments:
                    latest = max(current_employments, key=lambda x: x['year'])
                    return latest['name']
            
            # # 2. Versuch: Education (falls keine Employment)
            # educations = activities.get('educations', {})
            # if educations:
            #     education_groups = educations.get('affiliation-group', [])
                
            #     for group in education_groups:
            #         summaries = group.get('summaries', [])
            #         for summary in summaries:
            #             education_summary = summary.get('education-summary', {})
                        
            #             end_date = education_summary.get('end-date')
            #             if end_date is None:  # Noch in Ausbildung
            #                 org_name = education_summary.get('organization', {}).get('name')
            #                 if org_name:
            #                     return org_name
            
            # # 3. Fallback: Erste gefundene Institution
            # if employment_groups:
            #     first_group = employment_groups[0]
            #     summaries = first_group.get('summaries', [])
            #     if summaries:
            #         first_summary = summaries[0].get('employment-summary', {})
            #         org = first_summary.get('organization', {})
            #         return org.get('name')
        
        except (KeyError, ValueError, TypeError) as e:
            print(f"⚠️ Fehler beim Extrahieren der Affiliation: {e}")
        
        return None
    
    @staticmethod
    def get_keywords(orcid_id: str) -> list[str]:
        """Holt nur Keywords."""
        url = f"{ORCIDClient.BASE_URL}/{orcid_id}/keywords"
        headers = {'Accept': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            keywords_list = data.get('keyword', [])
            return [
                kw.get('content') 
                for kw in keywords_list 
                if kw.get('content')
            ]
        except:
            return []
    
    @staticmethod
    def get_biography(orcid_id: str) -> str | None:
        """Holt nur Biografie."""
        profile = ORCIDClient.get_profile(orcid_id)
        
        if not profile:
            return None
        
        try:
            person = profile.get('person', {})
            biography_obj = person.get('biography')
            
            if biography_obj and isinstance(biography_obj, dict):
                return biography_obj.get('content')
        except:
            pass
        
        return None
    
    @staticmethod
    def get_research_info(orcid_id: str) -> dict:
        """
        Kombiniert alle relevanten Forschungsinformationen inkl. Affiliation.
        
        Returns:
            Dictionary mit affiliation, biography, keywords, works_count
        """
        profile = ORCIDClient.get_profile(orcid_id)
        
        if not profile:
            return {
                'affiliation': None,
                'biography': None,
                'keywords': [],
                'works_count': 0,
                'orcid': orcid_id
            }
        
        # Aktuelle Affiliation
        affiliation = ORCIDClient.get_current_affiliation(orcid_id)
        
        # Biografie
        biography = None
        person = profile.get('person', {})
        bio_obj = person.get('biography')
        if bio_obj and isinstance(bio_obj, dict):
            biography = bio_obj.get('content')
        
        # Keywords
        keywords = []
        kw_obj = person.get('keywords', {})
        if kw_obj and isinstance(kw_obj, dict):
            kw_list = kw_obj.get('keyword', [])
            keywords = [
                kw.get('content') 
                for kw in kw_list 
                if isinstance(kw, dict) and kw.get('content')
            ]
        
        # Publikationsanzahl
        works_count = 0
        activities = profile.get('activities-summary', {})
        if activities:
            works = activities.get('works', {})
            if works and isinstance(works, dict):
                works_group = works.get('group', [])
                works_count = len(works_group) if isinstance(works_group, list) else 0
        
        return {
            'affiliation': affiliation,
            'biography': biography,
            'keywords': keywords,
            'works_count': works_count,
            'orcid': orcid_id
        }


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


def process_researcher_profile(results: dict, model: str = "deepseek-r1:1.5b") -> str:
    prompt = f"""
    You are a scientific summarizer. Based on the following structured information about a researcher, 
    summarize the following text in bullet points and concisely. Use semicolons (;) to separate the points, not complete sentences. This should highlight key topics or content.
    Input data:
    {results}
    """

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"] if "message" in response else str(response)

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
        print(f"⚠️ ORCID-Daten konnten nicht abgerufen werden")
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






# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Researcher Excel Explorer", layout="wide")






tab1, tab2, tab3 = st.tabs(["Step 1: File Upload", "Step 2: ERC Profilgenerator mit OpenAlex", "Step 3: Grantees und Panel Members zusammenführen"])
with tab1:
    st.info("ℹ️ Lade die erforderlichen Excel-Dateien hoch.")
    col1, col2 = st.columns(2)
    with col1:
        grantees_and_panel_member_excel = st.file_uploader("📁 Excel-Datei hochladen", type=["xlsx"])
    with col2:
        list_of_funded_projects_excel = st.file_uploader("📁 Dashboard-Datei hochladen", type=["xlsx"])
        st.markdown("Lade die 'List of funded projects' Excel-Datei vom [ERC-Dashboard](https://dashboard.tech.ec.europa.eu/qs_digit_dashboard_mt/public/sense/app/c140622a-87e0-412e-8b29-9b5ddd857e13/sheet/61a0bd1d-cd6d-4ac8-8b55-80d8661e44c0/state/analysis) hoch.")
    
    if grantees_and_panel_member_excel and list_of_funded_projects_excel:
        st.success("✅ Beide Dateien wurden erfolgreich hochgeladen! \n Du kannst nun zum nächsten Tab wechseln.")
    container = st.container()
    with container:
        st.markdown("🔗 **ERC Förderprogramme:**")
        col1, col2= st.columns(2)
        with col1:
            st.link_button("STG", "https://erc.europa.eu/apply-grant/starting-grant", icon="🌐")
            st.link_button("AdG", "https://erc.europa.eu/apply-grant/advanced-grant", icon="🌐")
            st.link_button("CoG", "https://erc.europa.eu/apply-grant/consolidator-grant", icon="🌐")
        with col2:
            st.markdown("🔗 **Nützliche Links:**")
            st.link_button("ERC-Dashboard", "https://erc.europa.eu/projects-statistics/erc-dashboard", icon="🌐")
            st.link_button("Panel Members", "https://erc.europa.eu/apply-grant/panel-members", icon="🌐")

    st.divider()
    st.subheader("Anleitung:")
    st.markdown("""
    1. Schritt — Dateien hochladen: Im Tab "Step 1: File Upload" lade die Excel-Datei mit Grantees & Panel Members hoch. Optional: lade hier auch die "List of funded projects" (Dashboard‑Export).
    2. Schritt — Profile generieren: Öffne "Step 2: ERC Profilgenerator mit OpenAlex" (ERC Profilgenerator mit OpenAlex), wähle das Tabellenblatt und die relevanten Spalten aus, überprüfe fehlende Werte und klicke "Profil generieren", um Felder wie "Field" und "Affiliation" automatisch zu befüllen.
    3. Schritt — Zusammenführen & Export: Im Tab "Step 3: Grantees und Panel Members zusammenführen" wähle die entsprechenden Spalten aus beiden Dateien aus, führe die Tabellen zusammen und lade die aktualisierte Excel‑Datei herunter.

    **Kurz-Tipps:**
    - Achte auf korrekte Spaltennamen (z. B. "First name", "Last name", "Call").
    - Nutze den Call‑Filter, um gezielt Jahrgänge/Programme zu bearbeiten.
    - Bei fehlenden OpenAlex‑Ergebnissen überprüfe die Schreibweise des Namens.
    """)

with tab2:
    st.subheader("ERC Profilgenerator mit OpenAlex")
    if grantees_and_panel_member_excel is not None:
        # Datei als DataFrame laden
        try:
            sheet_names = pd.ExcelFile(grantees_and_panel_member_excel).sheet_names
            col1, col2 = st.columns(2)
            
            
            with col1:
                sheet_name = st.selectbox("Wähle ein Tabellenblatt:", sheet_names)
            df_gapm = pd.read_excel(grantees_and_panel_member_excel, sheet_name=sheet_name)
            df_gapm.columns = df_gapm.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

            #st.subheader("🧾 Vorschau der Daten:")
            #st.dataframe(df_gapm.head())

            # Optionaler Filter
            if "Call" in df_gapm.columns:
                calls = df_gapm["Call"].dropna().unique().tolist()
                # sort calls e.g. CoG 2023, CoG 2022, CoG 2021, ...
                calls.sort(reverse=True)
                with col2:
                    filter_call = st.selectbox("Filter nach 'Call':", ["(kein Filter)"] + calls)
                if filter_call != "(kein Filter)":
                    df_gapm = df_gapm[df_gapm["Call"] == filter_call]
                    st.success(f"Gefiltert nach: {filter_call}")

            # Name-Spalte erstellen
            if "First name" in df_gapm.columns and "Last name" in df_gapm.columns:
                df_gapm["Name"] = df_gapm["First name"].astype(str) + " " + df_gapm["Last name"].astype(str)
                #st.info("✅ Spalte 'Name' erstellt.")
            else:
                st.warning("⚠️ Spalten 'First name' und/oder 'Last name' fehlen!")

            st.dataframe(df_gapm)
            st.divider()


            st.subheader("🔍 Zeige fehlende Spalten an:")
            selected_columns = st.multiselect(
                                "Wähle Spalten aus, um fehlende Werte zu überprüfen:",
                                df_gapm.columns.tolist()
                            )

            if selected_columns:
                # Erstelle Maske: True, wenn mindestens eine der ausgewählten Spalten NaN ist
                mask = df_gapm[selected_columns].isnull().any(axis=1)

                # Wähle alle Zeilen, wo mindestens ein Wert fehlt
                missing_rows = df_gapm[mask]

                st.write(f"Anzahl der Zeilen mit fehlenden Werten: {missing_rows.shape[0]}")
                st.dataframe(missing_rows.drop(columns=['Name']))
            else:
                st.info("Bitte wähle mindestens eine Spalte aus.")
                

            st.divider()
            # OpenAlex-Profil abrufen
            st.subheader("🔎 OpenAlex- Profilgenerierung")
            unique_members = missing_rows['Name'].unique()
            selected_member = st.multiselect(f"Wähle ein Mitglied aus: ({len(unique_members)})", unique_members, default=unique_members)
            col1, col2 = st.columns(2)
            with col1:
                profile_column = st.selectbox("Wähle die Spalte für das generierte Profil: (Field)", options=selected_columns, index=1)
            with col2:
                affiliation_column = st.selectbox("Wähle die Spalte für die Affiliation:", options=selected_columns, index=0)
            names_to_search = selected_member if selected_member else st.text_input("Name eingeben, um Profil zu erstellen:")

            num_generated_profiles = 0
            num_generated_affiliations = 0
            num_not_found = 0
            num_green = 0
            if st.button("Profil generieren"):
                if not names_to_search:
                    st.warning("Bitte mindestens einen Namen eingeben.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()  # Platzhalter für Statusnachricht
                    total_names = len(names_to_search)

                    for idx, name_to_search in enumerate(names_to_search):
                        current_progress = (idx + 1) / total_names
                        status_text.text(f"🔍 Verarbeite {idx + 1}/{total_names}: {name_to_search}")

                        if name_to_search.strip():
                            with st.spinner(f"Suche nach {name_to_search}..."):
                                results = fetch_researcher_info_orcid_first(name_to_search)

                                if results:
                                    #st.json(results)
                                    affiliation = results.get("affiliation", None)

                                    #st.write("**Generiere Profil mit Ollama...**")
                                    pprint(results)
                                    #profile_text = process_researcher_profile(results)
                                    profile_text = results.get("topics", [])
                                    # replace list commas with semicolons and make text lowercase
                                    profile_text = "; ".join(profile_text).lower()

                                    if not profile_text:
                                        rg_selenium = ResearchGateSelenium(name=name_to_search, headless=True)
                                        profile_text = rg_selenium.find_skills() 
                                        profile_text = "; ".join(profile_text).lower() if profile_text else None
                                    


                                    if profile_text and affiliation:
                                        st.success(f"✅ Profil für {name_to_search} generiert")
                                        num_generated_profiles += 1
                                        num_generated_affiliations += 1
                                        num_green += 1
                                    elif profile_text and not affiliation:
                                        num_generated_profiles += 1
                                        st.warning(f"⚠️ Profil generiert, aber keine Affiliation für {name_to_search} gefunden.")
                                    
                                    elif not profile_text and affiliation:
                                        num_generated_affiliations += 1
                                        st.warning(f"⚠️ Affiliation gefunden, aber kein Profil für {name_to_search}.")
                                        
                                    else:
                                        num_not_found += 1
                                        st.error(f"⚠️ Weder Profil noch Affiliation für {name_to_search} gefunden.")
                                        #st.write(profile_text)

                                    df_gapm_member = missing_rows[missing_rows['Name'] == name_to_search]
                                    df_gapm_member[profile_column] = profile_text
                                    df_gapm_member[affiliation_column] = affiliation

                                    # Ursprünglichen DataFrame aktualisieren
                                    for row_idx in df_gapm_member.index:
                                        df_gapm.at[row_idx, profile_column] = df_gapm_member.at[row_idx, profile_column]
                                        df_gapm.at[row_idx, affiliation_column] = df_gapm_member.at[row_idx, affiliation_column]
                                
                                else:
                                    st.error(f"⚠️ Keine Daten für {name_to_search} gefunden.")
                                    num_not_found += 1
                            random_time = random.uniform(0.5, 1.5)
                            time.sleep(random_time)

                        else:
                            st.warning("Leerer Name übersprungen.")

                        # Fortschritt aktualisieren
                        progress_bar.progress(current_progress)

                    # Alles fertig 🎉
                    progress_bar.empty()
                    status_text.text("✅ Alle Profile wurden verarbeitet!")

                    df_generated_profiles_affiliations = pd.DataFrame({
                        "Vollstädnige Profile" : [num_green],
                        "Generierte Profile": [num_generated_profiles],
                        "Generierte Affiliations": [num_generated_affiliations],
                        "Nicht gefunden": [num_not_found]
                    })
                    st.dataframe(df_generated_profiles_affiliations)

                    

                    st.subheader("📊 Aktualisierte Daten:")
                    # drop column 'Name' before displaying
                    df_gapm = df_gapm.drop(columns=['Name'])
                    st.dataframe(df_gapm)

                    st.success("✅ Alle fehlenden Profile wurden aktualisiert. \n Du kannst die aktualisierte Datei im nächsten Tab herunterladen.")


            # st.divider()
            # st.subheader("💾 Aktualisierte Datei herunterladen")
            # st.download_button("Download", df_gapm.to_csv().encode('utf-8'), "updated_data.csv", "text/csv")


                    

        except Exception as e:
            st.info("Keine fehlenden Werte gefunden.\n" + str(e))
    else:
        st.info("⬆️ Bitte lade die 'grantees_and_panel_members' Excel-Datei hoch.")



        
        
        


    st.divider()
with tab3:
    st.subheader("ERC Dashboard")
    if list_of_funded_projects_excel and grantees_and_panel_member_excel is not None:
        # Datei als DataFrame laden
        try:
            sheet_names_lofpe = pd.ExcelFile(list_of_funded_projects_excel).sheet_names
            sheet_name_lofpe = sheet_names_lofpe[0]
            df_dashboard = pd.read_excel(list_of_funded_projects_excel, sheet_name=sheet_name_lofpe)
            df_dashboard.columns = df_dashboard.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

            # Benötigte Spalten auswählen Host Institution(s), Country, Abstract, Project Title, Researcher, Acronym, Call, CORDIS Link, Panel, Domain
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                dashboard_column_aconym = st.selectbox("Wähle die Spalte für 'Acronym':", df_dashboard.columns.tolist(), index=1, key="df_dashboard_acronym")
            with col2:
                dashboard_column_project_title = st.selectbox("Wähle die Spalte für 'Project Title':", df_dashboard.columns.tolist(), index=2, key="df_dashboard_project_title")
            with col3:
                dashboard_column_abstract = st.selectbox("Wähle die Spalte für 'Abstract':", df_dashboard.columns.tolist(), index=3, key="df_dashboard_abstract")
            with col4:
                dashboard_column_researcher = st.selectbox("Wähle die Spalte für 'Researcher':", df_dashboard.columns.tolist(), index=4, key="df_dashboard_researcher")
            with col5:
                dashboard_column_institution = st.selectbox("Wähle die Spalte für 'Institution':", df_dashboard.columns.tolist(), index=5, key="df_dashboard_institution")

            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                dashboard_column_host_country = st.selectbox("Wähle die Spalte für 'Country':", df_dashboard.columns.tolist(), index=6, key="df_dashboard_host_country")
            with col7:
                dashboard_column_call = st.selectbox("Wähle die Spalte für 'Call':", df_dashboard.columns.tolist(), index=9, key="df_dashboard_call")
            with col8:
                dashboard_column_domain = st.selectbox("Wähle die Spalte für 'Domain':", df_dashboard.columns.tolist(), index=11, key="df_dashboard_domain")
            with col9:
                dashboard_column_panel = st.selectbox("Wähle die Spalte für 'Panel':", df_dashboard.columns.tolist(), index=12, key="df_dashboard_panel")
            with col10:
                dashboard_column_cordis_link = st.selectbox("Wähle die Spalte für 'CORDIS Link':", df_dashboard.columns.tolist(), index=17, key="df_dashboard_cordis_link")

            df_dashboard_selected_columns = [dashboard_column_aconym, dashboard_column_project_title, dashboard_column_abstract, dashboard_column_researcher, dashboard_column_institution, dashboard_column_host_country, dashboard_column_call, dashboard_column_domain, dashboard_column_panel, dashboard_column_cordis_link]


            st.dataframe(df_dashboard)

            

            st.subheader("Tabllenblatt 'Grantees' verarbeiten")
            sheet_names_gapme = pd.ExcelFile(grantees_and_panel_member_excel).sheet_names
            col1, col2 = st.columns(2)
            with col1:
                sheet_name_gapme = st.selectbox("Wähle das Tabellenblatt 'Grantees':", sheet_names_gapme, key="sheet_name_gapme", index=1)
            df_pm = pd.read_excel(grantees_and_panel_member_excel, sheet_name=sheet_name_gapme)
            df_pm.columns = df_pm.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

            # Benötigte Spalten auswählen Host Institution(s), Country, Abstract, Project Title, Researcher, Acronym, Call, CORDIS Link, Panel, Domain
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                pm_column_last_name = st.selectbox("Wähle die Spalte für 'Last Name':", df_pm.columns.tolist(), index=0, key="df_pm_last_name")
            with col2:
                pm_column_first_name = st.selectbox("Wähle die Spalte für 'First Name':", df_pm.columns.tolist(), index=1, key="df_pm_first_name")
            with col3:
                pm_column_institution = st.selectbox("Wähle die Spalte für 'Institution':", df_pm.columns.tolist(), index=2, key="df_pm_institution")
            with col4:
                pm_column_country = st.selectbox("Wähle die Spalte für 'Host Country':", df_pm.columns.tolist(), index=3, key="df_pm_country")
            with col5:
                pm_column_aconym = st.selectbox("Wähle die Spalte für 'Acronym':", df_pm.columns.tolist(), index=4, key="df_pm_acronym")
            # with col6:
            #     column_host_institution = st.selectbox("Wähle die Spalte für 'Host Institution(s)':", df_pm.columns.tolist(), index=11, key="df_pm_host_institution")


            col7, col8, col9, col10, col11, col12 = st.columns(6)
            with col7:
                pm_column_project_title = st.selectbox("Wähle die Spalte für 'Project Title':", df_pm.columns.tolist(), index=5, key="df_pm_project_title")
            with col8:
                pm_column_abstract = st.selectbox("Wähle die Spalte für 'Abstract':", df_pm.columns.tolist(), index=6, key="df_pm_abstract")
            with col9:
                pm_column_panel = st.selectbox("Wähle die Spalte für 'Panel':", df_pm.columns.tolist(), index=7, key="df_pm_panel")
            with col10:
                pm_column_domain = st.selectbox("Wähle die Spalte für 'Domain':", df_pm.columns.tolist(), index=8, key="df_pm_domain")

            with col11:
                pm_column_call = st.selectbox("Wähle die Spalte für 'Call':", df_pm.columns.tolist(), index=9, key="df_pm_call")
            with col12:
                pm_column_cordis_link = st.selectbox("Wähle die Spalte für 'CORDIS Link':", df_pm.columns.tolist(), index=10, key="df_pm_cordis_link")

            df_pm_name = df_pm[pm_column_first_name].astype(str) + " " + df_pm[pm_column_last_name].astype(str)
            df_pm["Name"] = df_pm_name.str.strip()

            st.dataframe(df_pm)



            


            df_pm = pd.read_excel(grantees_and_panel_member_excel, sheet_name=sheet_name_gapme)  # Lade alle Tabellenblätter
            df_pm["Name"] = df_pm[pm_column_first_name].astype(str) + " " + df_pm[pm_column_last_name].astype(str)
            df_pm["Name"] = df_pm["Name"].str.strip()
            unique_panels = df_pm[pm_column_panel].unique().tolist()


            df_dashboard = df_dashboard[df_dashboard_selected_columns]
            
            # rename columns
            df_dashboard.rename(columns={
                dashboard_column_researcher: "Name",
                dashboard_column_host_country: pm_column_country,
            }, inplace=True)
            # Neue Spalte mit Länderkürzel
            df_dashboard[pm_column_country] = df_dashboard[pm_column_country].apply(get_country_code)


            # select from Life Sciences (LS) only the word in ()
            df_dashboard[pm_column_domain] = df_dashboard[pm_column_domain].str.extract(r'\((.*?)\)')

            # only select the word bevore - in LS1 - Molecules of Life: Biological Mechanisms...
            df_dashboard[pm_column_panel] = df_dashboard[pm_column_panel].str.split('-').str[0].str.strip()

            # only select the Panel values that are in the unique_panels list
            df_dashboard = df_dashboard[df_dashboard[pm_column_panel].isin(unique_panels)]

            st.subheader("Zusammengeführte Daten")
            # merge both dataframes on Name
            df_combined = pd.concat([df_pm, df_dashboard], ignore_index=True, sort=False)
            # Maske erstellen
            mask = df_combined[pm_column_last_name].isnull() & df_combined[pm_column_first_name].isnull()

            # Überprüfen, ob die Spalte "Name" korrekt formatiert ist
            df_combined["Name"] = df_combined["Name"].str.strip()

            # Spalte "Name" in "First Name" und "Last Name" aufteilen
            split_names = df_combined.loc[mask, "Name"].str.split(' ', n=1, expand=True)

            split_names.columns = [pm_column_first_name, pm_column_last_name]

            # Fallback für fehlende Nachnamen
            split_names[pm_column_last_name] = split_names[pm_column_last_name]

            # Zuweisung der aufgeteilten Namen
            df_combined.loc[mask, [pm_column_first_name, pm_column_last_name]] = split_names

            df_combined = df_combined.drop_duplicates().reset_index(drop=True).drop(columns=['Name'])

            st.dataframe(df_combined)


            st.subheader("💾 Aktualisierte Datei mit beiden Tabellenblättern herunterladen")

            # Datei mit allen Tabellenblättern laden
            excel_data = pd.ExcelFile(grantees_and_panel_member_excel)
            all_sheets = {sheet: excel_data.parse(sheet) for sheet in excel_data.sheet_names}

            # Ersetze die Tabellenblätter "sheet_name" und "sheet_name_gapme"
            all_sheets[sheet_name] = df_gapm  # Aktualisiertes DataFrame für sheet_name
            all_sheets[sheet_name_gapme] = df_combined  # Aktualisiertes DataFrame für sheet_name_gapme

            # Speichere die Datei mit den aktualisierten Tabellenblättern
            output_file = "updated_grantees_and_panel_member.xlsx"
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                for sheet, data in all_sheets.items():
                    data.to_excel(writer, sheet_name=str(sheet), index=False)

            if output_file:
                st.success(f"Die Datei wurde erfolgreich gespeichert: {output_file}")

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 Aktualisierte Datei herunterladen",
                        data=open(output_file, "rb"),
                        file_name=output_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            else:
                st.error("Fehler beim Speichern der Datei.")
            
            
            


        except Exception as e:
            st.error(f"Datei noch nicht hochgeladen oder Fehler beim Einlesen der Datei: {e}")
    else:
        st.info("⬆️ Bitte lade die 'List of funded projects(armUGTS)' Excel-Datei hoch.")
