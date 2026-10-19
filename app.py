import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & HIGH-CONTRAST UX STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MFA Abschlussprüfung Simulator",
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
# 2. AUTOMATISCHE BILD- UND SCHAUBILD-GENERIERUNG (PIL / Matplotlib)
# -----------------------------------------------------------------------------
def generate_ekg_image():
    """Generiert ein dynamisches EKG-Schema als PIL-Image."""
    fig, ax = plt.subplots(figsize=(6, 2.5))
    x = np.linspace(0, 4 * np.pi, 500)
    y = np.sin(x) * 0.1
    y += 0.3 * np.exp(-((x - 2)**2) / 0.1)      # P-Welle
    y -= 0.4 * np.exp(-((x - 3.8)**2) / 0.02)   # Q-Zacke
    y += 2.0 * np.exp(-((x - 4.0)**2) / 0.02)   # R-Zacke
    y -= 0.6 * np.exp(-((x - 4.2)**2) / 0.02)   # S-Zacke
    y += 0.5 * np.exp(-((x - 5.5)**2) / 0.2)    # T-Welle
    ax.plot(x, y, color='#DC2626', linewidth=2.5)
    ax.set_title("EKG-Schema (Ableitung II)", fontsize=10, fontweight='bold', color='#1E3A8A')
    ax.grid(True, which='both', color='#FECACA', linestyle='--', linewidth=0.5)
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=130)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

def generate_urology_image():
    """Generiert eine vereinfachte Schemazahlentafel der Harnorgane."""
    img = Image.new('RGB', (400, 300), color='#FFFFFF')
    draw = ImageDraw.Draw(img)
    # Nieren
    draw.ellipse([80, 50, 140, 120], fill='#991B1B', outline='black')
    draw.ellipse([260, 50, 320, 120], fill='#991B1B', outline='black')
    # Harnleiter (Ureter)
    draw.line([110, 120, 180, 220], fill='#2563EB', width=4)
    draw.line([290, 120, 220, 220], fill='#2563EB', width=4)
    # Blase
    draw.ellipse([160, 210, 240, 260], fill='#F59E0B', outline='black')
    # Harnröhre (Urethra)
    draw.line([200, 260, 200, 290], fill='#10B981', width=5)
    
    # Beschriftungszahlen
    draw.text((105, 75), "1", fill="white") # Niere
    draw.text((140, 160), "4", fill="black") # Ureter (4)
    draw.text((195, 230), "5", fill="black") # Blase
    draw.text((208, 270), "6", fill="black") # Urethra (6)
    return img

def generate_arm_fracture_image():
    """Generiert ein Unterarm-Knochen-Schema zur Frakturaufgabe."""
    fig, ax = plt.subplots(figsize=(5, 2))
    ax.plot([0.2, 0.8], [0.6, 0.6], color='#4B5563', linewidth=8, label='Humerus (A)')
    ax.plot([0.8, 1.8], [0.7, 0.7], color='#2563EB', linewidth=6, label='Radius (C)')
    ax.plot([0.8, 1.8], [0.5, 0.5], color='#D97706', linewidth=6, label='Ulna (B)')
    ax.scatter([1.8, 1.85, 1.9], [0.6, 0.65, 0.55], color='#059669', s=100, label='Ossa carpi (D)')
    ax.set_title("Schema Unterarmknochen (A: Humerus, B: Ulna, C: Radius, D: Handwurzel)", fontsize=8)
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

