import random
import tkinter as tk
from tkinter import messagebox, ttk

# ==============================================================================
# FRAGEN- UND FALLBEISPIEL-DATENBANK (AUS DEN ANALYSIERTEN PDFS)
# ==============================================================================

CASES = {
    "udo_abel": {
        "title": "Fallbeispiel 1: Udo Abel (56 J.) - Lebererkrankung / Hepatitis B",
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
    # Behandlungsassistenz - Medizin
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
            "BMI = 100 / (1,70 * 1,70) = 34,6 kg/m².\nBewertung: Adipositas Grad"
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
        "id": "m4",
        "subject": "Behandlungsassistenz (Medizin)",
        "type": "mc",
        "question": (
            "Welche Erste-Hilfe-Maßnahme ist bei Verdacht auf einen akuten"
            " Herzinfarkt korrekt?"
        ),
        "options": [
            "Patienten flach auf den Bauch legen und Beine hochlagern",
            (
                "Oberkörper hochlagern, Notruf 112 absetzen, beengende Kleidung"
                " öffnen"
            ),
            "Sofort Kaltwasser-Güsse durchführen",
            "Patienten intensiv umhergehen lassen",
        ],
        "correct": 1,
        "explanation": (
            "Bei Herzinfarkt entlastet die Lagerung mit erhöhtem Oberkörper das"
            " Herz (Herzentlastung)."
        ),
    },
    # Behandlungsassistenz - Labor
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
        "id": "l2",
        "subject": "Behandlungsassistenz (Labor)",
        "type": "open",
        "question": (
            "Erklären Sie, warum der HbA1c-Wert auch als 'Langzeitzucker'"
            " bezeichnet wird."
        ),
        "correct_answer": (
            "Der HbA1c-Wert gibt die glykierte Hämoglobin-Konzentration an. Da"
            " Erythrozyten eine Lebensdauer von ca. 100 bis 120 Tagen haben,"
            " spiegelt der Wert den durchschnittlichen Blutzuckerspiegel der"
            " letzten 8 bis 12 Wochen wider."
        ),
        "explanation": (
            "Er gibt Aufschluss über die Qualität der Blutzuckereinstellung über"
            " Monate."
        ),
    },
    # Betriebsorganisation & Abrechnung (BOV)
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
        "id": "b2",
        "subject": "Betriebsorganisation & Abrechnung",
        "type": "open",
        "question": (
            "Wie viele Tage ist ein BtM-Rezept (Betäubungsmittelrezept) nach"
            " dem Tag der Ausstellung gültig?"
        ),
        "correct_answer": "8 Tage (inklusive Ausstellungsdatum).",
        "explanation": (
            "Nach § 12 BtMVV dürfen BtM-Rezepte nur innerhalb von 8 Tagen in der"
            " Apotheke eingelöst werden."
        ),
    },
    # Wirtschaftskunde
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
            "Laut § 20 Berufsbildungsgesetz (BBiG) muss die Probezeit"
            " mindestens 1 Monat und darf maximal 4 Monate betragen."
        ),
    },
    {
        "id": "w2",
        "subject": "Wirtschaftskunde",
        "type": "open",
        "question": (
            "Erläutern Sie das Lagerprinzip FIFO (First In - First Out)."
        ),
        "correct_answer": (
            "Waren und Verbrauchsmaterialien, die zuerst eingelagert wurden,"
            " werden auch zuerst verbraucht/ausgelagert."
        ),
        "explanation": (
            "Dies ist essenziell im Praxisbedarf, um das Überschreiten des"
            " Verfallsdatums von Medikamenten zu verhindern."
        ),
    },
    # Gemeinschaftskunde
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
# GUI ANWENDUNGS-KLASSE
# ==============================================================================


