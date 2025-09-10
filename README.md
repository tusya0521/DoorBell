# 🛎️ Smart Doorbell System  

## 📖 Overview  
The Smart Doorbell System is an intelligent IoT-based application that captures and logs visitor information whenever the doorbell is activated. It integrates **video, audio, and database logging** with **real-time email notifications** to keep the homeowner informed.  

---

## ✨ Features  
- 📅 **Visitor Logging** – Stores visitor name, date, and time in a local SQLite database.  
- 🎙️ **Audio Recording** – Captures a short audio message from the visitor (default: 5 seconds).  
- 📹 **Video Recording** – Records a short video clip of the visitor (default: 20 seconds).  
- 📧 **Email Alerts** – Sends visitor details along with audio/video attachments to the homeowner’s email.  
- 🗄️ **Persistent Logs** – Maintains a database of all past visitor entries for historical review.  
- 🖥️ **Live Camera Feed** – Displays a live webcam feed until terminated.  

---

## 🏗️ How It Works  
1. When a visitor rings the doorbell, the system prompts for their name.  
2. The system:  
   - Logs the visitor’s **name, date, and time** into `smart_doorbell.db`.  
   - Records a **short audio message** and a **video clip** of the visitor.  
   - Sends an **email notification** with the recordings attached.  
3. All visitor logs can be displayed later from the database.  

---

## 📂 Data Collection Workflow  
- **Database (SQLite3):** Stores visitor logs in the `VisitorLog` table.  
- **Audio Files (.wav):** Captured using `PyAudio` and saved locally.  
- **Video Files (.avi):** Captured via OpenCV and saved locally.  
- **Email Notifications:** Sent using Gmail SMTP with attachments (audio + video).  

---

## ⚙️ Requirements  
Install dependencies before running the program:  

```bash
pip install opencv-python pyaudio
