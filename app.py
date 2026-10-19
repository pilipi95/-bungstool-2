import random
import streamlit as st

# ==============================================================================
# DATENBANK (Fallbeispiele & Fragen)
# ==============================================================================
CASES = {
    "udo_abel": {
        "title": (
            "Fallbeispiel 1: Udo Abel (56 J.) - Lebererkrankung / Hepatitis B"
        ),
        "text": (
            "Herr Udo Abel (56 J., AOK BW) wechselt nach Umzug in die Praxis Dr."
            " Reutner. Er leidet unter Polyarthrose.\nSymptome: Bauchschmerzen,"
            " Appetitlosigkeit, Müdigkeit, Temp: 38,5°C, leicht gelbliche"
            " Augäpfel.\nLabor/Urin: CRP, großes Blutbild, GOT, GPT, Gamma-GT,"
            " Bilirubin, Hepatitis-Serologie. Urin: bierbraun.\nBefund: Akute"
            " Hepatitis B. Später Einweisung wegen Verdacht auf akutes"
            " Leberversagen."
        ),
    },
    "tamara_jahn": {
        "title": (
            "Fallbeispiel 2: Tamara Jahn (63 J.) - Diabetes Typ 2 & Pneumonie"
        ),
        "text": (
            "Frau Tamara Jahn (170 cm, 100 kg, BMI 34,6) kommt wegen starkem"
            " Husten mit rot-bräunlichem Sputum, Fieber (40°C), Tachykardie"
            " (120/min) und Hypertonie (160/100 mmHg).\nVerdacht auf"
            " bakterielle Pneumonie (Pneumokokken). Später: DMP Diabetes Typ 2"
            " Einschreibung und Belastungs-EKG."
        ),
    },
    "simone_fink": {
        "title": (
            "Fallbeispiel 3: Simone Fink (47 J.) - Cholezystolithiasis &"
            " Cholezystitis"
        ),
        "text": (
            "Frau Simone Fink (170 cm, 82 kg) kommt zur GU und"
            " Hautkrebs-Screening. Später akute Oberbauchschmerzen nach"
            " fettigem Essen, Übelkeit, Druckschmerz unter dem Rippenbogen,"
            " gelbliche Skleren.\nSonografie: Gallenblasensteine,"
            " Wandverdickung. Labor: Leukozytose, CRP-Erhöhung. Kurzinfusion"
            " Novalgin, Notfall-Einweisung per RTW."
        ),
    },
    "petra_kaiser": {
        "title": (
            "Fallbeispiel 4: Petra Kaiser (61 J.) - Diabetischer Fuß &"
            " Nierenkolik"
        ),
        "text": (
            "Frau Petra Kaiser (BMI 34) leidet an Diabetes mellitus und"
            " Hypertonie. Schmerzlose Wunde an der Ferse durch enge Schuhe"
            " (Diabetisches Fußsyndrom).\nSpäter akute krampfartige"
            " Rückenschmerzen mit Ausstrahlung in den Unterbauch"
            " (Nierenkolik durch Harnleiterstein)."
        ),
    },
}

