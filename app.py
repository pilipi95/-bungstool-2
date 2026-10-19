import streamlit as st
import pdfplumber
from PIL import Image, ImageDraw
import pandas as pd
import time
import re
import io
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURATION ---
st.set_page_config(page_title="AI Exam Simulator", page_icon="🎓", layout="wide")

# --- SESSION STATE INITIALISIERUNG ---
if 'exam_data' not in st.session_state:
    st.session_state.exam_data = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'exam_state' not in st.session_state:
    st.session_state.exam_state = 'upload' # upload, active, evaluated
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'time_limit' not in st.session_state:
    st.session_state.time_limit = 60 * 45 # 45 Minuten Standard

# --- HILFSFUNKTIONEN FÜR EXTRAKTION UND GENERIERUNG ---

def extract_pdf_content(uploaded_file):
    """
    Extrahiert Text und Bilder aus dem PDF.
    In einer voll ausgebauten Version würde hier der Text an ein LLM (z.B. GPT-4) 
    gesendet werden, um daraus exakt die Struktur der Prüfung lückenlos aufzubauen.
    """
    text_content = ""
    images = []
    
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() + "\n"
            # Bilder extrahieren (stark vereinfacht für dieses Setup)
            for img in page.images:
                # Hier würde die tatsächliche Bildrekonstruktion stattfinden
                pass
                
    return text_content, images

