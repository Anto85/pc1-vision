import mss
import numpy as np
from ultralytics import YOLO
from config import CAPTURE_REGION, YOLO_CONFIDENCE, YOLO_MODEL_PATH
from shared_enums import WeaponID

_model = None


def load_model() -> None:
    global _model
    _model = YOLO(YOLO_MODEL_PATH)
    print(f"Modèle YOLO chargé depuis {YOLO_MODEL_PATH}")


def detect_weapons() -> tuple[int, int]:
    """
    Capture l'inventaire et retourne (slot1_id, slot2_id).
    Retourne (WeaponID.NONE, WeaponID.NONE) si aucune arme détectée.
    """
    with mss.mss() as sct:
        screenshot = sct.grab(CAPTURE_REGION)
        frame = np.array(screenshot)

    results = _model(frame, conf=YOLO_CONFIDENCE, verbose=False)[0]

    detected = []
    for box in results.boxes:
        class_name = results.names[int(box.cls)].upper()
        x_center = float(box.xywh[0][0])
        try:
            weapon_id = WeaponID[class_name].value
            detected.append((x_center, weapon_id))
        except KeyError:
            print(f"Arme inconnue détectée par YOLO : {class_name}")

    # Trie par position X (gauche = slot 1, droite = slot 2)
    detected.sort(key=lambda item: item[0])

    slot1 = detected[0][1] if len(detected) > 0 else WeaponID.NONE
    slot2 = detected[1][1] if len(detected) > 1 else WeaponID.NONE

    return slot1, slot2
