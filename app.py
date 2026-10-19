import streamlit as st
import json
import random
import time
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MFA Prüfungs-Simulator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.3rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.5rem; }
    .quiz-card { background-color: #F8FAFC; border-left: 5px solid #2563EB; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .timer-badge { font-size: 1.25rem; font-weight: bold; background-color: #FEF2F2; color: #DC2626; padding: 8px 16px; border-radius: 20px; text-align: center; }
    .badge-points { background-color: #EFF6FF; color: #1D4ED8; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. JSON-DATENBANK LADEN
# -----------------------------------------------------------------------------
@st.cache_data
def load_question_pool():
    try:
        with open("fragenpool.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ Die Datei 'fragenpool.json' wurde nicht gefunden. Bitte erstelle die Datei im selben Verzeichnis.")
        return []
    except json.JSONDecodeError:
        st.error("⚠️ Fehler beim Lesen der 'fragenpool.json'. Bitte überprüfe das JSON-Format.")
        return []

full_pool = load_question_pool()

# Session State Initialisierung
if "exam_state" not in st.session_state:
    st.session_state.exam_state = "SETUP"
if "active_questions" not in st.session_state:
    st.session_state.active_questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "duration_minutes" not in st.session_state:
    st.session_state.duration_minutes = 45

# Header UI
st.markdown('<div class="main-header">🎓 Pro-Exam Simulator — MFA Abschlussprüfung</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Dynamischer Fragenpool aus der JSON-Datenbank</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Einstellungen")
    selected_duration = st.slider("Zeitlimit (Minuten)", min_value=10, max_value=120, value=45, step=5)
    st.session_state.duration_minutes = selected_duration

    st.markdown("---")
    st.metric("Gesamtfragen in Datenbank", len(full_pool))

    if st.session_state.exam_state == "RUNNING":
        if st.button("❌ Prüfung abbrechen", use_container_width=True):
            st.session_state.exam_state = "SETUP"
            st.session_state.user_answers = {}
            st.rerun()

# -----------------------------------------------------------------------------
# 4. SETUP-SCREEN
# -----------------------------------------------------------------------------
if st.session_state.exam_state == "SETUP":
    st.subheader("📋 Prüfungsvorbereitung & Konfiguration")
    
    if full_pool:
        all_fields = sorted(list(set(q["field"] for q in full_pool)))
        
        col_cfg1, col_cfg2 = st.columns(2)
        with col_cfg1:
            selected_fields = st.multiselect("Themengebiete auswählen:", options=all_fields, default=all_fields)
        with col_cfg2:
            filtered_pool = [q for q in full_pool if q["field"] in selected_fields]
            max_q = max(1, len(filtered_pool))
            num_questions = st.number_input("Anzahl der Prüfungsfragen:", min_value=1, max_value=max_q, value=min(15, max_q))

        if st.button("🚀 Prüfung Jetzt Starten", type="primary", use_container_width=True):
            st.session_state.active_questions = random.sample(filtered_pool, int(num_questions))
            st.session_state.exam_state = "RUNNING"
            st.session_state.start_time = time.time()
            st.session_state.user_answers = {}
            st.rerun()

# -----------------------------------------------------------------------------
# 5. PRÜFUNGSDURCHFÜHRUNG (RUNNING)
# -----------------------------------------------------------------------------
elif st.session_state.exam_state == "RUNNING":
    elapsed_time = time.time() - st.session_state.start_time
    total_seconds = st.session_state.duration_minutes * 60
    remaining_seconds = max(0, int(total_seconds - elapsed_time))

    col_timer1, col_timer2 = st.columns([3, 1])
    with col_timer1:
        progress = elapsed_time / total_seconds
        st.progress(min(1.0, progress), text=f"Verstrichene Zeit: {int(progress*100)}%")
    with col_timer2:
        mins, secs = divmod(remaining_seconds, 60)
        st.markdown(f'<div class="timer-badge">⏱️ Restzeit: {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)

    if remaining_seconds <= 0:
        st.warning("⏱️ Die Bearbeitungszeit ist abgelaufen!")
        st.session_state.exam_state = "SUBMITTED"
        st.rerun()

    st.markdown("---")

    for idx, q in enumerate(st.session_state.active_questions, 1):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown(f"### Aufgabe {idx} <span class='badge-points'>{q['points']} Punkte</span>", unsafe_allow_html=True)
        st.markdown(f"**Themenbereich:** `{q['field']}`")
        st.markdown(f"**Aufgabenstellung:** {q['question']}")

        if q["type"] == "single_choice":
            ans = st.radio("Wählen Sie eine Antwort:", options=q["options"], key=f"q_{q['id']}", index=None)
            st.session_state.user_answers[q["id"]] = ans

        elif q["type"] == "multiple_choice":
            selected = [opt for opt in q["options"] if st.checkbox(opt, key=f"q_{q['id']}_{opt}")]
            st.session_state.user_answers[q["id"]] = selected

        elif q["type"] == "matching":
            match_answers = {}
            for key_term, correct_v in q["pairs"].items():
                options_list = sorted(list(q["pairs"].values()))
                sel = st.selectbox(f"**{key_term}** ➔", options=options_list, key=f"q_{q['id']}_{key_term}")
                match_answers[key_term] = sel
            st.session_state.user_answers[q["id"]] = match_answers

        elif q["type"] == "freetext":
            ans = st.text_area("Ihre Antwort:", key=f"q_{q['id']}", height=100)
            st.session_state.user_answers[q["id"]] = ans

        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("📥 Prüfung Endgültig Abgeben", type="primary", use_container_width=True):
        st.session_state.exam_state = "SUBMITTED"
        st.rerun()

# -----------------------------------------------------------------------------
# 6. AUSWERTUNG (SUBMITTED)
# -----------------------------------------------------------------------------
elif st.session_state.exam_state == "SUBMITTED":
    st.subheader("📊 Auswertungs-Dashboard & Musterlösung")
    st.balloons()

    total_achievable = sum(q["points"] for q in st.session_state.active_questions)
    total_earned = 0
    field_scores = {}
    evaluations = []

    for q in st.session_state.active_questions:
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
            elif isinstance(u_ans, list) and len(set(u_ans).intersection(set(q.get("correct_answer", [])))) > 0:
                earned = round(q["points"] / 2, 1)
                status = "Teilweise Richtig"

        elif q["type"] == "matching":
            correct_pairs = sum(1 for k, v in q["pairs"].items() if u_ans and u_ans.get(k) == v)
            if correct_pairs == len(q["pairs"]):
                earned = q["points"]
                status = "Richtig"
            else:
                earned = round((correct_pairs / len(q["pairs"])) * q["points"], 1)
                status = "Teilweise Richtig"

        elif q["type"] == "freetext":
            if u_ans and len(u_ans.strip()) > 10:
                earned = q["points"]
                status = "Richtig (Bewertet)"

        total_earned += earned
        field = q["field"]
        if field not in field_scores:
            field_scores[field] = {"earned": 0, "max": 0}
        field_scores[field]["earned"] += earned
        field_scores[field]["max"] += q["points"]

        evaluations.append({"question": q, "user_ans": u_ans, "earned": earned, "status": status})

    score_pct = round((total_earned / total_achievable) * 100, 1) if total_achievable > 0 else 0

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Gesamtergebnis", f"{total_earned} / {total_achievable} Pkt.")
    col_kpi2.metric("Erfolgsquote", f"{score_pct}%")
    col_kpi3.metric("Status", "Bestanden" if score_pct >= 50 else "Nicht Bestanden")

    st.markdown("---")

    # Diagramm
    df_chart = pd.DataFrame([
        {"Themengebiet": k, "Erreicht (%)": round((v["earned"]/v["max"])*100, 1)}
        for k, v in field_scores.items()
    ])
    fig = px.bar(df_chart, x="Themengebiet", y="Erreicht (%)", color="Erreicht (%)", range_y=[0, 100], color_continuous_scale="RdYlGn")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔍 Detailed Solutions")
    for item in evaluations:
        q = item["question"]
        with st.expander(f"Aufgabe {q['id']}: {q['question'][:75]}... [{item['status']}]"):
            st.write(f"**Ihre Antwort:** `{item['user_ans']}`")
            st.write(f"**Musterlösung:** `{q.get('correct_answer', q.get('pairs'))}`")
            st.info(f"**Erklärung:** {q['explanation']}")

    if st.button("🔄 Neue Simulation Starten", use_container_width=True):
        st.session_state.exam_state = "SETUP"
        st.session_state.user_answers = {}
        st.rerun()
