import mss
import numpy as np
import cv2
import os
from config import CAPTURE_SLOT_1, CAPTURE_SLOT_2, TEMPLATE_DIR, MATCH_THRESHOLD
from shared_enums import WeaponID

# Cache en RAM : {WeaponID.value -> np.ndarray (template binarisé)}
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


def _capture_region(region: dict) -> np.ndarray:
    with mss.mss() as sct:
        shot = sct.grab(region)
    frame = np.array(shot)
    return cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)


def _match_weapon(region_gray: np.ndarray) -> int:
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
    slot1_id = _match_weapon(_capture_region(CAPTURE_SLOT_1))
    slot2_id = _match_weapon(_capture_region(CAPTURE_SLOT_2))
    return slot1_id, slot2_id
