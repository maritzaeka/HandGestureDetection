import ssl
from fastapi import FastAPI, UploadFile, File

# MediaPipe menyediakan model AI siap pakai untuk deteksi tangan secara real-time, ringan, dan akurat
#--> MediaPipe punya pre-trained deep learning model (Hand Landmarker) mendeteksi 21 landmark tangan

# Karena MediaPipe tidak mengurus kamera dan tampilan layar -> jadi OpenCV digunakan untuk mengakses kamera webcam, mengambil frame video, 
#menampilkan hasil ke layar (imshow), serta menggambar titik landmark pada objek yang terdeteksi.

# NumPy digunakan sebagai representasi data numerik untuk citra dan koordinat landmark yang diproses oleh OpenCV dan MediaPipe.

import cv2
import mediapipe as mp
import numpy as np

# Import pertama menyediakan antarmuka Python untuk MediaPipe Tasks, sedangkan import kedua menyediakan modul vision yang berisi model AI untuk pemrosesan citra.
# cara ngomong ke AI & AI yang bisa lihat
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import paho.mqtt.client as mqtt
import time
import os

app = FastAPI(title="ESP32 Hand Open Detection API")


MQTT_BROKER = "192.168.2.140" #wifi kos
# MQTT_BROKER = "mqtt.local"
# MQTT_PORT = 8883
MQTT_PORT = 1883
MQTT_TOPIC = "atm/warn"
MQTT_USERNAME = "backend"
MQTT_PASSWORD = "user"
# CA_CERT_PATH = os.path.join(os.path.dirname(__file__), "ca.crt")

# Buat client biasa
mqtt_client = mqtt.Client(client_id="ai-hand-detector")  # Optional client_id

# Set username/password
# mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# # Set TLS (sertifikat CA)
# mqtt_client.tls_set(
#     ca_certs=CA_CERT_PATH,
#     certfile=None,   # kalau broker gak minta client cert
#     keyfile=None,    # kalau broker gak minta client key
#     tls_version=ssl.PROTOCOL_TLSv1_2
# )
# mqtt_client.tls_insecure_set(True)  # pastikan broker certificate, tls insecure jangan mau -> dicek IPSAN

# Connect & start loop
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()


# =========================
# LOAD MODEL AI
# =========================
# BaseOptions berisi path ke model AI (.task)
# Model ini adalah model deep learning pre-trained dari MediaPipe
base_options = python.BaseOptions(
    model_asset_path="hand_landmarker.task"
)

# HandLandmarkerOptions:
# - Mengatur jumlah tangan yang ingin dideteksi
# - Model ini akan mendeteksi 21 titik landmark pada tangan
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)

# Membuat objek detector (AI inference engine)
detector = vision.HandLandmarker.create_from_options(options)

# =========================
# HAND LOGIC AI LOGIC
# =========================
def is_hand_open(landmarks):
    """
    Fungsi ini MENENTUKAN apakah tangan terbuka atau tidak
    berdasarkan posisi landmark jari.
    """
    # Pasangan landmark:
    # (ujung jari, sendi jari)
    fingers = [
        (8, 6),     # jari telunju
        (12, 10),   # jari tengah
        (16, 14),   # jari manis
        (20, 18)    # jari kelingking
    ]

    open_count = 0
    # Jika ujung jari lebih tinggi dari sendinya,
    # berarti jari tersebut terbuka
    for tip, pip in fingers:
        if landmarks[tip].y < landmarks[pip].y:
            open_count += 1
    # Jika ≥ 4 jari terbuka → tangan dianggap terbuka
    return open_count >= 4

# =========================
# API ENDPOINT
# =========================
# Ini endpoint FastAPI yang bisa diakses lewat POST request
# ESP32-CAM akan kirim satu frame gambar (JPEG) ke sini
@app.post("/detect-hand")
async def detect_hand(file: UploadFile = File(...)):
    """
    Fungsi ini menerima gambar dari ESP32-CAM,
    memeriksa apakah telapak tangan terbuka,
    kalau iya → kirim peringatan lewat MQTT
    """

    # =========================
    # BACA FILE GAMBAR
    # =========================
    # file.read() → baca isi file yang dikirim client (ESP32-CAM)
    contents = await file.read()

    # Convert bytes → OpenCV image
    # =========================
    # KONVERSI FILE KE IMAGE
    # =========================
    # np.frombuffer → ubah bytes jadi array NumPy
    np_img = np.frombuffer(contents, np.uint8)
    # cv2.imdecode → ubah array jadi gambar OpenCV (BGR)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # kalau gambar gagal dibaca → kirim error
    if frame is None:
        return {"status": "error", "message": "Invalid image"}

    # Convert to RGB for MediaPipe
    # =========================
    # PREPARASI UNTUK AI (MediaPipe)
    # =========================
    # OpenCV pakai BGR, MediaPipe pakai RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # ubah frame jadi format MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame_rgb
    )

    # =========================
    # PROSES AI (INFERENCE)
    # =========================
    # detector.detect → cek apakah ada tangan + landmark
    result = detector.detect(mp_image)

    # =========================
    # CEK LOGIKA TANGAN TERBUKA
    # =========================
    if result.hand_landmarks:
        # ambil landmark tangan pertama
        hand_landmarks = result.hand_landmarks[0]

        if is_hand_open(hand_landmarks):
            # Buat payload peringatan untuk MQTT
            payload = {
                "event": "HAND_OPEN",
                "message": "WARNING: NASABAH MINTA TOLONG",
                "timestamp": time.time()
            }

            # Kirim pesan ke broker MQTT
            mqtt_client.publish(MQTT_TOPIC, str(payload))

            # Balikan response ke client (ESP32-CAM) → tangan terbuka
            return {
                "warning": True,
                "message": "Telapak tangan terdeteksi – peringatan dikirim resp api"
            }

    # Kalau tidak ada tangan terbuka → balikan response false
    return {
        "warning": False,
        "message": "No open palm detected"
    }