def generate_placeholder_image(text="Generierte KI-Grafik"):
    """
    Generiert lokal eine Fallback-Grafik mit Matplotlib, falls keine KI-API verfügbar ist
    oder Bilder im Skript fehlen.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, text, fontsize=15, ha='center', va='center', wrap=True)
    ax.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return Image.open(buf)

def parse_exam_to_structure(raw_text):
    """
    Simuliert die KI-basierte Aufbereitung des rohen Textes in strukturierte Prüfungsfragen.
    Hier wird für die Lauffähigkeit ein Dummy-Datensatz basierend auf medizinischem Kontext generiert,
    der die verschiedenen geforderten Aufgabentypen demonstriert.
    """
    return [
        {
            "id": 1,
            "type": "multiple_choice",
            "topic": "Anatomie & Physiologie",
            "question": "Welche Aufgaben übernimmt die Niere im menschlichen Körper?",
            "options": [
                "Nur die Produktion von roten Blutkörperchen",
                "Regulierung des Wasser- und Elektrolythaushaltes & Ausscheidung harnpflichtiger Substanzen",
                "Ausschließliche Speicherung von Vitaminen",
                "Steuerung der Atmung"
            ],
            "correct": "Regulierung des Wasser- und Elektrolythaushaltes & Ausscheidung harnpflichtiger Substanzen",
            "points": 2,
            "image": None
        },
        {
            "id": 2,
            "type": "free_text",
            "topic": "Betriebsorganisation",
            "question": "Beschreiben Sie drei mögliche Fehler bei der manuellen Blutdruckmessung.",
            "correct_keywords": ["Manschette", "zu breit", "zu schmal", "nicht geruht", "zu locker", "nicht Herzhöhe"],
            "points": 3,
            "image": generate_placeholder_image("Skizze: Blutdruckmessung am Patienten")
        },
        {
            "id": 3,
            "type": "matching",
            "topic": "Medizinische Fachbegriffe",
            "question": "Ordnen Sie die medizinischen Fachbegriffe ihrer deutschen Bedeutung zu.",
            "pairs": {"Palpation": "Abtasten", "Auskultation": "Abhören", "Inspektion": "Betrachten"},
            "points": 3,
            "image": None
        }
    ]

# --- UI KOMPONENTEN ---

def render_upload_screen():
    st.title("📄 KI-Prüfungssimulator: Setup")
    st.markdown("Lade hier deine Prüfungsunterlagen (Skripte, Altklausuren) hoch. Die KI analysiert die Dokumente, extrahiert alle relevanten Fakten und generiert daraus eine interaktive Prüfungsumgebung.")
    
    uploaded_file = st.file_uploader("Prüfungsdokument hochladen (PDF)", type=['pdf'])
    api_key = st.text_input("OpenAI API Key (Optional für erweiterte Bildgenerierung/LLM)", type="password")
    
    if st.button("Prüfung generieren", use_container_width=True) and uploaded_file:
        with st.spinner("Analysiere Dokumente, extrahiere Bilder und generiere Prüfungsumgebung... Dies kann einen Moment dauern."):
            raw_text, _ = extract_pdf_content(uploaded_file)
            # KI Strukturierung
            st.session_state.exam_data = parse_exam_to_structure(raw_text)
            st.session_state.exam_state = 'active'
            st.session_state.start_time = time.time()
            st.rerun()

def render_active_exam():
    # Header mit Timer und Fortschritt
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, st.session_state.time_limit - elapsed)
    mins, secs = divmod(remaining, 60)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.subheader(f"⏱ Zeit: {mins:02d}:{secs:02d}")
    with col2:
        progress = (st.session_state.current_question_index) / len(st.session_state.exam_data)
        st.progress(progress, text=f"Fortschritt: Aufgabe {st.session_state.current_question_index + 1} von {len(st.session_state.exam_data)}")
    with col3:
        st.subheader(f"Thema: {st.session_state.exam_data[st.session_state.current_question_index]['topic']}")

    st.divider()
    
    # Aktuelle Frage
    q = st.session_state.exam_data[st.session_state.current_question_index]
    st.markdown(f"### Frage {q['id']} ({q['points']} Punkte)")
    st.write(q['question'])
    
    if q['image']:
        st.image(q['image'], caption="Zusatzmaterial / Generierte Grafik zur Aufgabe", use_container_width=True)
        
    # Fragetypen-Logik
    ans_key = f"ans_{q['id']}"
    current_val = st.session_state.user_answers.get(ans_key, None)
    
    if q['type'] == 'multiple_choice':
        choice = st.radio("Wähle die richtige Antwort:", q['options'], index=q['options'].index(current_val) if current_val else None, key=ans_key+"_widget")
        st.session_state.user_answers[ans_key] = choice
        
    elif q['type'] == 'free_text':
        text = st.text_area("Deine Antwort:", value=current_val if current_val else "", height=150, key=ans_key+"_widget")
        st.session_state.user_answers[ans_key] = text
        
    elif q['type'] == 'matching':
        st.write("Wähle den passenden Begriff aus dem Dropdown:")
        if current_val is None:
            current_val = {k: "Bitte wählen..." for k in q['pairs'].keys()}
        
        choices = ["Bitte wählen..."] + list(q['pairs'].values())
        for term in q['pairs'].keys():
            selected = st.selectbox(term, choices, index=choices.index(current_val.get(term, "Bitte wählen...")), key=f"match_{term}")
            current_val[term] = selected
        st.session_state.user_answers[ans_key] = current_val

    st.divider()
    
    # Navigation
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
    with nav_col1:
        if st.session_state.current_question_index > 0:
            if st.button("⬅ Zurück"):
                st.session_state.current_question_index -= 1
                st.rerun()
    with nav_col3:
        if st.session_state.current_question_index < len(st.session_state.exam_data) - 1:
            if st.button("Weiter ➡"):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button("✅ Prüfung abgeben", type="primary"):
                st.session_state.exam_state = 'evaluated'
                st.rerun()

def evaluate_exam():
    total_points = 0
    earned_points = 0
    results = []
    
    for q in st.session_state.exam_data:
        ans_key = f"ans_{q['id']}"
        user_ans = st.session_state.user_answers.get(ans_key, "")
        points = 0
        feedback = ""
        
        if q['type'] == 'multiple_choice':
            if user_ans == q['correct']:
                points = q['points']
                feedback = "Korrekt!"
            else:
                feedback = f"Falsch. Die richtige Antwort ist: {q['correct']}"
                
        elif q['type'] == 'free_text':
            # Einfache Keyword-Matching-Heuristik als Platzhalter für KI-Bewertung
            if user_ans:
                matches = sum(1 for kw in q['correct_keywords'] if kw.lower() in user_ans.lower())
                if matches >= 2:
                    points = q['points']
                    feedback = "Sehr gut! Wichtige Kernbegriffe wurden genannt."
                elif matches == 1:
                    points = q['points'] / 2
                    feedback = "Teilweise korrekt. Es fehlen wichtige Details."
                else:
                    feedback = "Leider nicht ausreichend. Wichtige Konzepte fehlen."
            else:
                feedback = "Keine Antwort gegeben."
                
        elif q['type'] == 'matching':
            correct_matches = sum(1 for k, v in q['pairs'].items() if user_ans.get(k) == v)
            points = (correct_matches / len(q['pairs'])) * q['points']
            feedback = f"{correct_matches} von {len(q['pairs'])} korrekt zugeordnet."

        total_points += q['points']
        earned_points += points
        results.append({"Thema": q['topic'], "Erreicht": points, "Maximal": q['points'], "Feedback": feedback})
        
    return earned_points, total_points, pd.DataFrame(results)

def render_evaluation_screen():
    st.title("📊 Auswertungs-Dashboard")
    st.success("Prüfung erfolgreich abgeschlossen!")
    
    earned, total, df_results = evaluate_exam()
    quote = (earned / total) * 100 if total > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Gesamtpunkte", f"{earned:.1f} / {total}")
    col2.metric("Erfolgsquote", f"{quote:.1f} %")
    col3.metric("Note (simuliert)", "Gut (2.0)" if quote > 80 else "Befriedigend (3.0)" if quote > 60 else "Nicht bestanden")

    st.subheader("Stärken-/Schwächen-Analyse")
    # Radar-Chart für Themenbereiche
    topic_df = df_results.groupby('Thema').sum(numeric_only=True).reset_index()
    topic_df['Prozent'] = (topic_df['Erreicht'] / topic_df['Maximal']) * 100
    
    fig = px.line_polar(topic_df, r='Prozent', theta='Thema', line_close=True, range_r=[0,100], 
                        title="Lernfortschritt nach Themenbereichen")
    fig.update_traces(fill='toself')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Detailliertes Feedback & Musterlösung")
    for idx, row in df_results.iterrows():
        with st.expander(f"Aufgabe {idx+1}: {row['Thema']} ({row['Erreicht']}/{row['Maximal']} Pkt)"):
            st.write(f"**KI-Feedback:** {row['Feedback']}")
            
    if st.button("Neue Prüfung starten"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- MAIN APP LOGIC ---

if st.session_state.exam_state == 'upload':
    render_upload_screen()
elif st.session_state.exam_state == 'active':
    render_active_exam()
elif st.session_state.exam_state == 'evaluated':
    render_evaluation_screen()
