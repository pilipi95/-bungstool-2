import random
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="MFA Prüfungstrainer BW",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #0E1117;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4A5568;
        margin-bottom: 25px;
    }
    .card {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2563EB;
        margin-bottom: 15px;
    }
    .badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_allow_html=True,
)

# Database of Questions Extracted from Exam Documents
EXAM_DATA = [
    # --- BEHANDLUNGSASSISTENZ ---
    {
        "id": 1,
        "area": "Behandlungsassistenz",
        "topic": "Anatomie & Labor",
        "type": "mc",
        "question": "Welcher Blutzucker-Langzeitwert spiegelt die durchschnittliche Glucosekonzentration der letzten 8–12 Wochen wider?",
        "options": ["MCH", "HbA1c", "Kreatinin", "D-Dimer"],
        "answer": "HbA1c",
        "explanation": "Der HbA1c-Wert (Glykohämoglobin) gibt Auskunft über den durchschnittlichen Blutzuckerspiegel der letzten 2 bis 3 Monate (Lebensdauer der Erythrozyten).",
    },
    {
        "id": 2,
        "area": "Behandlungsassistenz",
        "topic": "Anatomie & Physiologie",
        "type": "text",
        "question": "Nennen Sie die drei harnpflichtigen Substanzen, die über die Niere ausgeschieden werden.",
        "solution": "1. Harnstoff\n2. Harnsäure\n3. Kreatinin",
        "explanation": "Diese Stoffwechselendprodukte müssen zwingend über den Urin ausgeschieden werden. Ein Anstieg im Blut deutet auf eine eingeschränkte Nierenfunktion hin.",
    },
    {
        "id": 3,
        "area": "Behandlungsassistenz",
        "topic": "Hygiene & Sterilisation",
        "type": "mc",
        "question": "Was unterscheidet die Desinfektion von der Sterilisation?",
        "options": [
            "Desinfektion erzielt völlige Keimfreiheit inklusive Sporen.",
            "Desinfektion reduziert Keime (Erregerarmut); Sterilisation bedeutet völlige Keimfreiheit (inkl. Bakteriensporen).",
            "Sterilisation wird ausschließlich chemisch durchgeführt.",
            "Es gibt keinen praktischen Unterschied.",
        ],
        "answer": "Desinfektion reduziert Keime (Erregerarmut); Sterilisation bedeutet völlige Keimfreiheit (inkl. Bakteriensporen).",
        "explanation": "Durch Desinfektion wird biologisches Material in einen Zustand versetzt, dass es nicht mehr infizieren kann (Keimreduktion um mind. 5 Log-Stufen). Sterilisation tötet alle lebenden Mikroorganismen inkl. Sporen ab.",
    },
    {
        "id": 4,
        "area": "Behandlungsassistenz",
        "topic": "Notfall & Diagnostik",
        "type": "mc",
        "question": "Welcher Laborwert dient primär dem Ausschluss einer tiefen Beinvenenthrombose (TVT) bzw. Lungenembolie?",
        "options": ["HbA1c", "D-Dimer", "CRP", "GOT/ALAT"],
        "answer": "D-Dimer",
        "explanation": "D-Dimere sind Fibrinspaltprodukte. Ein negativer D-Dimer-Test schließt ein thromboembolisches Geschehen mit hoher Wahrscheinlichkeit aus.",
    },
    {
        "id": 5,
        "area": "Behandlungsassistenz",
        "topic": "EKG & Herz",
        "type": "text",
        "question": "Wohin wird die EKG-Elektrode V4 bei der Brustwandableitung nach Wilson platziert?",
        "solution": "Im 5. Intercostalraum (ICR) auf der linken Medioclavicularlinie.",
        "explanation": "V1: 4. ICR rechts parasternal; V2: 4. ICR links parasternal; V3: zwischen V2 und V4; V4: 5. ICR Medioclavicularlinie; V5: 5. ICR vordere Axillarlinie; V6: 5. ICR mittlere Axillarlinie.",
    },
    # --- BETRIEBSORGANISATION & ABRECHNUNG ---
    {
        "id": 6,
        "area": "Betriebsorganisation & Abrechnung",
        "topic": "EBM Abrechnung",
        "type": "mc",
        "question": "Welche Voraussetzung muss erfüllt sein, damit die Chronikerpauschale (z. B. GOP 03220) im EBM berechnet werden kann?",
        "options": [
            "Mindestens 1 Kontakt im Quartal bei einer akuten Erkrankung.",
            "Mindestens 1 Arzt-Patienten-Kontakt pro Quartal in mindestens 3 von 4 Quartalen wegen derselben chronischen Erkrankung (4-3-2-Regel).",
            "Einmaliger Befund von Diabetes mellitus ohne Folgekonsultation.",
            "Ausschließlich telefonische Konsultationen über zwei Jahre.",
        ],
        "answer": "Mindestens 1 Arzt-Patienten-Kontakt pro Quartal in mindestens 3 von 4 Quartalen wegen derselben chronischen Erkrankung (4-3-2-Regel).",
        "explanation": "Die Betreuungspauschale für chronisch Kranke erfordert eine kontinuierliche Behandlung (laufendes Quartal + 3 Vorquartale, darin mind. 3 Quartale mit Kontakt, davon mind. 2 persönliche Kontakte).",
    },
    {
        "id": 7,
        "area": "Betriebsorganisation & Abrechnung",
        "topic": "GOÄ Abrechnung",
        "type": "mc",
        "question": "Wie hoch ist der Regelhöchstsatz (Schwellenwert) für persönliche ärztliche Leistungen nach der GOÄ?",
        "options": ["1,8-fach", "2,3-fach", "3,5-fach", "1,15-fach"],
        "answer": "2,3-fach",
        "explanation": "Der Gebührenrahmen für ärztliche Leistungen reicht vom 1,0- bis 3,5-fachen. Der Regelhöchstsatz ohne gesonderte schriftliche Begründung liegt beim 2,3-fachen Satz (technische Leistungen: 1,8-fach, Labor: 1,15-fach).",
    },
    {
        "id": 8,
        "area": "Betriebsorganisation & Abrechnung",
        "topic": "Qualitätsmanagement",
        "type": "text",
        "question": "Wofür steht die Abkürzung PDCA im Qualitätsmanagement und was bedeuten die Phasen?",
        "solution": "P = Plan (Planen)\nD = Do (Durchführen / Umsetzen)\nC = Check (Überprüfen / Kontrollieren)\nA = Act (Anpassen / Agieren)",
        "explanation": "Der PDCA-Zyklus (Demingkreisel) beschreibt den kontinuierlichen Verbesserungsprozess (KVP) im Praxis-Qualitätsmanagement.",
    },
    {
        "id": 9,
        "area": "Betriebsorganisation & Abrechnung",
        "topic": "Formularwesen",
        "type": "mc",
        "question": "Auf welchem Muster-Formular wird eine Verordnung von Häuslicher Krankenpflege ausgestellt?",
        "options": ["Muster 6", "Muster 8", "Muster 12", "Muster 16"],
        "answer": "Muster 12",
        "explanation": "Muster 12 ist die Verordnung häuslicher Krankenpflege. Muster 6 ist der Überweisungsschein, Muster 16 das Arzneiverordnungsblatt (Kassenrezept).",
    },
    # --- WIRTSCHAFTS- UND SOZIALKUNDE ---
    {
        "id": 10,
        "area": "Wirtschafts- & Sozialkunde",
        "topic": "Jugendarbeitsschutzgesetz (JArbSchG)",
        "type": "mc",
        "question": "Wie viele Stunden darf eine 16-jährige MFA-Auszubildende laut § 8 JArbSchG höchstens täglich beschäftigt werden?",
        "options": ["6 Stunden", "8 Stunden", "10 Stunden", "12 Stunden"],
        "answer": "8 Stunden",
        "explanation": "Jugendliche dürfen grundsätzlich nicht mehr als 8 Stunden täglich und nicht mehr als 40 Stunden wöchentlich beschäftigt werden (§ 8 Abs. 1 JArbSchG).",
    },
    {
        "id": 11,
        "area": "Wirtschafts- & Sozialkunde",
        "topic": "BGB Kaufrecht / Sachmangel",
        "type": "text",
        "question": "Welche vorrangigen Rechte hat ein Käufer gemäß § 437 BGB, wenn eine gelieferte Sache einen Sachmangel aufweist?",
        "solution": "Anspruch auf Nacherfüllung (§ 439 BGB):\nWahlweise Mangelbeseitigung (Reparatur) oder Neulieferung einer mangelfreien Sache.",
        "explanation": "Erst nach dem zweimaligen Erfolglossein der Nacherfüllung oder bei Verweigerung greifen nachrangige Rechte wie Rücktritt, Minderung oder Schadensersatz.",
    },
    {
        "id": 12,
        "area": "Wirtschafts- & Sozialkunde",
        "topic": "Arbeitsrecht & Kündigung",
        "type": "mc",
        "question": "Wie lang ist die gesetzliche Probezeit bei einem Berufsausbildungsverhältnis nach § 20 BBiG mindestens und höchstens?",
        "options": [
            "Mindestens 2 Wochen, höchstens 3 Monate.",
            "Mindestens 1 Monat, höchstens 4 Monate.",
            "Mindestens 1 Monat, höchstens 6 Monate.",
            "Immer exakt 6 Monate.",
        ],
        "answer": "Mindestens 1 Monat, höchstens 4 Monate.",
        "explanation": "Im Berufsausbildungsverhältnis beträgt die Probezeit gem. § 20 BBiG mindestens 1 Monat und maximal 4 Monate. (Im regulären Arbeitsvertrag max. 6 Monate nach BGB).",
    },
    {
        "id": 13,
        "area": "Wirtschafts- & Sozialkunde",
        "topic": "Sozialversicherung",
        "type": "mc",
        "question": "Welcher Zweig der gesetzlichen Sozialversicherung wird finanziell zu 100 % allein vom Arbeitgeber getragen?",
        "options": [
            "Krankenversicherung",
            "Rentenversicherung",
            "Unfallversicherung (Berufsgenossenschaft)",
            "Pflegeversicherung",
        ],
        "answer": "Unfallversicherung (Berufsgenossenschaft)",
        "explanation": "Die Beiträge zur gesetzlichen Unfallversicherung (BGW für Arztpraxen) werden vollumfänglich vom Arbeitgeber entrichtet.",
    },
    # --- GEMEINSCHAFTSKUNDE ---
    {
        "id": 14,
        "area": "Gemeinschaftskunde",
        "topic": "Staatsrecht & Grundgesetz",
        "type": "text",
        "question": "Nennen Sie die fünf Grundsätze der Wahl zum Deutschen Bundestag gemäß Art. 38 Grundgesetz.",
        "solution": "1. Allgemein\n2. Unmittelbar\n3. Frei\n4. Gleich\n5. Geheim",
        "explanation": "Diese Wahlgrundsätze sichern die demokratische Legitimation des Deutschen Bundestages.",
    },
    {
        "id": 15,
        "area": "Gemeinschaftskunde",
        "topic": "Gewaltenteilung & Medien",
        "type": "mc",
        "question": "Welche drei klassischen Gewalten werden im System der staatlichen Gewaltenteilung unterschieden?",
        "options": [
            "Presse, Rundfunk, Social Media",
            "Legislative (Gesetzgebung), Exekutive (vollziehende Gewalt), Judikative (Rechtsprechung)",
            "Bundestag, Bundesrat, Bundeskanzleramt",
            "Arbeitgeber, Gewerkschaften, Staat",
        ],
        "answer": "Legislative (Gesetzgebung), Exekutive (vollziehende Gewalt), Judikative (Rechtsprechung)",
        "explanation": "Die Gewaltenteilung schützt vor Machtmissbrauch. Medien werden im Volksmund oft als '4. Gewalt' bezeichnet, da sie eine Kontroll- und Kritikfunktion ausüben.",
    },
]

