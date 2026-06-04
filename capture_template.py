"""
Outil de capture de templates pour le template matching.

Usage :
  1. Lance le script
  2. Dans Apex, équipe l'arme voulue et ouvre l'inventaire (TAB)
  3. Appuie sur F8 — la capture et l'extraction du texte blanc se font automatiquement
  4. Une fenêtre s'ouvre avec un aperçu du template extrait
  5. Tape le numéro correspondant à l'arme et appuie sur Entrée pour sauvegarder
"""

import os
import mss
import numpy as np
import cv2
import keyboard
from shared_enums import WeaponID

# Zones exactes des noms d'armes (2560x1440)
CAPTURE_SLOTS = {
    "slot 1 (gauche)": {"top": 430, "left": 890,  "width": 400, "height": 40},
    "slot 2 (droite)": {"top": 430, "left": 1620, "width": 400, "height": 40},
}

TEMPLATE_DIR = "pc1-vision/templates"
HOTKEY = "f8"

WEAPON_NAMES = [w for w in WeaponID if w != WeaponID.NONE]

os.makedirs(TEMPLATE_DIR, exist_ok=True)


def extract_white_text(frame_bgra: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Retourne (image_originale_gray, masque_binaire_texte_blanc).
    Isole le texte blanc pur en supprimant les tons colorés.
    """
    # Convertit en float pour éviter les overflows
    bgr = frame_bgra[:, :, :2].astype(np.float32)
    b = frame_bgra[:, :, 0].astype(np.float32)
    g = frame_bgra[:, :, 1].astype(np.float32)
    r = frame_bgra[:, :, 2].astype(np.float32)

    # Le blanc pur = R, G, B tous élevés ET proches les uns des autres
    brightness = (r + g + b) / 3.0
    # Écart max entre canaux (faible = neutre / blanc / gris)
    color_spread = np.max(np.stack([
        np.abs(r - g),
        np.abs(g - b),
        np.abs(r - b),
    ], axis=2), axis=2)

    # Masque : pixel brillant ET peu coloré (texte blanc)
    white_mask = ((brightness > 200) & (color_spread < 40)).astype(np.uint8) * 255

    # Nettoyage morphologique : supprime le bruit isolé
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)

    gray = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2GRAY)
    return gray, white_mask


def crop_to_text(mask: np.ndarray, padding: int = 6) -> tuple[int, int, int, int] | None:
    """
    Retourne le bounding box (x, y, w, h) englobant tous les pixels blancs.
    Retourne None si aucun texte détecté.
    """
    coords = cv2.findNonZero(mask)
    if coords is None:
        return None
    x, y, w, h = cv2.boundingRect(coords)
    # Ajoute un peu de padding
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(mask.shape[1] - x, w + padding * 2)
    h = min(mask.shape[0] - y, h + padding * 2)
    return x, y, w, h


def show_weapon_menu() -> WeaponID | None:
    print("\nQuelle arme viens-tu de capturer ?")
    for i, weapon in enumerate(WEAPON_NAMES, 1):
        print(f"  {i:2d}. {weapon.name}")
    print("   0. Annuler")

    while True:
        try:
            choice = int(input("\nNuméro : "))
            if choice == 0:
                return None
            if 1 <= choice <= len(WEAPON_NAMES):
                return WEAPON_NAMES[choice - 1]
        except ValueError:
            pass
        print("Entrée invalide, réessaie.")


def capture_and_process():
    print(f"\n[F8] Capture en cours...")

    for side_name, region in CAPTURE_SLOTS.items():
        with mss.MSS() as sct:
            screenshot = sct.grab(region)
        frame = np.array(screenshot)
        _, half_mask = extract_white_text(frame)

        if True:
            bbox = crop_to_text(half_mask)
        if bbox is None:
            print(f"  Aucun texte blanc détecté côté {side_name}, ignoré.")
            continue

        x, y, w, h = bbox
        cropped = half_mask[y:y+h, x:x+w]

        # Aperçu grossi x3 pour mieux voir
        preview = cv2.resize(cropped, (w * 3, h * 3), interpolation=cv2.INTER_NEAREST)
        cv2.imshow(f"Template extrait — {side_name} (ferme pour continuer)", preview)
        cv2.waitKey(1)

        weapon = show_weapon_menu()
        cv2.destroyAllWindows()

        if weapon is None:
            print("  Ignoré.")
            continue

        out_path = os.path.join(TEMPLATE_DIR, f"{weapon.name.lower()}.png")
        cv2.imwrite(out_path, cropped)
        print(f"  Sauvegardé : {out_path}  ({w}x{h}px)")


def main():
    print("=== Outil de capture de templates ===")
    print(f"Appuie sur {HOTKEY.upper()} dans Apex (inventaire ouvert) pour capturer.")
    print("Ctrl+C pour quitter.\n")

    keyboard.add_hotkey(HOTKEY, capture_and_process)

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\nFermeture.")


if __name__ == "__main__":
    main()