QUESTIONS = [
    {
        "id": "m1",
        "subject": "Behandlungsassistenz (Medizin)",
        "case_id": "udo_abel",
        "type": "mc",
        "question": (
            "Welcher Erreger verursachte bei Herrn Udo Abel die festgestellte"
            " Lebererkrankung mit gelblich gefärbten Augen und bierbraunem Urin?"
        ),
        "options": [
            "Hepatitis A Virus",
            "Hepatitis B Virus",
            "Hepatitis C Virus",
            "Epstein-Barr-Virus",
        ],
        "correct": 1,
        "explanation": (
            "In der Blutserologie wurden HBs-Ag / Anti-HBs nachgewiesen, was"
            " auf eine akute Hepatitis B hinweist."
        ),
    },
    {
        "id": "m2",
        "subject": "Behandlungsassistenz (Medizin)",
        "case_id": "tamara_jahn",
        "type": "open",
        "question": (
            "Berechnen Sie den BMI der Patientin Tamara Jahn (Gewicht: 100 kg,"
            " Größe: 1,70 m) und beurteilen Sie das Ergebnis fachlich."
        ),
        "correct_answer": (
            "BMI = 100 / (1,70 * 1,70) = 34,6 kg/m². Bewertung: Adipositas Grad"
            " I (Fettleibigkeit)."
        ),
        "explanation": (
            "Formel: Gewicht in kg / (Größe in m)². Ab einem BMI von 30 liegt"
            " eine Adipositas vor."
        ),
    },
    {
        "id": "m3",
        "subject": "Behandlungsassistenz (Medizin)",
        "case_id": "simone_fink",
        "type": "mc",
        "question": (
            "Wofür steht die ABCDE-Regel bei der Beurteilung von Pigmentmalen in"
            " der Hautkrebsvorsorge?"
        ),
        "options": [
            "Asymmetrie, Begrenzung, Color (Farbe), Durchmesser, Erhabenheit",
            "Auskultation, Blutdruck, Cholesterin, Diabetes, EKG",
            "Alter, Befund, Diagnose, Empfehlung, Erstversorgung",
            "Allergie, Bakterien, Chromosomen, Dosis, Eiter",
        ],
        "correct": 0,
        "explanation": (
            "Die ABCDE-Regel bewertet Asymmetrie, Begrenzung, Color"
            " (Farbvarianz), Durchmesser (>5mm) und Erhabenheit/Evolutionsverlauf."
        ),
    },
    {
        "id": "l1",
        "subject": "Behandlungsassistenz (Labor)",
        "type": "mc",
        "question": (
            "Welches Blutentnahmeröhrchen wird für die Bestimmung der"
            " Blutsenkungsgeschwindigkeit (BSG) benötigt?"
        ),
        "options": [
            "EDTA-Röhrchen",
            "Serum-Gel-Röhrchen",
            "Natrium-Citrat-Röhrchen (Mischungsverhältnis 1:5)",
            "Natrium-Fluorid-Röhrchen",
        ],
        "correct": 2,
        "explanation": (
            "Für die BSG wird Natrium-Citrat im Mischungsverhältnis 1:5"
            " verwendet."
        ),
    },
    {
        "id": "b1",
        "subject": "Betriebsorganisation & Abrechnung",
        "type": "mc",
        "question": (
            "Welche EBM-Gebührenordnungsposition (GOP) deckt die"
            " Abdomensonografie bei einem GKV-Patienten ab?"
        ),
        "options": ["GOP 03000", "GOP 33042", "GOP 01732", "GOP 03220"],
        "correct": 1,
        "explanation": (
            "GOP 33042 beschreibt im EBM die Ultraschalluntersuchung der"
            " Abdomenorgane."
        ),
    },
    {
        "id": "w1",
        "subject": "Wirtschaftskunde",
        "type": "mc",
        "question": (
            "Wie lange darf die Probezeit in einem Berufsausbildungsverhältnis"
            " nach § 20 BBiG maximal dauern?"
        ),
        "options": ["1 Monat", "3 Monate", "4 Monate", "6 Monate"],
        "correct": 2,
        "explanation": (
            "Laut § 20 BBiG muss die Probezeit mindestens 1 Monat und darf"
            " maximal 4 Monate betragen."
        ),
    },
    {
        "id": "g1",
        "subject": "Gemeinschaftskunde",
        "type": "mc",
        "question": (
            "Welche drei Gewalten bilden das demokratische Prinzip der"
            " Gewaltenteilung?"
        ),
        "options": [
            "Legislative, Exekutive, Judikative",
            "Bundesrat, Bundestag, Bundeskanzler",
            "Presse, Fernsehen, Internet",
            "Arbeitgeber, Gewerkschaften, Staat",
        ],
        "correct": 0,
        "explanation": (
            "Gewaltenteilung gliedert sich in Gesetzgebung (Legislative),"
            " ausführende Gewalt (Exekutive) und Rechtsprechung (Judikative)."
        ),
    },
]

# ==============================================================================
# STREAMLIT APPLIKATION
# ==============================================================================
st.set_page_config(
    page_title="MFA Prüfungstrainer BW", page_icon="🩺", layout="centered"
)

st.title("🩺 MFA Abschlussprüfungs-Trainer Baden-Württemberg")

if "exam_started" not in st.session_state:
    st.session_state.exam_started = False
    st.session_state.current_index = 0
    st.session_state.user_answers = {}
    st.session_state.questions = []