# -----------------------------------------------------------------------------
# 3. ANALYSIERTER FRAGENKATALOG (Aus allen Originaldokumenten konsolidiert)
# -----------------------------------------------------------------------------
MFA_EXAM_DATA = [
    # --- BEHANDLUNGSASSISTENZ / MEDIZIN & LABOR ---
    {
        "id": 1,
        "type": "single_choice",
        "field": "Behandlungsassistenz / Labor",
        "question": "Frau Kaiser (61 J.) leidet an Diabetes mellitus Typ 2. Welcher Blutzucker-Laborwert gibt Auskunft über die durchschnittliche Blutzuckereinstellung der letzten 8 bis 12 Wochen (Langzeitzucker)?",
        "image": None,
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
        "type": "single_choice",
        "field": "Behandlungsassistenz / Kardiologie & EKG",
        "question": "Betrachten Sie das vorliegende EKG-Schema. Welche Welle bzw. welcher Komplex stellt die Repolarisation (Erregungsrückbildung) der Herzkammern dar?",
        "image": generate_ekg_image(),
        "options": [
            "A) P-Welle",
            "B) QRS-Komplex",
            "C) T-Welle",
            "D) PQ-Intervall"
        ],
        "correct_answer": "C) T-Welle",
        "points": 3,
        "explanation": "Die T-Welle entspricht der Repolarisation der Ventrikel. Die P-Welle zeigt die Vorhoferregung und der QRS-Komplex die Kammererregung."
    },
    {
        "id": 3,
        "type": "multiple_choice",
        "field": "Behandlungsassistenz / Medizin",
        "question": "Welche der folgenden Maßnahmen gehören zur korrekten Durchführung einer manuellen Blutdruckmessung nach Riva-Rocci (RR)? (Wählen Sie alle zutreffenden Aussagen)",
        "image": None,
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
        "explanation": "Der erste hörbare Korotkow-Ton entspricht dem systolischen Blutdruckwert, nicht dem diastolischen."
    },
    {
        "id": 4,
        "type": "matching",
        "field": "Behandlungsassistenz / Anatomie & Urologie",
        "question": "Ordnen Sie den Nummern im Schema der Harnorgane die passenden medizinischen Fachbegriffe zu:",
        "image": generate_urology_image(),
        "pairs": {
            "Nummer 4 (Ableitender Gang)": "Ureter (Harnleiter)",
            "Nummer 5 (Sammelorgan)": "Harnblase",
            "Nummer 6 (Ausscheidungsgang)": "Urethra (Harnröhre)"
        },
        "points": 3,
        "explanation": "Ureter = Harnleiter (4), Harnblase (5), Urethra = Harnröhre (6)."
    },
    {
        "id": 5,
        "type": "matching",
        "field": "Behandlungsassistenz / Labor / Blutbild",
        "question": "Ordnen Sie die deutschen Bezeichnungen der Blutzellen den jeweiligen Fachbegriffen und Aufgaben zu:",
        "image": None,
        "pairs": {
            "Rote Blutkörperchen": "Erythrozyten (Sauerstofftransport)",
            "Weiße Blutkörperchen": "Leukozyten (Abwehrfunktion)",
            "Blutplättchen": "Thrombozyten (Blutgerinnung)"
        },
        "points": 3,
        "explanation": "Erythrozyten transportieren O2/CO2, Leukozyten dienen der Immunabwehr, Thrombozyten der Blutstillung."
    },
    {
        "id": 6,
        "type": "freetext",
        "field": "Behandlungsassistenz / Wundversorgung & Hygiene",
        "question": "Bei einer Patientin liegt eine Bisswunde am Unterschenkel vor. Erklären Sie, weshalb eine Bisswunde in der Regel primär nicht durch eine Naht verschlossen werden sollte und welche Hygienemaßnahmen beim Verbandswechsel beachtet werden müssen.",
        "image": None,
        "correct_answer": "Bisswunden weisen aufgrund der hohen Keimbesiedlung im Speichel ein extrem hohes Infektionsrisiko auf. Ein primärer Wundverschluss würde Keime einschließen und Abszesse oder Phlegmonen begünstigen. Beim Verbandwechsel gelten sterile Bedingungen, Antiseptik, Händedesinfektion und die Entsorgung von Kanülen/Scharfstoffen in stichfesten Boxen.",
        "points": 4,
        "explanation": "Bisswunden gelten als primär infiziert. Der offene Ablauf von Wundsekret verhindert schwerwiegende Infektionen."
    },
    {
        "id": 7,
        "type": "matching",
        "field": "Behandlungsassistenz / Traumatologie",
        "question": "Ordnen Sie die Buchstabencodes aus dem Schaubild den jeweiligen Armknochen zu:",
        "image": generate_arm_fracture_image(),
        "pairs": {
            "A (Oberarm)": "Humerus",
            "B (Unterarm daumenseitig abgewandt)": "Ulna (Elle)",
            "C (Unterarm daumenseitig)": "Radius (Speiche)",
            "D (Handwurzel)": "Ossa carpi"
        },
        "points": 4,
        "explanation": "A=Humerus, B=Ulna, C=Radius, D=Ossa carpi (Handwurzelknochen)."
    },

    # --- BETRIEBSORGANISATION & ABRECHNUNG ---
    {
        "id": 8,
        "type": "matching",
        "field": "Betriebsorganisation & Abrechnung",
        "question": "Ordnen Sie die Abrechnungsregelungen/Gebührenordnungen den jeweiligen Patientengruppen korrekt zu:",
        "image": None,
        "pairs": {
            "GKV-Patient (gesetzlich versichert)": "EBM (Einheitlicher Bewertungsmaßstab)",
            "Privatpatient / Selbstzahler": "GOÄ (Gebührenordnung für Ärzte)",
            "Arbeits- oder Wegeunfall": "UV-GOÄ (Berufsgenossenschaft / DGUV)"
        },
        "points": 3,
        "explanation": "GKV-Leistungen werden über den EBM, Privatbehandlungen über die GOÄ und Arbeitsunfälle über die UV-GOÄ abgerechnet."
    },
    {
        "id": 9,
        "type": "single_choice",
        "field": "Betriebsorganisation & Abrechnung",
        "question": "Eine GKV-Patientin erhält wegen akuter Beschwerden am 20.03. eine Erstberatung sowie eine sonografische Untersuchung des Abdomens. Welche Gebührenordnungsposition (GOP) deckt das hausärztliche Gespräch ab?",
        "image": None,
        "options": [
            "A) GOP 03000 (Versichertenpauschale)",
            "B) GOP 03230 (Problemorientiertes ärztliches Gespräch)",
            "C) GOP 01410 (Besuchsgebühr)",
            "D) GOP 03220 (Chronikerpauschale)"
        ],
        "correct_answer": "B) GOP 03230 (Problemorientiertes ärztliches Gespräch)",
        "points": 2,
        "explanation": "Die GOP 03230 berechnet das problemorientierte hausärztliche Gespräch je vollendete 10 Minuten."
    },

    # --- WIRTSCHAFTS- UND BETRIEBSKUNDE (WISO) ---
    {
        "id": 10,
        "type": "freetext",
        "field": "Wirtschafts- und Betriebskunde (WISO)",
        "question": "Eine 17-jährige Auszubildende zur MFA möchte ein E-Bike zum Preis von 2.500 EUR kaufen. Sie hat das Geld gespart. Der Verkäufer weigert sich ohne Zustimmung der Eltern, den Kaufvertrag abzuschließen. Erklären Sie die rechtliche Lage bezüglich der Geschäftsfähigkeit.",
        "image": None,
        "correct_answer": "Minderjährige (7 bis 17 Jahre) sind beschränkt geschäftsfähig (§ 106 BGB). Rechtsgeschäfte, die nicht lediglich rechtlich vorteilhaft sind, bedürfen der Einwilligung oder nachträglichen Genehmigung der gesetzlichen Vertreter (§ 107, § 108 BGB). Der 'Taschengeldparagraf' (§ 110 BGB) greift bei Beträgen dieser Höhe i. d. R. nicht ohne Weiteres.",
        "points": 5,
        "explanation": "Minderjährige benötigen für rechtlich nicht ausschließlich vorteilhafte Verträge dieser Größenordnung die schriftliche Zustimmung der Erziehungsberechtigten."
    },
    {
        "id": 11,
        "type": "multiple_choice",
        "field": "Wirtschafts- und Betriebskunde (WISO)",
        "question": "Welche Bestimmungen des Jugendarbeitsschutzgesetzes (JArbSchG) treffen auf 16-jährige Auszubildende zu? (Wählen Sie alle richtigen Antworten)",
        "image": None,
        "options": [
            "A) Tägliche Arbeitszeit darf maximal 8 Stunden (bzw. 8,5 Std. bei Ausgleich) betragen.",
            "B) Samstagsarbeit ist grundsätzlich erlaubt ohne Ruhetagsausgleich.",
            "C) Bei mehr als 6 Stunden Arbeitszeit steht eine Pause von mindestens 60 Minuten zu.",
            "D) Der Urlaubsanspruch beträgt mindestens 27 Werktage, wenn der Jugendliche zu Beginn des Jahres noch nicht 17 Jahre alt ist."
        ],
        "correct_answer": [
            "A) Tägliche Arbeitszeit darf maximal 8 Stunden (bzw. 8,5 Std. bei Ausgleich) betragen.",
            "C) Bei mehr als 6 Stunden Arbeitszeit steht eine Pause von mindestens 60 Minuten zu.",
            "D) Der Urlaubsanspruch beträgt mindestens 27 Werktage, wenn der Jugendliche zu Beginn des Jahres noch nicht 17 Jahre alt ist."
        ],
        "points": 3,
        "explanation": "Für Jugendliche gilt die 5-Tage-Woche sowie Samstagsruhe (§ 15, § 16 JArbSchG)."
    },

    # --- GEMEINSCHAFTSKUNDE ---
    {
        "id": 12,
        "type": "multiple_choice",
        "field": "Gemeinschaftskunde",
        "question": "Welche der folgenden Wahlgrundsätze sind in Art. 38 des Grundgesetzes (GG) für Wahlen zum Deutschen Bundestag verankert? (Wählen Sie alle zutreffenden Aussagen)",
        "image": None,
        "options": [
            "A) Allgemein (alle Staatsbürger ab 18 Jahren dürfen wählen)",
            "B) Unmittelbar (direkte Wahl ohne Wahlmänner)",
            "C) Verpflichtend (Wahlpflicht für alle Bürger)",
            "D) Geheim (unbeeinflusste, verdeckte Stimmabgabe)"
        ],
        "correct_answer": [
            "A) Allgemein (alle Staatsbürger ab 18 Jahren dürfen wählen)",
            "B) Unmittelbar (direkte Wahl ohne Wahlmänner)",
            "D) Geheim (unbeeinflusste, verdeckte Stimmabgabe)"
        ],
        "points": 3,
        "explanation": "Die Wahlen in Deutschland sind allgemein, unmittelbar, frei, gleich und geheim. Eine Wahlpflicht gibt es in Deutschland nicht."
    }
]

