from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUT = Path("output/pdf/Jarvis_AI_Hackathon_Report.pdf")


def p(text, style):
    return Paragraph(text, style)


def bullet(text, styles):
    return p(f"- {text}", styles["bullet"])


def section(title, body, styles):
    items = [p(title, styles["h1"]), Spacer(1, 0.12 * cm)]
    for line in body:
        if isinstance(line, tuple):
            items.append(bullet(line[0], styles))
        else:
            items.append(p(line, styles["body"]))
        items.append(Spacer(1, 0.07 * cm))
    items.append(Spacer(1, 0.15 * cm))
    return items


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#CAE8FF"))
    canvas.line(doc.leftMargin, 1.25 * cm, A4[0] - doc.rightMargin, 1.25 * cm)
    canvas.setFillColor(colors.HexColor("#4B6172"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(doc.leftMargin, 0.78 * cm, "Jarvis AI - Hackathon Project Report")
    canvas.drawRightString(A4[0] - doc.rightMargin, 0.78 * cm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4, rightMargin=1.65 * cm, leftMargin=1.65 * cm,
        topMargin=1.5 * cm, bottomMargin=1.65 * cm,
    )
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25,
                                leading=30, alignment=TA_CENTER, textColor=colors.HexColor("#075985"), spaceAfter=10),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontSize=11, leading=15,
                                   alignment=TA_CENTER, textColor=colors.HexColor("#4B6172")),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=15,
                              leading=19, textColor=colors.HexColor("#075985"), spaceBefore=5),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11,
                              leading=14, textColor=colors.HexColor("#0F4C6E")),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=9.4, leading=13,
                               textColor=colors.HexColor("#17212B"), alignment=TA_LEFT),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontSize=9.2, leading=13,
                                 leftIndent=0, firstLineIndent=0, textColor=colors.HexColor("#17212B")),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontSize=8.4, leading=11,
                                textColor=colors.HexColor("#4B6172")),
    }
    story = []

    story += [Spacer(1, 2.1 * cm), p("JARVIS AI", styles["title"]),
              p("Voice-enabled Windows Desktop Assistant | Hackathon Project Report", styles["subtitle"]),
              Spacer(1, 0.7 * cm)]
    cover = [[p("Project Goal", styles["h2"]), p("A desktop assistant that accepts voice or text commands, secures access with face and pattern authentication, and helps users search, chat, remember information, open apps, and communicate faster.", styles["body"])],
             [p("Built With", styles["h2"]), p("Python, Eel, HTML/CSS/JavaScript, SQLite, OpenCV, Groq AI, Firebase (optional), OpenWeather, ADB and WhatsApp.", styles["body"])],
             [p("Presentation Line", styles["h2"]), p("Jarvis AI combines an attractive assistant interface with practical automation and privacy-focused local security.", styles["body"])]]
    t = Table(cover, colWidths=[3.25 * cm, 12.1 * cm], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E0F2FE")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F8FCFF")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9AD6F5")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBEAFE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story += [t, Spacer(1, 0.75 * cm), p("Prepared for college hackathon submission", styles["subtitle"]), PageBreak()]

    story += section("1. Project in Simple Words", [
        "Jarvis AI is a Windows desktop voice assistant. It works like a small personal helper: the user can speak or type a command, and Jarvis identifies the request, performs an action, and shows the answer in the interface.",
        "The project uses a web-like front end inside a desktop application. This gives it a modern visual interface while Python handles the real system actions.",
        "The key differentiator is the secure entry flow: face recognition is checked first, then the user unlocks the app using a 3x3 pattern lock.",
    ], styles)
    story += section("2. Main Features", [
        ("Voice input through microphone using SpeechRecognition."),
        ("Text chat input from the Jarvis interface."),
        ("Face authentication using OpenCV LBPH face recognizer."),
        ("Pattern lock with salted SHA-256 hash; the raw pattern is not stored."),
        ("AI chat through Groq using llama-3.3-70b-versatile."),
        ("Open installed applications or saved websites."),
        ("Play a requested song/video on YouTube."),
        ("Google search and live weather lookup."),
        ("Remember and recall short personal facts from SQLite."),
        ("WhatsApp messaging, WhatsApp call/video call, and Android mobile calling through ADB."),
        ("Chat sessions and history in local SQLite; optional Firebase Firestore cloud sync."),
        ("Modern animated UI, code-answer formatting and copy button for AI code replies."),
    ], styles)
    story += [PageBreak()]

    story += section("3. How the Project Works", [
        "User opens Jarvis -> face camera verifies the user -> pattern lock opens -> user gives a voice or text command -> Python command router selects the right feature -> result is shown on screen and can be spoken aloud.",
        "If no fixed command matches, the message goes to the Groq AI chatbot. The response is displayed and saved to the active chat session.",
    ], styles)
    flow = [[p("Input", styles["h2"]), p("Security", styles["h2"]), p("Command Router", styles["h2"]), p("Action / Output", styles["h2"])],
            [p("Voice or text", styles["body"]), p("Face + pattern", styles["body"]), p("allCommands()", styles["body"]), p("App, web, AI, weather, memory or communication", styles["body"])]]
    ft = Table(flow, colWidths=[3.6 * cm, 3.6 * cm, 4.0 * cm, 5.1 * cm])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F0F9FF")), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9AD6F5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story += [ft, Spacer(1, 0.4 * cm)]
    story += section("4. Code Explanation - File by File", [
        "<b>run.py</b> - Starts the project. It sets the correct working folder and calls <b>main.start()</b>.",
        "<b>main.py</b> - Main desktop app setup. It starts Eel, opens Microsoft Edge in app mode, exposes pattern-lock functions to JavaScript, plays startup sound, and controls face-authentication flow.",
        "<b>engine/command.py</b> - The command control center. <b>takecommand()</b> listens through microphone; <b>allCommands()</b> decides which feature should run; <b>speak()</b> sends messages to UI and optionally speaks them using Windows SAPI.",
        "<b>engine/feature.py</b> - Contains actual actions: opening apps/sites, YouTube, Google, weather, memory, WhatsApp, ADB calls, and Groq AI chat.",
        "<b>engine/pattern_lock.py</b> - Creates, verifies, changes and removes the secure pattern. A unique salt plus SHA-256 hash protects saved pattern data.",
        "<b>engine/auth/recoganize.py</b> - Uses webcam, Haar Cascade face detection and trained LBPH model to verify the saved face.",
        "<b>cloud.py</b> - Makes chat sessions, stores chats in <b>jarvis.db</b>, and optionally syncs unsynced records to Firebase Firestore.",
        "<b>www/</b> - Interface files. <b>index.html</b> gives page structure, <b>style.css</b> gives visual design, <b>main.js</b> sends microphone/text actions, <b>controller.js</b> controls UI and pattern lock, and <b>script.js</b> renders chat history and code blocks.",
        "<b>engine/db.py</b> - SQLite table setup/demo database operations for saved commands, contacts and memory.",
    ], styles)
    story += [PageBreak()]

    story += section("5. Important Code Logic to Explain to Judges", [
        "<b>Command routing:</b> <b>allCommands()</b> checks command keywords in order. For example, 'open chrome' calls <b>openCommand()</b>, 'weather in Delhi' calls the weather function, and unknown/general questions go to <b>chatBot()</b>.",
        "<b>AI fallback:</b> Instead of creating separate rules for every question, general questions are sent to Groq. This makes Jarvis useful beyond fixed commands.",
        "<b>Local-first chat storage:</b> Chat messages are always saved in SQLite. If Firebase credentials are available, the same records sync to cloud; if not, the app still works locally.",
        "<b>Security:</b> The pattern is stored as a hash with a random salt. Face verification is used as the first gate before the pattern screen.",
        "<b>Frontend-backend bridge:</b> Eel connects JavaScript and Python. JavaScript can call Python functions such as <b>eel.allCommands()</b>, and Python can update the UI using <b>eel.DisplayMessage()</b>.",
    ], styles)
    story += section("6. Demo Script (2 to 3 Minutes)", [
        ("Start with: 'This is Jarvis AI, a secure voice-enabled Windows desktop assistant.'"),
        ("Show face recognition, then draw the pattern lock."),
        ("Type or speak: 'open calculator' or 'open youtube'."),
        ("Show AI chat: ask a normal question; then show a code question to demonstrate formatted code and Copy button."),
        ("Say: 'weather in Delhi' after setting OpenWeather API key."),
        ("Say: 'remember my college is [college name]', then ask 'what is my college'."),
        ("Open the chat panel and show previous sessions/history."),
        ("Close with benefit: 'Jarvis brings security, AI conversation, and common desktop/mobile actions into one interface.'"),
    ], styles)
    story += section("7. Setup Before Demo", [
        ("Use Windows with a working webcam, microphone and Microsoft Edge."),
        ("Activate the Python environment and install packages: <b>pip install -r requirements.txt</b>."),
        ("Create a local <b>.env</b> file with GROQ_API_KEY and OPENWEATHER_API_KEY. Never upload this file."),
        ("For cloud history, add Firebase service-account file as <b>firebase_key.json</b>. This is optional."),
        ("For mobile calls, install ADB, enable USB/Wi-Fi debugging on Android, and connect the device first. This is optional."),
        ("Run <b>python run.py</b>. For an executable, run <b>build_app.bat</b>; output is expected at <b>dist/Jarvis/Jarvis.exe</b> after a successful PyInstaller build."),
    ], styles)
    story += [PageBreak()]

    story += section("8. How to Submit the Project", [
        "Create one clean submission folder or GitHub repository. Include source code, README, requirements, presentation PDF, screenshots/video and setup instructions.",
        ("Include: main.py, run.py, engine/, www/, requirements.txt, README.md, FEATURES.md, build_app.bat and this PDF."),
        ("Do NOT upload: .env, firebase_key.json, pattern_lock.json, jarvis.db with personal data, face sample images/trainer if they contain private biometric data, virtual environment folder, and build/cache folders."),
        ("If submitting a GitHub link, add a .gitignore for secrets, local databases, Python virtual environment and generated output."),
        ("Attach a 1 to 3 minute demo video. It helps judges even if the live demo faces network, webcam or API issues."),
        ("For hackathon portal: upload project zip + PDF + demo video link + GitHub link if requested."),
    ], styles)
    story += section("9. Suggested Submission Checklist", [
        ("Test webcam, microphone, face model, pattern lock and internet before submission."),
        ("Keep a backup demo recording and 4 to 6 screenshots."),
        ("Add your name, team name, college and GitHub link to README/PDF if required."),
        ("Confirm API keys are present locally but not committed."),
        ("Explain optional modules honestly: Firebase/ADB need their own configuration."),
        ("If packaging fails, submit source code with exact run steps; do not claim the EXE is included unless it is tested."),
    ], styles)
    story += section("10. Limitations and Future Scope", [
        "Face recognition uses a pre-trained local model and may need retraining for a different user. Voice recognition and cloud features depend on microphone/internet availability. WhatsApp/ADB automation depends on installed apps and connected Android device.",
        "Future improvements: multi-user login, better intent classification, language selection, encrypted local database, reminders/calendar integration, robust error logs, and a packaged installer with first-run setup.",
    ], styles)
    story += [Spacer(1, 0.25 * cm), p("One-line conclusion: Jarvis AI is a practical desktop automation project that combines voice interaction, AI chat, local data, cloud-ready history and layered user security.", styles["h2"])]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)


if __name__ == "__main__":
    main()