# Session State Initialization
if "user_score" not in st.session_state:
    st.session_state.user_score = 0
if "answered_questions" not in st.session_state:
    st.session_state.answered_questions = set()
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0


# Main App Layout
st.markdown('<div class="main-header">🩺 MFA Abschlussprüfungstrainer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interaktives Lernmodell auf Basis der Prüfungsaufgaben Baden-Württemberg (2021–2024)</div>', unsafe_allow_html=True)

# Sidebar Navigation & Filters
st.sidebar.title("📌 Navigation & Filter")
app_mode = st.sidebar.radio(
    "Wählen Sie einen Lernmodus:",
    ["📖 Karteikarten / Lernmodus", "📝 Interaktives Quiz", "📊 Themenübersicht & Statistik"]
)

st.sidebar.markdown("---")
area_filter = st.sidebar.selectbox(
    "Prüfungsfach filtern:",
    ["Alle Fächer", "Behandlungsassistenz", "Betriebsorganisation & Abrechnung", "Wirtschafts- & Sozialkunde", "Gemeinschaftskunde"]
)

# Filter Dataset
if area_filter == "Alle Fächer":
    filtered_data = EXAM_DATA
else:
    filtered_data = [q for q in EXAM_DATA if q["area"] == area_filter]


# MODE 1: FLASHCARDS / LERNMODUS
if app_mode == "📖 Karteikarten / Lernmodus":
    st.subheader("📖 Karteikarten-Lernmodus")
    st.info("Nutzen Sie die Karteikarten, um Fachbegriffe, Gesetzestexte und medizinische Abläufe systematisch zu wiederholen.")
    
    if not filtered_data:
        st.warning("Keine Fragen für diesen Filter vorhanden.")
    else:
        card_idx = st.slider("Karteikarte auswählen:", 1, len(filtered_data), 1) - 1
        item = filtered_data[card_idx]
        
        st.markdown(f'<span class="badge">{item["area"]}</span> &nbsp; <span class="badge" style="background-color:#E2E8F0; color:#334155;">{item["topic"]}</span>', unsafe_allow_html=True)
        st.markdown(f"### Frage {card_idx + 1} von {len(filtered_data)}")
        
        with st.container():
            st.markdown(f'<div class="card"><h4>{item["question"]}</h4></div>', unsafe_allow_html=True)
            
            show_ans = st.button("👁️ Antwort / Musterlösung anzeigen", key=f"btn_{item['id']}")
            
            if show_ans:
                st.success("**Musterlösung / Antwort:**")
                if item["type"] == "mc":
                    st.write(f"👉 **{item['answer']}**")
                else:
                    st.markdown(f"```\n{item['solution']}\n```")
                
                st.markdown(f"**Erklärung / Hintergrund:**\n{item['explanation']}")


