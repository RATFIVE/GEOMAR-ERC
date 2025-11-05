import streamlit as st
import pandas as pd
import time
import requests
import ollama
from tqdm import tqdm
import random
from pprint import pprint

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
        topics = first_result.get('topics', [])
        sorted_topics = sorted(topics, key=lambda x: x.get('count', 0), reverse=True)
        top_topics = [t['display_name'] for t in sorted_topics[:3]]

        affiliations = first_result.get('affiliations', [])
        affiliation = affiliations[0]["institution"]["display_name"] if affiliations else None

        x_concepts = first_result.get('x_concepts', [])
        x_concepts_fields_list = [
            concept['display_name'] for concept in x_concepts if concept.get("score", 0) >= 90
        ]

        return {
            "Name": name,
            "topics": top_topics,
            "affiliation": affiliation,
            "x_concepts": x_concepts_fields_list
        }

    else:
        st.error(f"⚠️ Fehler bei Anfrage: {response.status_code}")
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






# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Researcher Excel Explorer", layout="wide")
st.title("ERC Profilgenerator mit OpenAlex")
st.divider()



with st.sidebar:
    # Upload-Feld
    grantees_and_panel_member_excel = st.file_uploader("📁 Excel-Datei hochladen", type=["xlsx"])



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
                            results = fetch_openalex_id(name_to_search)

                            if results:
                                #st.json(results)
                                affiliation = results.get("affiliation", None)

                                #st.write("**Generiere Profil mit Ollama...**")
                                pprint(results)
                                #profile_text = process_researcher_profile(results)
                                profile_text = results.get("topics", [])
                                # replace list commas with semicolons and make text lowercase
                                profile_text = "; ".join(profile_text).lower()
                                st.success(f"✅ Profil für {name_to_search} generiert")
                                #st.write(profile_text)

                                df_gapm_member = missing_rows[missing_rows['Name'] == name_to_search]
                                df_gapm_member[profile_column] = profile_text
                                df_gapm_member[affiliation_column] = affiliation

                                # Ursprünglichen DataFrame aktualisieren
                                for row_idx in df_gapm_member.index:
                                    df_gapm.at[row_idx, profile_column] = df_gapm_member.at[row_idx, profile_column]
                                    df_gapm.at[row_idx, affiliation_column] = df_gapm_member.at[row_idx, affiliation_column]

                            else:
                                st.warning(f"Keine Daten für {name_to_search} gefunden.")
                        random_time = random.uniform(0.5, 1.5)
                        time.sleep(random_time)

                    else:
                        st.warning("Leerer Name übersprungen.")

                    # Fortschritt aktualisieren
                    progress_bar.progress(current_progress)

                # Alles fertig 🎉
                progress_bar.empty()
                status_text.text("✅ Alle Profile wurden verarbeitet!")

                st.subheader("📊 Aktualisierte Daten:")
                # drop column 'Name' before displaying
                df_gapm = df_gapm.drop(columns=['Name'])
                st.dataframe(df_gapm)


        # st.divider()
        # st.subheader("💾 Aktualisierte Datei herunterladen")
        # st.download_button("Download", df_gapm.to_csv().encode('utf-8'), "updated_data.csv", "text/csv")


                

    except Exception as e:
        st.error(f"Fehler beim Einlesen der Datei: {e}")
else:
    st.info("⬆️ Bitte lade die 'grantees_and_panel_members' Excel-Datei hoch.")


with st.sidebar:
    # download the Dashboard File from https://dashboard.tech.ec.europa.eu/qs_digit_dashboard_mt/public/sense/app/c140622a-87e0-412e-8b29-9b5ddd857e13/sheet/61a0bd1d-cd6d-4ac8-8b55-80d8661e44c0/state/analysis and upload it here
    list_of_funded_projects_excel = st.file_uploader("📁 Dashboard-Datei hochladen", type=["xlsx"])
    st.markdown("Lade die 'List of funded projects' Excel-Datei vom [ERC-Dashboard](https://dashboard.tech.ec.europa.eu/qs_digit_dashboard_mt/public/sense/app/c140622a-87e0-412e-8b29-9b5ddd857e13/sheet/61a0bd1d-cd6d-4ac8-8b55-80d8661e44c0/state/analysis) hoch.")

st.divider()
st.title("ERC Dashboard")
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
            # select the Researcher column and Project Title column
            column_researcher = st.selectbox("Wähle die Spalte für 'Acronym':", df_dashboard.columns.tolist(), index=1)
        with col2:
            column_project_title = st.selectbox("Wähle die Spalte für 'Project Title':", df_dashboard.columns.tolist(), index=2)
        with col3:
            column_abstract = st.selectbox("Wähle die Spalte für 'Abstract':", df_dashboard.columns.tolist(), index=3)
        with col4:
            column_call = st.selectbox("Wähle die Spalte für 'Researcher':", df_dashboard.columns.tolist(), index=4)
        with col5:
            column_cordis_link = st.selectbox("Wähle die Spalte für 'Institution':", df_dashboard.columns.tolist(), index=5)
        
        col6, col7, col8, col9, col10 = st.columns(5)
        with col6:
            column_host_institution = st.selectbox("Wähle die Spalte für 'Country':", df_dashboard.columns.tolist(), index=6)
        with col7:
            column_country = st.selectbox("Wähle die Spalte für 'Call':", df_dashboard.columns.tolist(), index=9)
        with col8:
            column_panel = st.selectbox("Wähle die Spalte für 'Domain':", df_dashboard.columns.tolist(), index=11)
        with col9:
            column_domain = st.selectbox("Wähle die Spalte für 'Panel':", df_dashboard.columns.tolist(), index=12)
        with col10:
            column_domain_2 = st.selectbox("Wähle die Spalte für 'CORDIS Link':", df_dashboard.columns.tolist(), index=17)



        st.dataframe(df_dashboard)


        sheet_names_gapme = pd.ExcelFile(grantees_and_panel_member_excel).sheet_names
        col1, col2 = st.columns(2)
        with col1:
            sheet_name_gapme = st.selectbox("Wähle das Tabellenblatt 'Grantees':", sheet_names_gapme, key="sheet_name_gapme")
        df_pm = pd.read_excel(grantees_and_panel_member_excel, sheet_name=sheet_name_gapme)
        

        df_pm_name = df_pm["First Name"].astype(str) + " " + df_pm["Last Name"].astype(str)
        df_pm["Name"] = df_pm_name.str.strip()

        st.dataframe(df_pm)
        


    except Exception as e:
        st.error(f"Fehler beim Einlesen der Datei: {e}")
else:
    st.info("⬆️ Bitte lade die 'List of funded projects(armUGTS)' Excel-Datei hoch.")
