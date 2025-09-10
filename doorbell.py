import cv2
import sqlite3
import pyaudio
import wave
import threading
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
def create_db():
    try:
        conn = sqlite3.connect('smart_doorbell.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS VisitorLog
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           visit_time TEXT NOT NULL)''')
        conn.commit()
        print("Database and table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
    finally:
        conn.close()

#TO STORE THE NAME DATE AND TIME OF ARRIVAL OF THE PERSON WHO RANG THE BELL
def log_visitor(name):
    try:
        conn = sqlite3.connect('smart_doorbell.db')
        cursor = conn.cursor()
        visit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO VisitorLog (name, visit_time) VALUES (?, ?)", (name, visit_time))
        conn.commit()
        print(f"Visitor {name} logged successfully.")
    except sqlite3.Error as e:
        print(f"Error logging visitor: {e}")
    finally:
        conn.close()

# SPEAKING OF THE PERSON WHO ARRIVED AT THE BELL TO BE SENT TO HOUSE OWNER
def record_audio(output_file, record_seconds=5):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2
    fs = 44100
    p = pyaudio.PyAudio()

    print("Recording Audio...")
    stream = p.open(format=sample_format, channels=channels, rate=fs, 
                   frames_per_buffer=chunk, input=True)
    frames = []

    for _ in range(0, int(fs / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Audio saved to {output_file}")

# CAPTARING A SHORT VIDEO  OF THE PERSON WHO ARRIVED AT THE DOOR TO KNOW WHO THEY ARE

def record_video(output_file, record_seconds=20):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 30.0, (640, 420))

    print("Recording Video...")
    start_time = datetime.now()

    while (datetime.now() - start_time).seconds < record_seconds:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Video Recording - Press Q to quit', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video saved to {output_file}")

def send_email(visitor_name, audio_file, video_file):
    sender_email = "coaproject717457@gmail.com"
    recipient_email = "tusyamarsonia@gmail.com"
    app_password = "tjbtdzxeoqhkwmaa"  # DO NOT KEEP GMAIL PASSWORD

    # COMPOSING THE MAIL TO BE SENT 
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Smart Doorbell Alert: {visitor_name} at the Door"

    body = f"""
    Hello,

    {visitor_name} has rung the doorbell.
    Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    Please find the audio and video recordings attached.

    Best regards,
    Your Smart Doorbell System
    """
    msg.attach(MIMEText(body, 'plain'))

    # Function to attach files
    def attach_file(filename):
        with open(filename, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(filename)}'
            )
            msg.attach(part)

    # Attach both files
    try:
        if os.path.exists(audio_file):
            attach_file(audio_file)
        if os.path.exists(video_file):
            attach_file(video_file)
    except Exception as e:
        print(f"Error attaching files: {e}")
        return

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def ring_doorbell(visitor_name):
    print(f"{visitor_name} is at the door!")
    log_visitor(visitor_name)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"{visitor_name}_audio_{timestamp}.wav"
    video_filename = f"{visitor_name}_video_{timestamp}.avi"

    audio_thread = threading.Thread(target=record_audio, args=(audio_filename, 5))
    video_thread = threading.Thread(target=record_video, args=(video_filename, 5))

    audio_thread.start()
    video_thread.start()

    audio_thread.join()
    video_thread.join()

    print("Visitor data recorded.")
    send_email(visitor_name, audio_filename, video_filename)

def show_visitor_logs():
    conn = sqlite3.connect('smart_doorbell.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM VisitorLog")
    rows = cursor.fetchall()
    print("\nVisitor Logs:")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Time: {row[2]}")
    conn.close()


if __name__ == "__main__":  
    
    create_db()
    print("Smart Doorbell System")
    print("-" * 20)
    name = input("Enter visitor name: ")
    ring_doorbell(name)
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
    # SHOW IMAGE BACK TO SCREEN
        cv2.imshow('Image Collection', frame)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    
    show_visitor_logs()