# MODE 2: INTERAKTIVES QUIZ
elif app_mode == "📝 Interaktives Quiz":
    st.subheader("📝 Prüfungs-Quiz (Selbsttest)")
    
    if not filtered_data:
        st.warning("Keine Fragen für den ausgewählten Fachbereich verfügbar.")
    else:
        q_count = len(filtered_data)
        curr_idx = st.session_state.current_q_index % q_count
        item = filtered_data[curr_idx]
        
        st.progress((curr_idx + 1) / q_count)
        st.caption(f"Frage {curr_idx + 1} von {q_count} | Aktueller Punktestand: {st.session_state.user_score}")
        
        st.markdown(f'<span class="badge">{item["area"]}</span> &nbsp; <b>{item["topic"]}</b>', unsafe_allow_html=True)
        st.markdown(f"### {item['question']}")
        
        if item["type"] == "mc":
            user_choice = st.radio("Wählen Sie die richtige Antwort:", item["options"], key=f"radio_{item['id']}")
            submit_btn = st.button("Antwort überprüfen")
            
            if submit_btn:
                if user_choice == item["answer"]:
                    st.success("✅ Richtig! Hervorragend gewusst.")
                    if item["id"] not in st.session_state.answered_questions:
                        st.session_state.user_score += 10
                        st.session_state.answered_questions.add(item["id"])
                else:
                    st.error(f"❌ Leider falsch. Die richtige Antwort lautet: **{item['answer']}**")
                
                st.info(f"**Erläuterung:** {item['explanation']}")
        
        else: # Free Text Question
            user_text = st.text_area("Ihre Antwort / Stichpunkte eingeben:", key=f"text_{item['id']}")
            submit_text = st.button("Musterlösung vergleichen")
            
            if submit_text:
                st.markdown("**Erwartete Musterlösung:**")
                st.info(item["solution"])
                st.markdown(f"**Hintergrundwissen:** {item['explanation']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Meine Antwort war richtig (+10 Pkt)"):
                        if item["id"] not in st.session_state.answered_questions:
                            st.session_state.user_score += 10
                            st.session_state.answered_questions.add(item["id"])
                            st.rerun()
                with col2:
                    if st.button("👎 Nochmals wiederholen"):
                        pass

        st.markdown("---")
        col_prev, col_next, col_reset = st.columns([1, 1, 2])
        with col_prev:
            if st.button("◀️ Vorherige Frage"):
                st.session_state.current_q_index = (st.session_state.current_q_index - 1) % q_count
                st.rerun()
        with col_next:
            if st.button("Nächste Frage ▶️"):
                st.session_state.current_q_index = (st.session_state.current_q_index + 1) % q_count
                st.rerun()
        with col_reset:
            if st.button("🔄 Quiz-Fortschritt zurücksetzen"):
                st.session_state.user_score = 0
                st.session_state.answered_questions = set()
                st.session_state.current_q_index = 0
                st.rerun()


