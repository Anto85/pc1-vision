import mss
import numpy as np
import cv2
import os
from config import CAPTURE_REGION, TEMPLATE_DIR, MATCH_THRESHOLD
from shared_enums import WeaponID

# Cache en RAM : {WeaponID.value -> np.ndarray (template en niveaux de gris binarisé)}
_templates: dict[int, np.ndarray] = {}


def load_templates() -> None:
    loaded = []
    for weapon in WeaponID:
        if weapon == WeaponID.NONE:
            continue
        path = os.path.join(TEMPLATE_DIR, f"{weapon.name.lower()}.png")
        if not os.path.exists(path):
            continue
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        _, binary = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
        _templates[weapon.value] = binary
        loaded.append(weapon.name)

    print(f"Templates chargés ({len(loaded)}) : {loaded}")


def _match_weapon(region_gray: np.ndarray) -> int:
    """Retourne le WeaponID le plus probable dans la région donnée."""
    _, binary = cv2.threshold(region_gray, 200, 255, cv2.THRESH_BINARY)

    best_score = 0.0
    best_id = WeaponID.NONE

    for weapon_id, template in _templates.items():
        th, tw = template.shape
        rh, rw = binary.shape
        if tw > rw or th > rh:
            continue

        result = cv2.matchTemplate(binary, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val > best_score:
            best_score = max_val
            best_id = weapon_id

    if best_score < MATCH_THRESHOLD:
        return WeaponID.NONE

    return best_id


def detect_weapons() -> tuple[int, int]:
    """
    Capture la zone d'inventaire et retourne (slot1_id, slot2_id).
    L'inventaire est coupé en deux moitiés : gauche = slot 1, droite = slot 2.
    """
    with mss.mss() as sct:
        screenshot = sct.grab(CAPTURE_REGION)
        frame = np.array(screenshot)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)

    mid = gray.shape[1] // 2
    left_region = gray[:, :mid]
    right_region = gray[:, mid:]

    slot1_id = _match_weapon(left_region)
    slot2_id = _match_weapon(right_region)

    return slot1_id, slot2_id
