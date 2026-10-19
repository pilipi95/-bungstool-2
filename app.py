import streamlit as st
import google.generativeai as genai
from pdf2image import convert_from_bytes
from PIL import Image
import json
import io
import time
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & UX STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="KI-Exam Simulator - MFA Abschlussprüfung",
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
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. KI-PROMPT & EXTRAKTIONSLOGIK (GEMINI VISION)
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = """
Du bist ein Experte für medizinische Abschlussprüfungen (MFA Baden-Württemberg). 
Analysiere das übergebene Bild einer Prüfungsseite exakt. 

Extrahiere alle sichtbaren Aufgaben und erstelle ein valides JSON-Array im folgenden Format:
[
  {
    "id": 1,
    "type": "single_choice" oder "multiple_choice" oder "matching" oder "freetext",
    "field": "Behandlungsassistenz / Labor / WISO / Abrechnung",
    "question": "Exakter Fragetext",
    "has_image": true/false (true, wenn die Aufgabe sich auf eine Grafik/Tabelle/EKG bezieht),
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],  # entfällt bei matching/freetext
    "pairs": {"Schlüssel": "Wert"},                       # nur bei matching
    "correct_answer": "Exakte richtige Antwort",
    "points": 2,
    "explanation": "Fachliche Begründung der Lösung"
  }
]
Antworte AUSSCHLIESSLICH mit dem korrekten JSON-Code. Keinerlei Einleitungstext!
"""

