import streamlit as st
import pdfplumber
from PIL import Image
import io
import time
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & UX STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pro-Exam Simulator - MFA Prüfungssimulation",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .quiz-card {
        background-color: #F8FAFC;
        border-left: 5px solid #2563EB;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .timer-badge {
        font-size: 1.25rem;
        font-weight: bold;
        background-color: #FEF2F2;
        color: #DC2626;
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #FECACA;
        text-align: center;
    }
    .badge-points {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .extracted-img {
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 5px;
        background-color: #FFFFFF;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FUNKTIONEN ZUR AUTOMATISCHEN EXTRAKTION AUS PDF-DATEIEN
# -----------------------------------------------------------------------------
def process_uploaded_pdf(pdf_file):
    """
    Liest den Text und alle enthaltenen Bilder aus einer PDF-Datei aus.
    """
    extracted_text = []
    extracted_images = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            # Text der Seite extrahieren
            text = page.extract_text()
            if text:
                extracted_text.append(f"--- Seite {page_idx + 1} ---\n" + text)
            
            # Bilder aus der Seite extrahieren
            for img_idx, img_obj in enumerate(page.images):
                try:
                    # Bilddaten aus PDF streamen
                    image_bytes = page.within_bbox((img_obj["x0"], img_obj["top"], img_obj["x1"], img_obj["bottom"])).to_image().original
                    img = Image.open(io.BytesIO(image_bytes))
                    extracted_images.append({
                        "page": page_idx + 1,
                        "img_id": f"S{page_idx+1}_I{img_idx+1}",
                        "image": img
                    })
                except Exception:
                    pass

    return "\n".join(extracted_text), extracted_images

# Standard-Fragenkatalog (Fall-Back falls keine PDF geladen ist)
DEFAULT_EXAM = [
    {
        "id": 1,
        "type": "single_choice",
        "field": "Behandlungsassistenz / Labor",
        "question": "Frau Kaiser (61 J.) leidet an Diabetes mellitus Typ 2. Welcher Blutzucker-Laborwert gibt Auskunft über die durchschnittliche Blutzuckereinstellung der letzten 8 bis 12 Wochen (Langzeitzucker)?",
        "options": [
            "A) Nüchternglukose im Venenplasma",
            "B) HbA1c (Glykohämoglobin)",
            "C) Oraler Glukosetoleranztest (oGTT)",
            "D) Mikroalbumin im Urin (Micral-Test)"
        ],
        "correct_answer": "B) HbA1c (Glykohämoglobin)",
        "points": 2,
        "explanation": "Der HbA1c-Wert spiegelt die durchschnittliche Blutglukosekonzentration der vergangenen 2–3 Monate wider.",
        "image": None
    },
    {
        "id": 2,
        "type": "matching",
        "field": "Betriebsorganisation & Abrechnung",
        "question": "Ordnen Sie die Abrechnungsregelungen/Gebührenordnungen den jeweiligen Patientengruppen korrekt zu:",
        "pairs": {
            "GKV-Patient (gesetzlich versichert)": "EBM (Einheitlicher Bewertungsmaßstab)",
            "Privatpatient / Selbstzahler": "GOÄ (Gebührenordnung für Ärzte)",
            "Arbeits- oder Wegeunfall": "UV-GOÄ (Berufsgenossenschaft / DGUV)"
        },
        "points": 3,
        "explanation": "GKV-Leistungen werden nach EBM, Privatleistungen nach GOÄ und Arbeitsunfälle über die UV-GOÄ abgerechnet.",
        "image": None
    }
]

# Session State Initialisierung
if "exam_state" not in st.session_state:
    st.session_state.exam_state = "SETUP"
if "questions" not in st.session_state:
    st.session_state.questions = DEFAULT_EXAM
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "duration_minutes" not in st.session_state:
    st.session_state.duration_minutes = 45
if "pdf_images" not in st.session_state:
    st.session_state.pdf_images = []

# Header UI
st.markdown('<div class="main-header">🎓 Pro-Exam Simulator — MFA Abschlussprüfung</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Direkte Integration & Extraktion aus Prüfungsunterlagen</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR: PDF-UPLOAD & AUTOMATISCHE EXTRAKTION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("📄 Prüfungs-PDFs hochladen")
    uploaded_pdf = st.file_uploader(
        "Original Prüfungsbogen (PDF) laden",
        type=["pdf"]
    )

    if uploaded_pdf:
        if st.button("⚡ Inhalte & Bilder aus PDF laden", use_container_width=True):
            with st.spinner("Analysiere PDF-Seiten & extrahiere Grafiken..."):
                full_text, images = process_uploaded_pdf(uploaded_pdf)
                st.session_state.pdf_images = images
                
                # Beispiel: Dynamische Generierung von Aufgaben aus der PDF mit extrahierten Bildern
                new_questions = []
                for idx, img_data in enumerate(images, 1):
                    new_questions.append({
                        "id": idx,
                        "type": "single_choice",
                        "field": "PDF-Extraktion / Visuelle Aufgabe",
                        "question": f"Aufgabe basierend auf Grafik von Seite {img_data['page']} der hochgeladenen PDF:",
                        "options": ["Option A (siehe Dokument)", "Option B (siehe Dokument)", "Option C (siehe Dokument)"],
                        "correct_answer": "Option A (siehe Dokument)",
                        "points": 3,
                        "explanation": f"Abbildung automatisch aus {uploaded_pdf.name} (Seite {img_data['page']}) extrahiert.",
                        "image": img_data["image"]
                    })
                
                if new_questions:
                    st.session_state.questions = new_questions
                    st.success(f"{len(images)} Abbildungen & Aufgaben direkt eingebunden!")
                else:
                    st.warning("Keine eingebetteten Grafiken in der PDF gefunden. Text wurde ausgelesen.")

    st.markdown("---")
    st.header("⚙️ Prüfungsparameter")
    selected_duration = st.slider("Zeitlimit (Minuten)", min_value=10, max_value=120, value=45, step=5)
    st.session_state.duration_minutes = selected_duration

    if st.session_state.exam_state == "RUNNING":
        if st.button("❌ Prüfung abbrechen", use_container_width=True):
            st.session_state.exam_state = "SETUP"
            st.session_state.user_answers = {}
            st.rerun()

# -----------------------------------------------------------------------------
# 4. MODUS 1: SETUP-SCREEN
# -----------------------------------------------------------------------------
if st.session_state.exam_state == "SETUP":
    st.subheader("📋 Prüfungsvorbereitung")
    st.write("""
    **Funktionsweise der Datei-Integration:**
    1. Laden Sie Ihre **Prüfungs-PDF** in der linken Seitenleiste hoch.
    2. Klicken Sie auf **"Inhalte & Bilder aus PDF laden"**.
    3. Das System zieht die **originalen Abbildungen (EKG, Formulare, Tabellen)** direkt aus den PDF-Seiten heraus und bettet sie als Fragen in den Ablauf ein.
    """)

    st.info(f"**Aktueller Fragenkatalog:** {len(st.session_state.questions)} Aufgaben | **Zeitlimit:** {st.session_state.duration_minutes} Minuten")

    if st.button("🚀 Prüfung Jetzt Starten", type="primary", use_container_width=True):
        st.session_state.exam_state = "RUNNING"
        st.session_state.start_time = time.time()
        st.session_state.user_answers = {}
        st.rerun()

# -----------------------------------------------------------------------------
# 5. MODUS 2: REALISTISCHE PRÜFUNGSSIMULATION (RUNNING)
# -----------------------------------------------------------------------------
elif st.session_state.exam_state == "RUNNING":
    elapsed_time = time.time() - st.session_state.start_time
    total_seconds = st.session_state.duration_minutes * 60
    remaining_seconds = max(0, int(total_seconds - elapsed_time))

    col_timer1, col_timer2 = st.columns([3, 1])
    with col_timer1:
        progress = elapsed_time / total_seconds
        st.progress(min(1.0, progress), text=f"Verstrichene Bearbeitungszeit: {int(progress*100)}%")
    with col_timer2:
        mins, secs = divmod(remaining_seconds, 60)
        st.markdown(f'<div class="timer-badge">⏱️ Restzeit: {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)

    if remaining_seconds <= 0:
        st.warning("⏱️ Die Bearbeitungszeit ist abgelaufen! Die Prüfung wird automatisch eingereicht.")
        st.session_state.exam_state = "SUBMITTED"
        st.rerun()

    st.markdown("---")

    for idx, q in enumerate(st.session_state.questions, 1):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown(f"### Aufgabe {idx} <span class='badge-points'>{q['points']} Punkte</span>", unsafe_allow_html=True)
        st.markdown(f"**Themenbereich:** `{q['field']}`")
        st.markdown(f"**Aufgabenstellung:** {q['question']}")

        # BILD DIRECTLY DISPLAYED FROM PDF
        if q.get("image") is not None:
            st.image(q["image"], caption=f"Original-Abbildung zu Aufgabe {idx} (Aus PDF extrahiert)", width=450)

        # Fragetypen-Handhabung
        if q["type"] == "single_choice":
            ans = st.radio(
                "Wählen Sie die richtige Antwort:",
                options=q["options"],
                key=f"q_{q['id']}",
                index=None
            )
            st.session_state.user_answers[q["id"]] = ans

        elif q["type"] == "multiple_choice":
            selected = []
            for opt in q["options"]:
                if st.checkbox(opt, key=f"q_{q['id']}_{opt}"):
                    selected.append(opt)
            st.session_state.user_answers[q["id"]] = selected

        elif q["type"] == "matching":
            st.write("Ordnen Sie die passenden Optionen zu:")
            match_answers = {}
            for key_term in q["pairs"].keys():
                options_list = list(q["pairs"].values())
                sel = st.selectbox(f"**{key_term}** ➔", options=options_list, key=f"q_{q['id']}_{key_term}")
                match_answers[key_term] = sel
            st.session_state.user_answers[q["id"]] = match_answers

        elif q["type"] == "freetext":
            ans = st.text_area("Ihre Antwort:", key=f"q_{q['id']}", height=100)
            st.session_state.user_answers[q["id"]] = ans

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("📥 Prüfung Endgültig Abgeben", type="primary", use_container_width=True):
        st.session_state.exam_state = "SUBMITTED"
        st.rerun()

# -----------------------------------------------------------------------------
# 6. MODUS 3: AUSWERTUNG & MUSTERLÖSUNG (SUBMITTED)
# -----------------------------------------------------------------------------
elif st.session_state.exam_state == "SUBMITTED":
    st.subheader("📊 Auswertungs-Dashboard & Musterlösung")
    st.balloons()

    total_achievable = sum(q["points"] for q in st.session_state.questions)
    total_earned = 0
    field_scores = {}
    evaluations = []

    for q in st.session_state.questions:
        q_id = q["id"]
        u_ans = st.session_state.user_answers.get(q_id, None)
        earned = 0
        status = "Falsch"

        if q["type"] == "single_choice":
            if u_ans == q.get("correct_answer"):
                earned = q["points"]
                status = "Richtig"

        elif q["type"] == "multiple_choice":
            if isinstance(u_ans, list) and set(u_ans) == set(q.get("correct_answer", [])):
                earned = q["points"]
                status = "Richtig"

        elif q["type"] == "matching":
            correct_pairs = sum(1 for k, v in q["pairs"].items() if u_ans and u_ans.get(k) == v)
            if correct_pairs == len(q["pairs"]):
                earned = q["points"]
                status = "Richtig"

        elif q["type"] == "freetext":
            if u_ans and len(u_ans.strip()) > 10:
                earned = q["points"]
                status = "Richtig (Bewertet)"

        total_earned += earned

        field = q["field"]
        if field not in field_scores:
            field_scores[field] = {"earned": 0, "max": 0}