# Session State Initialisierung
if "exam_state" not in st.session_state:
    st.session_state.exam_state = "SETUP"
if "questions" not in st.session_state:
    st.session_state.questions = MFA_EXAM_DATA
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "duration_minutes" not in st.session_state:
    st.session_state.duration_minutes = 45

# Header UI
st.markdown('<div class="main-header">🎓 Pro-Exam Simulator — MFA Abschlussprüfung</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interaktive Prüfungssimulation mit integrierten Bild- und Textaufgaben aus den Prüfungsjahrgängen</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. SIDEBAR CONFIGURATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Prüfungsparameter")
    selected_duration = st.slider("Zeitlimit (Minuten)", min_value=10, max_value=120, value=45, step=5)
    st.session_state.duration_minutes = selected_duration

    st.markdown("---")
    st.info(f"**Geladene Aufgaben:** {len(st.session_state.questions)}\n\nIntegrierte Themenbereiche:\n- Behandlungsassistenz & Labor\n- Kardiologie & Urologie\n- Betriebsorganisation & EBM/GOÄ\n- WISO & Gesetzestexte\n- Gemeinschaftskunde")

    if st.session_state.exam_state == "RUNNING":
        if st.button("❌ Prüfung abbrechen", use_container_width=True):
            st.session_state.exam_state = "SETUP"
            st.session_state.user_answers = {}
            st.rerun()

# -----------------------------------------------------------------------------
# 5. MODUS 1: SETUP-SCREEN
# -----------------------------------------------------------------------------
if st.session_state.exam_state == "SETUP":
    st.subheader("📋 Prüfungsvorbereitung & Startkonfiguration")
    st.write("""
    Diese Anwendung simuliert die **MFA-Abschlussprüfung (Baden-Württemberg)** unter realistischen Prüfungsbedingungen basierend auf den aktuellen Aufgabenkatalogen.
    
    **Highlights:**
    - 🖼️ **Integrierte Schaubilder & Anatomie**: EKG-Streifen, Organ-Schemata, Knochenstruktur & Laborwerte.
    - ⏱️ **Echter Timer**: Exakte Zeiterfassung mit Warnung bei Ablauf.
    - 📊 **Auswertungs-Dashboard**: Automatische Punkteberechnung, Musterlösungen und Aufschlüsselung nach Themengebieten.
    """)

    if st.button("🚀 Prüfung Jetzt Starten", type="primary", use_container_width=True):
        st.session_state.exam_state = "RUNNING"
        st.session_state.start_time = time.time()
        st.session_state.user_answers = {}
        st.rerun()

# -----------------------------------------------------------------------------
# 6. MODUS 2: REALISTISCHE PRÜFUNGSSIMULATION (RUNNING)
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

        # Bildanzeige falls in der Aufgabe definiert
        if q.get("image") is not None:
            st.image(q["image"], caption=f"Abbildung zu Aufgabe {idx}", width=450)

        # Dynamisches Rendering je nach Fragetyp
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
            ans = st.text_area("Ihre Antwort (in ganzen Sätzen):", key=f"q_{q['id']}", height=100)
            st.session_state.user_answers[q["id"]] = ans

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("📥 Prüfung Endgültig Abgeben", type="primary", use_container_width=True):
        st.session_state.exam_state = "SUBMITTED"
        st.rerun()

# -----------------------------------------------------------------------------
# 7. MODUS 3: AUSWERTUNG & MUSTERLÖSUNG (SUBMITTED)
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
        st.markdown("#### 💡 Schwachstellen-Analyse")
        for k, v in field_scores.items():
            ratio = v["earned"] / v["max"]
            if ratio < 0.6:
                st.warning(f"⚠️ **{k}**: Wiederholungsbedarf ({round(ratio*100)}%). Vertiefung empfohlen!")
            else:
                st.success(f"✅ **{k}**: Gute Kenntnisse ({round(ratio*100)}%).")

    st.markdown("---")

    st.markdown("### 🔍 Detaillierte Musterlösung & Auswertung")
    for item in evaluations:
        q = item["question"]
        with st.expander(f"Aufgabe {q['id']}: {q['question'][:75]}... [{item['status']} - {item['earned']}/{q['points']} Pkt.]"):
            st.write(f"**Aufgabenstellung:** {q['question']}")
            
            if q.get("image") is not None:
                st.image(q["image"], caption="Zugehörige Abbildung", width=350)

            st.write(f"**Ihre Antwort:** `{item['user_ans']}`")
            
            if q["type"] == "matching":
                st.write("**Musterlösung:**")
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
