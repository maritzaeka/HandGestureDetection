# MediaPipe menyediakan model AI siap pakai untuk deteksi tangan secara real-time, ringan, dan akurat
# --> MediaPipe punya pre-trained deep learning model (Hand Landmarker) mendeteksi 21 landmark tangan

# Karena MediaPipe tidak mengurus kamera dan tampilan layar -> jadi OpenCV digunakan untuk mengakses kamera webcam, mengambil frame video, 
# menampilkan hasil ke layar (imshow), serta menggambar titik landmark pada objek yang terdeteksi.

# NumPy digunakan sebagai representasi data numerik untuk citra dan koordinat landmark yang diproses oleh OpenCV dan MediaPipe.

import cv2
import mediapipe as mp
import numpy as np

# Import pertama menyediakan antarmuka Python untuk MediaPipe Tasks, sedangkan import kedua menyediakan modul vision yang berisi model AI untuk pemrosesan citra.
# cara ngomong ke AI & AI yang bisa lihat
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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
# AKSES KAMERA
# =========================
cap = cv2.VideoCapture(0)

# =========================
# FUNGSI LOGIKA AI (RULE-BASED)
# =========================
def is_hand_open(landmarks):
    """
    Fungsi ini MENENTUKAN apakah tangan terbuka atau tidak
    berdasarkan posisi landmark jari.
    """
    
    # Pasangan landmark:
    # (ujung jari, sendi jari)
    fingers = [
        (8, 6),     # Jari telunjuk
        (12, 10),   # Jari tengah
        (16, 14),   # Jari manis
        (20, 18)    # Jari kelingking
    ]

    open_fingers = 0
    
    # Jika ujung jari lebih tinggi dari sendinya,
    # berarti jari tersebut terbuka
    for tip, pip in fingers:
        if landmarks[tip].y < landmarks[pip].y:
            open_fingers += 1

    # Jika ≥ 4 jari terbuka → tangan dianggap terbuka
    return open_fingers >= 4

# =========================
# LOOP UTAMA (REAL-TIME)
# =========================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # OpenCV pakai BGR, MediaPipe butuh RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Konversi frame ke format MediaPipe Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame_rgb
    )

    # =========================
    # PROSES AI (INFERENCE)
    # =========================
    # Model AI mendeteksi:
    # - Ada tangan atau tidak
    # - Posisi 21 landmark tangan
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        # Ambil landmark tangan pertama
        hand_landmarks = result.hand_landmarks[0]

        # =========================
        # KEPUTUSAN AI
        # =========================
        if is_hand_open(hand_landmarks):
            print("⚠ WARNING: NASABAH MINTA TOLONG")

        # =========================
        # VISUALISASI LANDMARK
        # =========================
        for lm in hand_landmarks:
            x = int(lm.x * frame.shape[1])
            y = int(lm.y * frame.shape[0])
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    cv2.imshow("Hand Detection", frame)
    
    # ESC untuk keluar
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
