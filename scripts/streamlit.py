import streamlit as st
import pandas as pd
import time
import requests
import ollama
from tqdm import tqdm

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
    write a concise, natural-sounding academic profile of about 3 sentences. Focus on their main research areas.
    Input data:
    {results}
    """

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"] if "message" in response else str(response)


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Researcher Excel Explorer", layout="wide")
st.title("Excel Analyzer mit OpenAlex & Ollama")

# Upload-Feld
uploaded_file = st.file_uploader("📁 Excel-Datei hochladen", type=["xlsx"])

if uploaded_file is not None:
    # Datei als DataFrame laden
    try:
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        sheet_name = st.selectbox("Wähle ein Tabellenblatt:", sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

        #st.subheader("🧾 Vorschau der Daten:")
        #st.dataframe(df.head())

        # Optionaler Filter
        if "Call" in df.columns:
            calls = df["Call"].dropna().unique().tolist()
            # sort calls e.g. CoG 2023, CoG 2022, CoG 2021, ...
            calls.sort(reverse=True)
            filter_call = st.selectbox("Filter nach 'Call':", ["(kein Filter)"] + calls)
            if filter_call != "(kein Filter)":
                df = df[df["Call"] == filter_call]
                st.success(f"Gefiltert nach: {filter_call}")

        # Name-Spalte erstellen
        if "First name" in df.columns and "Last name" in df.columns:
            df["Name"] = df["First name"].astype(str) + " " + df["Last name"].astype(str)
            #st.info("✅ Spalte 'Name' erstellt.")
        else:
            st.warning("⚠️ Spalten 'First name' und/oder 'Last name' fehlen!")

        st.dataframe(df)


        st.subheader("Zeige fehlende Spalten an:")
        selected_columns = st.multiselect(
                            "Wähle Spalten aus, um fehlende Werte zu überprüfen:",
                            df.columns.tolist()
                        )

        if selected_columns:
            # Erstelle Maske: True, wenn mindestens eine der ausgewählten Spalten NaN ist
            mask = df[selected_columns].isnull().any(axis=1)

            # Wähle alle Zeilen, wo mindestens ein Wert fehlt
            missing_rows = df[mask]

            st.subheader(f"🔍 Zeilen mit fehlenden Werten in {selected_columns}:")
            st.write(f"Anzahl der Zeilen mit fehlenden Werten: {missing_rows.shape[0]}")
            st.dataframe(missing_rows.drop(columns=['Name']))
        else:
            st.info("Bitte wähle mindestens eine Spalte aus.")
            


        # Optional: OpenAlex-Profil abrufen
        st.subheader("🔎 OpenAlex- und Ollama-Profilgenerierung")
        unique_members = missing_rows['Name'].unique()
        selected_member = st.multiselect(f"Wähle ein Mitglied aus: ({len(unique_members)})", unique_members, default=unique_members)
        profile_column = st.selectbox("Wähle die Spalte für das generierte Profil:", options=selected_columns, index=1)
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
                                profile_text = process_researcher_profile(results)
                                st.success(f"✅ Profil für {name_to_search} generiert")
                                #st.write(profile_text)

                                df_member = missing_rows[missing_rows['Name'] == name_to_search]
                                df_member[profile_column] = profile_text
                                df_member[affiliation_column] = affiliation

                                # Ursprünglichen DataFrame aktualisieren
                                for row_idx in df_member.index:
                                    df.at[row_idx, profile_column] = df_member.at[row_idx, profile_column]
                                    df.at[row_idx, affiliation_column] = df_member.at[row_idx, affiliation_column]

                            else:
                                st.warning(f"Keine Daten für {name_to_search} gefunden.")
                        time.sleep(0.5)  # kurze Pause

                    else:
                        st.warning("Leerer Name übersprungen.")

                    # Fortschritt aktualisieren
                    progress_bar.progress(current_progress)

                # Alles fertig 🎉
                progress_bar.empty()
                status_text.text("✅ Alle Profile wurden verarbeitet!")

                st.subheader("📊 Aktualisierte Daten:")
                # drop column 'Name' before displaying
                df = df.drop(columns=['Name'])
                st.dataframe(df)

    except Exception as e:
        st.error(f"Fehler beim Einlesen der Datei: {e}")
else:
    st.info("⬆️ Bitte lade zuerst eine Excel-Datei hoch.")