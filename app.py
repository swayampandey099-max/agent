from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

engine = pyttsx3.init()

SENDER_EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def speak(text):
    engine.say(text)
    engine.runAndWait()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/voice-input', methods=['GET'])
def voice_input():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        speak('Listening')
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return jsonify({'text': text})

    except:
        return jsonify({'text': 'Could not recognize voice'})


@app.route('/send-email', methods=['POST'])
def send_email():
    recipient = request.form['recipient']
    subject = request.form['subject']
    message = request.form['message']

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        # File Attachment
        if 'file' in request.files:
            file = request.files['file']

            if file.filename != '':
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)

                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={file.filename}'
                )

                msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        server.sendmail(
            SENDER_EMAIL,
            recipient,
            msg.as_string()
        )

        server.quit()

        return jsonify({
            'status': 'success',
            'message': 'Email Sent Successfully ✅'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
