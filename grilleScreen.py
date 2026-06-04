import mss
import cv2
import numpy as np

# Copie/Colle ici tes zones actuelles pour voir où elles tombent
CAPTURE_SLOTS = {
    "slot 1 (gauche)": {"top": 430, "left": 890,  "width": 400, "height": 40},
    "slot 2 (droite)": {"top": 430, "left": 1620, "width": 400, "height": 40},
}

def generate_grid_screenshot():
    print("📸 Capture de l'écran principal en cours...")
    
    with mss.mss() as sct:
        # Capture l'écran principal (monitors[1])
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        
        # Conversion pour OpenCV (BGRA)
        img = np.array(screenshot)

    height, width = img.shape[:2]
    step_small = 50
    step_large = 100

    print("📏 Dessin de la grille...")
    # Lignes verticales (X)
    for x in range(0, width, step_small):
        if x % step_large == 0:
            cv2.line(img, (x, 0), (x, height), (0, 255, 255, 255), 1) # Jaune pour les centaines
            cv2.putText(img, str(x), (x + 2, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255, 255), 1)
            cv2.putText(img, str(x), (x + 2, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255, 255), 1)
        else:
            cv2.line(img, (x, 0), (x, height), (255, 255, 255, 100), 1) # Blanc transparent pour les 50

    # Lignes horizontales (Y)
    for y in range(0, height, step_small):
        if y % step_large == 0:
            cv2.line(img, (0, y), (width, y), (0, 255, 255, 255), 1) # Jaune pour les centaines
            cv2.putText(img, str(y), (5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255, 255), 1)
            cv2.putText(img, str(y), (width - 40, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255, 255), 1)
        else:
            cv2.line(img, (0, y), (width, y), (255, 255, 255, 100), 1) # Blanc transparent pour les 50

    print("🟥 Dessin de tes zones actuelles...")
    # Dessiner les zones actuelles pour ajustement
    for name, rect in CAPTURE_SLOTS.items():
        top, left = rect["top"], rect["left"]
        w, h = rect["width"], rect["height"]
        
        # Boîte de l'arme en Rouge
        cv2.rectangle(img, (left, top), (left + w, top + h), (0, 0, 255, 255), 2)
        cv2.putText(img, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255, 255), 2)

    # Sauvegarde
    output_file = "grille_ecran.png"
    cv2.imwrite(output_file, img)
    print(f"✅ Terminé ! Ouvre le fichier '{output_file}' et zoome pour ajuster tes coordonnées.")

if __name__ == "__main__":
    generate_grid_screenshot()