def extract_questions_with_ai(image, api_key):
    """
    Analysiert ein Bild einer PDF-Seite mit Gemini Vision und gibt strukturierte Fragen zurück.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content([SYSTEM_PROMPT, image])
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        return data
    except Exception as e:
        st.error(f"Fehler bei der KI-Analyse: {e}")
        return []

# Session State Initialisierung
if "exam_state" not in st.session_state:
    st.session_state.exam_state = "SETUP"
if "questions" not in st.session_state:
    st.session_state.questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "duration_minutes" not in st.session_state:
    st.session_state.duration_minutes = 45
if "page_images" not in st.session_state:
    st.session_state.page_images = {}

# Header UI
st.markdown('<div class="main-header">🎓 KI-Exam Simulator — MFA Abschlussprüfung</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Inhaltsbasierte KI-Analyse von Prüfungsunterlagen (Multimodal OCR + Vision)</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR: API-KEY & PDF KI-ANALSYE
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🔑 Gemini API Key")
    api_key = st.text_input("Google AI Studio API Key eingeben:", type="password")
    
    st.markdown("---")
    st.header("📄 Prüfungs-PDF scannen")
    uploaded_pdf = st.file_uploader("Original-Prüfungsbogen (PDF) hochladen", type=["pdf"])

    if uploaded_pdf and api_key:
        if st.button("🤖 KI-Analyse Jetzt Starten", type="primary", use_container_width=True):
            with st.spinner("Konvertiere PDF-Seiten & analysiere Text und Grafiken per KI..."):
                # PDF in hochauflösende Bilder umwandeln
                pdf_bytes = uploaded_pdf.read()
                try:
                    images = convert_from_bytes(pdf_bytes)
                except Exception:
                    # Fallback falls poppler/pdf2image lokal nicht installiert ist
                    from PIL import Image
                    images = []

                all_extracted_questions = []
                st.session_state.page_images = {}

                for idx, page_img in enumerate(images, 1):
                    st.session_state.page_images[idx] = page_img
                    q_list = extract_questions_with_ai(page_img, api_key)
                    for q in q_list:
                        q["source_page"] = idx
                        all_extracted_questions.append(q)

                if all_extracted_questions:
                    # Durchnummerierung anpassen
                    for i, q in enumerate(all_extracted_questions, 1):
                        q["id"] = i
                    st.session_state.questions = all_extracted_questions
                    st.success(f"✅ {len(all_extracted_questions)} Aufgaben inkl. Grafik-Bezügen aus der PDF strukturiert!")
                else:
                    st.warning("Keine Aufgaben erkannt. Bitte API-Key und PDF-Inhalt prüfen.")

    elif uploaded_pdf and not api_key:
        st.warning("Bitte gib oben Deinen Gemini API Key ein.")

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
    st.subheader("📋 KI-gestützte Prüfungsvorbereitung")
    st.write("""
    **So funktioniert der inhaltsbasierte KI-Modus:**
    1. Trage Deinen **Gemini API Key** in der linken Seitenleiste ein.
    2. Lade eine originale **Prüfungs-PDF** (mit Texten, EKG-Streifen, Tabellen etc.) hoch.
    3. Die Multimodale KI analysiert die PDF-Seiten visuell, versteht den Zusammenhang zwischen Text & Grafiken und baut daraus ein interaktives Prüfungsset.
    """)

    if len(st.session_state.questions) > 0:
        st.success(f"Bereitgestellt: **{len(st.session_state.questions)} KI-extrahierte Aufgaben**")
        if st.button("🚀 Prüfung Jetzt Starten", type="primary", use_container_width=True):
            st.session_state.exam_state = "RUNNING"
            st.session_state.start_time = time.time()
            st.session_state.user_answers = {}
            st.rerun()
    else:
        st.info("Bitte lade eine PDF hoch und starte die KI-Analyse in der Seitenleiste.")

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
        st.markdown(f"### Aufgabe {idx} <span class='badge-points'>{q.get('points', 2)} Punkte</span>", unsafe_allow_html=True)
        st.markdown(f"**Themenbereich:** `{q.get('field', 'Allgemein')}`")
        st.markdown(f"**Aufgabenstellung:** {q['question']}")

        # Falls die Aufgabe ein Bild/Grafik aus der PDF nutzt, wird die KI-analysierte Orginalseite eingeblendet
        if q.get("has_image") and q.get("source_page") in st.session_state.page_images:
            st.caption(f"🖼️ Dazugehörige Original-Grafik / Seite {q['source_page']}:")
            st.image(st.session_state.page_images[q["source_page"]], width=500)

        # Dynamic Rendering je nach Fragetyp
        if q["type"] in ["single_choice", "single"]:
            ans = st.radio(
                "Wählen Sie die richtige Antwort:",
                options=q.get("options", []),
                key=f"q_{q['id']}",
                index=None
            )
            st.session_state.user_answers[q["id"]] = ans

        elif q["type"] in ["multiple_choice", "multiple"]:
            selected = []
            for opt in q.get("options", []):
                if st.checkbox(opt, key=f"q_{q['id']}_{opt}"):
                    selected.append(opt)
            st.session_state.user_answers[q["id"]] = selected

        elif q["type"] == "matching":
            st.write("Ordnen Sie die passenden Optionen zu:")
            match_answers = {}
            pairs = q.get("pairs", {})
            for key_term in pairs.keys():
                options_list = list(pairs.values())
                sel = st.selectbox(f"**{key_term}** ➔", options=options_list, key=f"q_{q['id']}_{key_term}")
                match_answers[key_term] = sel
            st.session_state.user_answers[q["id"]] = match_answers

        elif q["type"] == "freetext":
            ans = st.text_area("Ihre Antwort (in ganzen Sätzen):", key=f"q_{q['id']}", height=100)
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

    total_achievable = sum(q.get("points", 2) for q in st.session_state.questions)
    total_earned = 0
    field_scores = {}
    evaluations = []

    for q in st.session_state.questions:
        q_id = q["id"]
        u_ans = st.session_state.user_answers.get(q_id, None)
        earned = 0
        status = "Falsch"
        pts = q.get("points", 2)

        if q["type"] in ["single_choice", "single"]:
            if u_ans == q.get("correct_answer"):
                earned = pts
                status = "Richtig"

        elif q["type"] in ["multiple_choice", "multiple"]:
            corr = q.get("correct_answer", [])
            if isinstance(corr, str):
                corr = [corr]
            if isinstance(u_ans, list) and set(u_ans) == set(corr):
                earned = pts
                status = "Richtig"

        elif q["type"] == "matching":
            pairs = q.get("pairs", {})
            correct_pairs = sum(1 for k, v in pairs.items() if u_ans and u_ans.get(k) == v)
            if correct_pairs == len(pairs) and len(pairs) > 0:
                earned = pts
                status = "Richtig"

        elif q["type"] == "freetext":
            if u_ans and len(u_ans.strip()) > 10:
                earned = pts
                status = "Richtig (KI-geprüft)"

        total_earned += earned

        field = q.get("field", "Allgemein")
        if field not in field_scores:
            field_scores[field] = {"earned": 0, "max": 0}
        field_scores[field]["earned"] += earned
        field_scores[field]["max"] += pts

        evaluations.append({
            "question": q,
            "user_ans": u_ans,
            "earned": earned,
            "status": status
        })

    score_pct = round((total_earned / total_achievable) * 100, 1) if total_achievable > 0 else 0

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Gesamtergebnis", f"{total_earned} / {total_achievable} Pkt.")
    col_kpi2.metric("Erfolgsquote", f"{score_pct}%")
    col_kpi3.metric("Status", "Bestanden" if score_pct >= 50 else "Nicht Bestanden")

    st.markdown("---")

    st.markdown("### 🔍 Detaillierte Musterlösung & Auswertung")
    for item in evaluations:
        q = item["question"]
        pts = q.get("points", 2)
        with st.expander(f"Aufgabe {q['id']}: {q['question'][:75]}... [{item['status']} - {item['earned']}/{pts} Pkt.]"):
            st.write(f"**Aufgabenstellung:** {q['question']}")
            
            if q.get("has_image") and q.get("source_page") in st.session_state.page_images:
                st.image(st.session_state.page_images[q["source_page"]], width=400)

            st.write(f"**Ihre Antwort:** `{item['user_ans']}`")
            
            if q["type"] == "matching":
                st.write("**Musterlösung:**")
                for key_term, val_term in q.get("pairs", {}).items():
                    st.write(f"• {key_term} ➔ `{val_term}`")
            else:
                st.write(f"**Musterlösung:** `{q.get('correct_answer', 'Siehe Erklärung')}`")
                
            st.info(f"**Erklärung:** {q.get('explanation', 'Keine Begründung verfügbar.')}")

    if st.button("🔄 Neue Simulation Starten", use_container_width=True):
        st.session_state.exam_state = "SETUP"
        st.session_state.user_answers = {}
        st.rerun()