# --- MENÜ / SEITENLEISTE ---
st.sidebar.header("Prüfungsmodus wählen")
mode = st.sidebar.radio(
    "Optionen:",
    [
        "Vollständige Prüfung",
        "Behandlungsassistenz (Medizin)",
        "Behandlungsassistenz (Labor)",
        "Betriebsorganisation & Abrechnung",
        "Wirtschaftskunde",
        "Gemeinschaftskunde",
        "Nur Komplex-Fallbeispiele",
    ],
)

if st.sidebar.button("Prüfung starten / zurücksetzen"):
    if mode == "Vollständige Prüfung":
        q_list = QUESTIONS.copy()
        random.shuffle(q_list)
        st.session_state.questions = q_list
    elif mode == "Nur Komplex-Fallbeispiele":
        st.session_state.questions = [q for q in QUESTIONS if "case_id" in q]
    else:
        st.session_state.questions = [
            q for q in QUESTIONS if q["subject"] == mode
        ]

    st.session_state.exam_started = True
    st.session_state.current_index = 0
    st.session_state.user_answers = {}
    st.rerun()

# --- PRÜFUNGS-ABLAUF ---
if st.session_state.exam_started and st.session_state.questions:
    idx = st.session_state.current_index
    q = st.session_state.questions[idx]

    st.progress((idx + 1) / len(st.session_state.questions))
    st.caption(
        f"Frage {idx + 1} von {len(st.session_state.questions)} | Fach:"
        f" {q['subject']}"
    )

    # Fallbeispiel anzeigen
    if "case_id" in q and q["case_id"] in CASES:
        case = CASES[q["case_id"]]
        with st.expander(f"📋 {case['title']}", expanded=True):
            st.info(case["text"])

    st.subheader(q["question"])

    # Eingabefelder je nach Fragetyp
    if q["type"] == "mc":
        selected_option = st.radio(
            "Wähle eine Antwort:",
            q["options"],
            key=f"q_{idx}",
            index=st.session_state.user_answers.get(idx, None),
        )
        if selected_option:
            st.session_state.user_answers[idx] = q["options"].index(
                selected_option
            )
    else:
        user_text = st.text_area(
            "Deine Antwort:",
            value=st.session_state.user_answers.get(idx, ""),
            key=f"q_{idx}",
        )
        st.session_state.user_answers[idx] = user_text

    # Auswertung / Auflösung der aktuellen Frage
    if st.button("Antwort prüfen"):
        if q["type"] == "mc":
            ans = st.session_state.user_answers.get(idx, None)
            if ans == q["correct"]:
                st.success(f"Richtig! 🎉\n\n**Erklärung:** {q['explanation']}")
            else:
                st.error(
                    f"Falsch. Richtige Antwort: **{q['options'][q['correct']]}**\n\n**Erklärung:**"
                    f" {q['explanation']}"
                )
        else:
            st.warning(
                f"**Musterlösung:**\n{q['correct_answer']}\n\n**Hintergrund:**"
                f" {q['explanation']}"
            )

    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if idx > 0 and st.button("⬅️ Vorherige Frage"):
            st.session_state.current_index -= 1
            st.rerun()

    with col2:
        if idx < len(st.session_state.questions) - 1:
            if st.button("Nächste Frage ➡️"):
                st.session_state.current_index += 1
                st.rerun()
        else:
            if st.button("🏁 Prüfung auswerten"):
                st.session_state.exam_started = False
                st.rerun()

# --- AUSWERTUNG ---
elif not st.session_state.exam_started and st.session_state.questions:
    st.header("🏆 Prüfungsauswertung")

    correct_count = 0
    total = len(st.session_state.questions)

    for i, q in enumerate(st.session_state.questions):
        ans = st.session_state.user_answers.get(i, None)
        if q["type"] == "mc" and ans == q["correct"]:
            correct_count += 1
        elif (
            q["type"] == "open"
            and isinstance(ans, str)
            and len(ans.strip()) > 10
        ):
            correct_count += 1

    percentage = round((correct_count / total) * 100) if total > 0 else 0

    if percentage >= 50:
        st.balloons()
        st.success(
            f"**BESTANDEN!** Du hast {percentage}% erreich ({correct_count} von"
            f" {total} richtig)."
        )
    else:
        st.error(
            f"**NICHT BESTANDEN.** Du hast {percentage}% erreicht ({correct_count}"
            f" von {total} richtig)."
        )

else:
    st.info(
        "Wähle auf der linken Seite einen Prüfungsmodus aus und klicke auf"
        " 'Prüfung starten'."
    )
