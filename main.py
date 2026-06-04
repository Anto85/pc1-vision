import time
import keyboard
from config import TAB_HOLD_THRESHOLD, KEY_SLOT_1, KEY_SLOT_2, KEY_HOLSTER, KEY_INVENTORY
from network_client import send_slot_change, send_init
from vision import load_model, detect_weapons
from shared_enums import WeaponAction

_tab_pressed_time: float = 0


def on_key_event(e: keyboard.KeyboardEvent) -> None:
    global _tab_pressed_time

    if e.event_type == keyboard.KEY_DOWN:
        if e.name == KEY_SLOT_1:
            send_slot_change(WeaponAction.SET_SLOT_1)
        elif e.name == KEY_SLOT_2:
            send_slot_change(WeaponAction.SET_SLOT_2)
        elif e.name == KEY_HOLSTER:
            send_slot_change(WeaponAction.HOLSTER)

    if e.name == KEY_INVENTORY:
        if e.event_type == keyboard.KEY_DOWN and _tab_pressed_time == 0:
            _tab_pressed_time = time.perf_counter()

        elif e.event_type == keyboard.KEY_UP and _tab_pressed_time != 0:
            hold_duration = time.perf_counter() - _tab_pressed_time
            _tab_pressed_time = 0

            if hold_duration > TAB_HOLD_THRESHOLD:
                print("Lancement de l'analyse YOLO...")
                slot1_id, slot2_id = detect_weapons()
                send_init(slot1_id, slot2_id)
                print(f"Init envoyé : Slot1={slot1_id}, Slot2={slot2_id}")


def main() -> None:
    load_model()
    keyboard.hook(on_key_event)
    print("PC1 Vision actif. En attente d'événements clavier...")
    keyboard.wait()


if __name__ == "__main__":
    main()
