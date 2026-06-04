PC2_IP = "192.168.1.50"
UDP_PORT = 8000

# Zone de capture pour l'analyse YOLO (à ajuster selon ta résolution)
CAPTURE_REGION = {
    "top": 800,
    "left": 0,
    "width": 1920,
    "height": 280,
}

# Durée minimale de maintien de TAB pour déclencher l'analyse YOLO (en secondes)
TAB_HOLD_THRESHOLD = 1.0

# Touches de changement de slot
KEY_SLOT_1 = "1"
KEY_SLOT_2 = "2"
KEY_HOLSTER = "3"
KEY_INVENTORY = "tab"

# Seuil de confiance YOLO
YOLO_CONFIDENCE = 0.5
YOLO_MODEL_PATH = "weights/best.pt"
