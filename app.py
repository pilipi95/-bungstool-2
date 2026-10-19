import streamlit as st
import pypdf
from PIL import Image
import io
import time
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
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
    .img-container {
        border: 2px dashed #94A3B8;
        padding: 10px;
        border-radius: 8px;
        background-color: #ffffff;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. ERWEITERTER FRAGENKATALOG (Inklusive Bild-Aufforderungen & Medien)
# -----------------------------------------------------------------------------
MFA_SAMPLE_EXAM = [
    {
        "id": 1,
        "type": "single_choice",
        "field": "Behandlungsassistenz / Labor",
        "question": "Frau Kaiser (61 J.) leidet an Diabetes mellitus Typ 2. Welcher Blutzucker-Laborwert gibt Auskunft über die durchschnittliche Blutzuckereinstellung der letzten 8 bis 12 Wochen (Langzeitzucker)?",
        "image_url": None,
        "options": [
            "A) Nüchternglukose im Venenplasma",
            "B) HbA1c (Glykohämoglobin)",
            "C) Oraler Glukosetoleranztest (oGTT)",
            "D) Mikroalbumin im Urin (Micral-Test)"
        ],
        "correct_answer": "B) HbA1c (Glykohämoglobin)",
        "points": 2,
        "explanation": "Der HbA1c-Wert gibt den Anteil des verzuckerten Hämoglobins an und spiegelt die durchschnittliche Blutglukosekonzentration der vergangenen 2–3 Monate wider."
    },
    {
        "id": 2,
        "type": "image_labeling",
        "field": "Behandlungsassistenz / Anatomie & EKG",
        "question": "Betrachten Sie das untenstehende EKG-Schema. Welcher Welle/Strecke entspricht der Pfeil, der die ventrikuläre Erregungsrückbildung anzeigt?",
        "image_demo": "EKG_SCHEMA",  # Platzhalter für Bildaufruf
        "options": [
            "A) P-Welle",
            "B) QRS-Komplex",
            "C) T-Welle",
            "D) ST-Strecke"
        ],
        "correct_answer": "C) T-Welle",
        "points": 3,
        "explanation": "Die T-Welle entspricht der Erregungsrückbildung (Repolarisation) der Herzkammern."
    },
    {
        "id": 3,
        "type": "multiple_choice",
        "field": "Behandlungsassistenz / Medizin",
        "question": "Welche der folgenden Maßnahmen gehören zur korrekten Durchführung einer manuellen Blutdruckmessung nach Riva-Rocci (RR)? (Wählen Sie alle zutreffenden Aussagen)",
        "image_url": None,
        "options": [
            "A) Der Patient sollte vor der Messung ca. 5 Minuten in Ruhe gesessen haben.",
            "B) Die Manschette muss auf Herzhöhe angelegt werden.",
            "C) Der erste hörbare Korotkow-Ton entspricht dem diastolischen Wert.",
            "D) Beim Entlasten der Manschette markiert das vollständige Verstummen der Töne den diastolischen Wert."
        ],
        "correct_answer": [
            "A) Der Patient sollte vor der Messung ca. 5 Minuten in Ruhe gesessen haben.",
            "B) Die Manschette muss auf Herzhöhe angelegt werden.",
            "D) Beim Entlasten der Manschette markiert das vollständige Verstummen der Töne den diastolischen Wert."
        ],
        "points": 3,
        "explanation": "Der erste hörbare Korotkow-Ton kennzeichnet den SYSTOLISCHEN Wert."
    },
    {
        "id": 4,
        "type": "freetext",
        "field": "Wirtschafts- und Betriebskunde",
        "question": "Eine 17-jährige Auszubildende zur MFA möchte ein E-Bike zum Preis von 2.500 EUR kaufen. Sie hat das Geld gespart. Der Verkäufer weigert sich ohne Zustimmung der Eltern, den Kaufvertrag abzuschließen. Erklären Sie die rechtliche Lage bezüglich der Geschäftsfähigkeit.",
        "image_url": None,
        "correct_answer": "Minderjährige (7 bis 17 Jahre) sind beschränkt geschäftsfähig (§ 106 BGB). Rechtsgeschäfte bedürfen der Einwilligung oder nachträglichen Genehmigung der gesetzlichen Vertreter (§ 107, § 108 BGB).",
        "points": 5,
        "explanation": "Minderjährige benötigen für rechtlich nicht ausschließlich vorteilhafte Verträge dieser Größenordnung die Zustimmung der Erziehungsberechtigten."
    },
    {
        "id": 5,
        "type": "matching",
        "field": "Betriebsorganisation & Abrechnung",
        "question": "Ordnen Sie die Abrechnungsregelungen/Gebührenordnungen den jeweiligen Patientengruppen korrekt zu:",
        "image_url": None,
        "pairs": {
            "GKV-Patient (gesetzlich versichert)": "EBM (Einheitlicher Bewertungsmaßstab)",
            "Privatpatient / Selbstzahler": "GOÄ (Gebührenordnung für Ärzte)",
            "Arbeits- oder Wegeunfall": "UV-GOÄ (Berufsgenossenschaft / DGUV)"
        },
        "points": 3,
        "explanation": "GKV-Leistungen werden nach EBM, Privatleistungen nach GOÄ und Arbeitsunfälle über die UV-GOÄ abgerechnet."
    }
]

# Session State Initialisierung
if "exam_state" not in st.session_state:
    st.session_state.exam_state = "SETUP"
if "questions" not in st.session_state:
    st.session_state.questions = MFA_SAMPLE_EXAM
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "duration_minutes" not in st.session_state:
    st.session_state.duration_minutes = 45
if "uploaded_question_images" not in st.session_state:
    st.session_state.uploaded_question_images = {}

# Header UI
st.markdown('<div class="main-header">🎓 Pro-Exam Simulator — MFA Abschlussprüfung</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interaktive, bildgestützte Prüfungssimulation für Medizinische Fachangestellte</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR: MEDIEN-UPLOAD & DYNAMISCHE BILD-ZUORDNUNG
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🖼️ Aufgaben-Bilder verwalten")
    st.caption("Laden Sie Abbildungen/Grafiken für bestimmte Fragen hoch:")
    
    selected_q_id = st.selectbox(
        "Zuordnung zu Aufgabe:", 
        options=[q["id"] for q in st.session_state.questions],
        format_func=lambda x: f"Aufgabe {x}"
    )
    
    img_file = st.file_uploader(f"Bild für Aufgabe {selected_q_id} hochladen", type=["png", "jpg", "jpeg"])
    if img_file:
        image = Image.open(img_file)
        st.session_state.uploaded_question_images[selected_q_id] = image
        st.success(f"Bild für Aufgabe {selected_q_id} erfolgreich verknüpft!")

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
    st.subheader("📋 Prüfungsvorbereitung & Interaktive Startkonfiguration")
    st.write("""
    **Neue interaktive Features:**
    - 🖼️ **Bildunterstützte Aufgaben**: EKG-Streifen, Laborwerte und Anatomie-Abbildungen direkt in den Aufgaben.
    - 📤 **Eigene Bilder einbinden**: Über die Sidebar können Sie Aufgaben mit eigenen Dokumenten/Grafiken verknüpfen.
    - ⏱️ **Echter Prüfungstimer**: Realistische Zeitmessung unter Prüfungsbedingungen.
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

    # Darstellung der Prüfungsaufgaben
    for idx, q in enumerate(st.session_state.questions, 1):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown(f"### Aufgabe {idx} <span class='badge-points'>{q['points']} Punkte</span>", unsafe_allow_html=True)
        st.markdown(f"**Themenbereich:** `{q['field']}`")
        st.markdown(f"**Aufgabenstellung:** {q['question']}")

        # BILD-INTEGRATION: Prüfung auf verknüpfte Bilder
        q_id = q["id"]
        if q_id in st.session_state.uploaded_question_images:
            st.markdown('<div class="img-container">', unsafe_allow_html=True)
            st.image(st.session_state.uploaded_question_images[q_id], caption=f"Abbildung zu Aufgabe {idx}", width=450)
            st.markdown('</div>', unsafe_allow_html=True)
        elif q.get("image_demo") == "EKG_SCHEMA":
            st.info("💡 *[Beispiel-Grafik eingebunden: EKG-Abschnitt mit P-, QRS- und T-Wellen]*")

        # Fragetypen-Handhabung
        if q["type"] in ["single_choice", "image_labeling"]:
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

        elif q["type"] == "freetext":
            ans = st.text_area(
                "Ihre Antwort (in ganzen Sätzen):",
                key=f"q_{q['id']}",
                height=120
            )
            st.session_state.user_answers[q["id"]] = ans

        elif q["type"] == "matching":
            st.write("Ordnen Sie die passenden Optionen zu:")
            match_answers = {}
            for key_term in q["pairs"].keys():
                options_list = list(q["pairs"].values())
                sel = st.selectbox(f"**{key_term}** ➔", options=options_list, key=f"q_{q['id']}_{key_term}")
                match_answers[key_term] = sel
            st.session_state.user_answers[q["id"]] = match_answers

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

        if q["type"] in ["single_choice", "image_labeling"]:
            if u_ans == q.get("correct_answer"):
                earned = q["points"]
                status = "Richtig"

        elif q["type"] == "multiple_choice":
            if isinstance(u_ans, list) and set(u_ans) == set(q.get("correct_answer", [])):
                earned = q["points"]
                status = "Richtig"
            elif isinstance(u_ans, list) and len(set(u_ans).intersection(set(q.get("correct_answer", [])))) > 0:
                earned = round(q["points"] / 2, 1)
                status = "Teilweise Richtig"

        elif q["type"] == "freetext":
            if u_ans and len(u_ans.strip()) > 15:
                earned = q["points"]
                status = "Richtig (Bewertet)"

        elif q["type"] == "matching":
            correct_pairs = sum(1 for k, v in q["pairs"].items() if u_ans and u_ans.get(k) == v)
            if correct_pairs == len(q["pairs"]):
                earned = q["points"]
                status = "Richtig"
            else:
                earned = round((correct_pairs / len(q["pairs"])) * q["points"], 1)
                status = "Teilweise Richtig"

        total_earned += earned

        field = q["field"]
        if field not in field_scores:
            field_scores[field] = {"earned": 0, "max": 0}
        field_scores[field]["earned"] += earned
        field_scores[field]["max"] += q["points"]

        evaluations.append({
            "question": q,
            "user_ans": u_ans,
            "earned": earned,
            "status": status
        })

    score_pct = round((total_earned / total_achievable) * 100, 1)

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Gesamtergebnis", f"{total_earned} / {total_achievable} Pkt.")
    col_kpi2.metric("Erfolgsquote", f"{score_pct}%")
    col_kpi3.metric("Status", "Bestanden" if score_pct >= 50 else "Nicht Bestanden")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("#### 📈 Erfolgsquote nach Themengebieten")
        df_chart = pd.DataFrame([
            {"Themengebiet": k, "Erreicht (%)": round((v["earned"]/v["max"])*100, 1)}
            for k, v in field_scores.items()
        ])
        fig = px.bar(df_chart, x="Themengebiet", y="Erreicht (%)", color="Erreicht (%)", range_y=[0, 100], color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.markdown("#### 💡 Schwachstellen-Analyse & Empfehlungen")
        for k, v in field_scores.items():
            ratio = v["earned"] / v["max"]
            if ratio < 0.6:
                st.warning(f"⚠️ **{k}**: Wiederholungsbedarf ({round(ratio*100)}%). Vertiefung empfohlen!")
            else:
                st.success(f"✅ **{k}**: Gute Kenntnisse ({round(ratio*100)}%).")

    st.markdown("---")

    st.markdown("### 🔍 Detaillierte Musterlösung & Erklärung")
    for item in evaluations:
        q = item["question"]
        with st.expander(f"Aufgabe {q['id']}: {q['question'][:75]}... [{item['status']} - {item['earned']}/{q['points']} Pkt.]"):
            st.write(f"**Aufgabenstellung:** {q['question']}")
            
            # Bild in Auswertung anzeigen
            q_id = q["id"]
            if q_id in st.session_state.uploaded_question_images:
                st.image(st.session_state.uploaded_question_images[q_id], caption=f"Abbildung zu Aufgabe {q_id}", width=350)

            st.write(f"**Ihre Antwort:** `{item['user_ans']}`")
            
            if q["type"] == "matching":
                st.write("**Musterlösung (Zuordnungen):**")
                for key_term, val_term in q["pairs"].items():
                    st.write(f"• {key_term} ➔ `{val_term}`")
            elif q["type"] == "multiple_choice" and isinstance(q.get("correct_answer"), list):
                correct_str = ", ".join(q["correct_answer"])
                st.write(f"**Musterlösung:** `{correct_str}`")
            else:
                st.write(f"**Musterlösung:** `{q.get('correct_answer', 'Siehe Erklärung')}`")
                
            st.info(f"**Erklärung:** {q['explanation']}")

    if st.button("🔄 Neue Simulation Starten", use_container_width=True):
        st.session_state.exam_state = "SETUP"
        st.session_state.user_answers = {}
        st.rerun()