# MODE 3: STATISTIK & THEMENÜBERSICHT
elif app_mode == "📊 Themenübersicht & Statistik":
    st.subheader("📊 Lernstatistik & Prüfungsstruktur")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Erreichte Punkte", f"{st.session_state.user_score} Pkt")
    col2.metric("Beantwortete Fragen", f"{len(st.session_state.answered_questions)} / {len(EXAM_DATA)}")
    col3.metric("Gesamtdatenbank", f"{len(EXAM_DATA)} Aufgaben")
    
    st.markdown("---")
    st.markdown("### 📋 Verteilung der Themengebiete")
    
    areas = ["Behandlungsassistenz", "Betriebsorganisation & Abrechnung", "Wirtschafts- & Sozialkunde", "Gemeinschaftskunde"]
    for a in areas:
        count = len([q for q in EXAM_DATA if q["area"] == a])
        st.write(f"• **{a}:** {count} Prüfungsfragen hinterlegt")
        
    st.markdown("---")
    st.markdown("""
    **Tipps zur Prüfungsvorbereitung (MFA BW):**
    * **EBM & GOÄ:** Achten Sie auf Kombinationsverbote und Mindestzeiten (z. B. GOP 03230 für 10-Minuten-Gespräch).
    * **Laborwerte:** Lernen Sie Normbereiche für Hb, Leukozyten, Erythrozyten, BZ und HbA1c auswendig.
    * **Rechtskunde:** Achten Sie bei BGB-Sachmängeln stets auf die Vorrangigkeit der Nacherfüllung (§ 439 BGB).
    """)