class MFAExamApp:

    def __init__(self, root):
        self.root = root
        self.root.title("MFA Abschlussprüfungs-Trainer BW")
        self.root.geometry("900x700")
        self.root.configure(bg="#f4f6f9")

        self.questions = []
        self.current_index = 0
        self.user_answers = {}
        self.time_left = 45 * 60  # 45 Minuten
        self.timer_running = False

        self.setup_styles()
        self.create_dashboard()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure(
            "Primary.TButton", background="#10b981", foreground="white"
        )
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 16, "bold"),
            background="#f4f6f9",
            foreground="#1e293b",
        )

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --------------------------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------------------------
    def create_dashboard(self):
        self.clear_screen()

        title_frame = tk.Frame(self.root, bg="#10b981", py=15)
        title_frame.pack(fill="x")

        lbl_main = tk.Label(
            title_frame,
            text="MFA Abschlussprüfungs-Trainer BW",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#10b981",
        )
        lbl_main.pack()

        main_frame = tk.Frame(self.root, bg="#f4f6f9", px=20, py=20)
        main_frame.pack(fill="both", expand=True)

        lbl_sub = ttk.Label(
            main_frame,
            text="Wählen Sie einen Prüfungsmodus aus:",
            style="Header.TLabel",
        )
        lbl_sub.pack(anchor="w", pady=(0, 15))

        btn_full = tk.Button(
            main_frame,
            text="🏆 Vollständige Examenssimulation (Alle Lernfelder & Fallbeispiele)",
            font=("Segoe UI", 11, "bold"),
            bg="#ecfdf5",
            fg="#047857",
            bd=2,
            relief="groove",
            pady=12,
            command=self.start_full_exam,
        )
        btn_full.pack(fill="x", pady=10)

        lbl_cat = ttk.Label(
            main_frame, text="Einzellernfelder:", style="Header.TLabel"
        )
        lbl_cat.pack(anchor="w", pady=(15, 10))

        subjects = [
            (
                "Gemeinschaftskunde",
                lambda: self.start_subject_exam("Gemeinschaftskunde"),
            ),
            (
                "Wirtschaftskunde",
                lambda: self.start_subject_exam("Wirtschaftskunde"),
            ),
            (
                "Behandlungsassistenz (Medizin)",
                lambda: self.start_subject_exam(
                    "Behandlungsassistenz (Medizin)"
                ),
            ),
            (
                "Behandlungsassistenz (Labor)",
                lambda: self.start_subject_exam("Behandlungsassistenz (Labor)"),
            ),
            (
                "Betriebsorganisation & Abrechnung",
                lambda: self.start_subject_exam(
                    "Betriebsorganisation & Abrechnung"
                ),
            ),
            (
                "Nur Komplex-Fallbeispiele (Udo Abel, Tamara Jahn u.a.)",
                lambda: self.start_subject_exam("cases"),
            ),
        ]

        for text, cmd in subjects:
            btn = ttk.Button(main_frame, text=text, command=cmd)
            btn.pack(fill="x", pady=4)

    # --------------------------------------------------------------------------
    # PRÜFUNGS-LOGIK & TIMER
    # --------------------------------------------------------------------------
    def start_full_exam(self):
        self.questions = QUESTIONS.copy()
        random.shuffle(self.questions)
        self.init_exam()

    def start_subject_exam(self, subject):
        if subject == "cases":
            self.questions = [q for q in QUESTIONS if "case_id" in q]
        else:
            self.questions = [q for q in QUESTIONS if q["subject"] == subject]
        self.init_exam()

    def init_exam(self):
        self.current_index = 0
        self.user_answers = {}
        self.time_left = 45 * 60
        self.timer_running = True
        self.create_exam_ui()
        self.update_timer()

    def update_timer(self):
        if self.timer_running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.lbl_timer.config(
                text=f"Verbleibende Zeit: {mins:02d}:{secs:02d}"
            )
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left <= 0:
            messagebox.showwarning(
                "Zeit abgelaufen", "Die Prüfungszeit ist abgelaufen!"
            )
            self.finish_exam()

    # --------------------------------------------------------------------------
    # PRÜFUNGS-BENUTZEROBERFLÄCHE
    # --------------------------------------------------------------------------
    def create_exam_ui(self):
        self.clear_screen()

        # Header mit Timer
        header_frame = tk.Frame(self.root, bg="#1e293b", py=10, px=15)
        header_frame.pack(fill="x")

        self.lbl_tracker = tk.Label(
            header_frame, text="", font=("Segoe UI", 11), fg="white", bg="#1e293b"
        )
        self.lbl_tracker.pack(side="left")

        self.lbl_timer = tk.Label(
            header_frame,
            text="45:00",
            font=("Segoe UI", 11, "bold"),
            fg="#f59e0b",
            bg="#1e293b",
        )
        self.lbl_timer.pack(side="right")

        # Scrollbarer Hauptbereich
        self.main_container = tk.Frame(self.root, bg="#f4f6f9", px=20, py=15)
        self.main_container.pack(fill="both", expand=True)

        # Fallbeispiel-Box
        self.case_frame = tk.LabelFrame(
            self.main_container,
            text=" Fallbeispiel ",
            font=("Segoe UI", 10, "bold"),
            bg="#f1f5f9",
            fg="#0284c7",
            px=10,
            py=10,
        )

        self.lbl_case_text = tk.Label(
            self.case_frame,
            text="",
            justify="left",
            wraplength=800,
            bg="#f1f5f9",
            font=("Segoe UI", 9),
        )
        self.lbl_case_text.pack(anchor="w")

        # Fragetext
        self.lbl_question = tk.Label(
            self.main_container,
            text="",
            font=("Segoe UI", 12, "bold"),
            wraplength=800,
            justify="left",
            bg="#f4f6f9",
            fg="#0f172a",
        )
        self.lbl_question.pack(anchor="w", pady=(10, 15))

        # Antwort-Bereich
        self.answer_container = tk.Frame(self.main_container, bg="#f4f6f9")
        self.answer_container.pack(fill="x", pady=10)

        # Feedback-Box
        self.feedback_frame = tk.Frame(
            self.main_container, bg="#e2e8f0", px=10, py=10
        )
        self.lbl_feedback = tk.Label(
            self.feedback_frame,
            text="",
            justify="left",
            wraplength=800,
            bg="#e2e8f0",
            font=("Segoe UI", 9.5),
        )
        self.lbl_feedback.pack(anchor="w")

        # Navigations-Buttons
        nav_frame = tk.Frame(self.root, bg="#f4f6f9", px=20, py=15)
        nav_frame.pack(fill="x", side="bottom")

        self.btn_prev = ttk.Button(
            nav_frame, text="Zurück", command=self.prev_question
        )
        self.btn_prev.pack(side="left")

        self.btn_check = ttk.Button(
            nav_frame, text="Antwort prüfen", command=self.check_answer
        )
        self.btn_check.pack(side="left", padx=10)

        self.btn_next = ttk.Button(
            nav_frame, text="Nächste Frage", command=self.next_question
        )
        self.btn_next.pack(side="right")

        self.render_question()

    def render_question(self):
        q = self.questions[self.current_index]

        self.lbl_tracker.config(
            text=(
                f"Frage {self.current_index + 1} von {len(self.questions)} |"
                f" {q['subject']}"
            )
        )
        self.lbl_question.config(text=q["question"])
        self.feedback_frame.pack_forget()

        # Fallbeispiel einblenden falls vorhanden
        if "case_id" in q and q["case_id"] in CASES:
            case_data = CASES[q["case_id"]]
            self.case_frame.config(text=f" {case_data['title']} ")
            self.lbl_case_text.config(text=case_data["text"])
            self.case_frame.pack(fill="x", pady=(0, 15))
        else:
            self.case_frame.pack_forget()

        # Antwortfeld leeren
        for widget in self.answer_container.winfo_children():
            widget.destroy()

        if q["type"] == "mc":
            self.mc_var = tk.IntVar(
                value=self.user_answers.get(self.current_index, -1)
            )
            for idx, opt in enumerate(q["options"]):
                rb = tk.Radiobutton(
                    self.answer_container,
                    text=f"{chr(65+idx)}) {opt}",
                    variable=self.mc_var,
                    value=idx,
                    font=("Segoe UI", 10),
                    bg="#f4f6f9",
                    anchor="w",
                    command=self.save_mc_answer,
                )
                rb.pack(fill="x", pady=4)

        elif q["type"] == "open":
            lbl_hint = tk.Label(
                self.answer_container,
                text="Geben Sie Ihre Antwort ein:",
                bg="#f4f6f9",
            )
            lbl_hint.pack(anchor="w")
            self.txt_open = tk.Text(
                self.answer_container, height=5, font=("Segoe UI", 10)
            )
            self.txt_open.pack(fill="x", pady=5)

            existing_ans = self.user_answers.get(self.current_index, "")
            self.txt_open.insert("1.0", existing_ans)
            self.txt_open.bind("<KeyRelease>", self.save_open_answer)

        self.btn_prev.config(
            state="normal" if self.current_index > 0 else "disabled"
        )
        if self.current_index == len(self.questions) - 1:
            self.btn_next.config(text="Prüfung Beenden")
        else:
            self.btn_next.config(text="Nächste Frage")

    def save_mc_answer(self):
        self.user_answers[self.current_index] = self.mc_var.get()

    def save_open_answer(self, event=None):
        self.user_answers[self.current_index] = self.txt_open.get(
            "1.0", "end-1c"
        )

    def check_answer(self):
        q = self.questions[self.current_index]
        self.feedback_frame.pack(fill="x", pady=10)

        if q["type"] == "mc":
            selected = self.user_answers.get(self.current_index, -1)
            if selected == q["correct"]:
                self.lbl_feedback.config(
                    text=f"Richtig!\n\nErklärung: {q['explanation']}",
                    fg="#15803d",
                )
            else:
                correct_opt = q["options"][q["correct"]]
                self.lbl_feedback.config(
                    text=(
                        f"Falsch. Richtige Antwort: {correct_opt}\n\nErklärung:"
                        f" {q['explanation']}"
                    ),
                    fg="#b91c1c",
                )
        else:
            ans = q["correct_answer"]
            self.lbl_feedback.config(
                text=(
                    f"Musterlösung:\n{ans}\n\nErklärung/Hintergrund:"
                    f" {q['explanation']}"
                ),
                fg="#0f172a",
            )

    def prev_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.render_question()

    def next_question(self):
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.render_question()
        else:
            self.finish_exam()

    # --------------------------------------------------------------------------
    # ERGEBNIS-AUSWERTUNG
    # --------------------------------------------------------------------------
    def finish_exam(self):
        self.timer_running = False
        self.clear_screen()

        correct_count = 0
        total = len(self.questions)

        for idx, q in enumerate(self.questions):
            ans = self.user_answers.get(idx, None)
            if q["type"] == "mc" and ans == q["correct"]:
                correct_count += 1
            elif (
                q["type"] == "open"
                and isinstance(ans, str)
                and len(ans.strip()) > 10
            ):
                correct_count += 1

        percentage = round((correct_count / total) * 100) if total > 0 else 0

        res_frame = tk.Frame(self.root, bg="#f4f6f9", px=20, py=30)
        res_frame.pack(fill="both", expand=True)

        lbl_res_title = ttk.Label(
            res_frame, text="Prüfungsauswertung", style="Header.TLabel"
        )
        lbl_res_title.pack(pady=10)

        lbl_score = tk.Label(
            res_frame,
            text=f"{percentage}%",
            font=("Segoe UI", 36, "bold"),
            fg="#10b981" if percentage >= 50 else "#ef4444",
            bg="#f4f6f9",
        )
        lbl_score.pack()

        status_text = (
            "BESTANDEN" if percentage >= 50 else "NICHT BESTANDEN"
        )
        lbl_status = tk.Label(
            res_frame,
            text=status_text,
            font=("Segoe UI", 14, "bold"),
            fg="#15803d" if percentage >= 50 else "#b91c1c",
            bg="#f4f6f9",
        )
        lbl_status.pack(pady=5)

        lbl_details = tk.Label(
            res_frame,
            text=(
                f"Sie haben {correct_count} von {total} Aufgaben erfolgreich"
                " gelöst."
            ),
            font=("Segoe UI", 11),
            bg="#f4f6f9",
        )
        lbl_details.pack(pady=15)

        btn_back = ttk.Button(
            res_frame,
            text="Zurück zum Hauptmenü",
            command=self.create_dashboard,
        )
        btn_back.pack(pady=20)


# ==============================================================================
# HAUPTPROGRAMM
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = MFAExamApp(root)
    root.mainloop()