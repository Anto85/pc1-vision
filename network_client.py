import socket
from config import PC2_IP, UDP_PORT
from shared_enums import WeaponAction

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_init(weapon1_id: int, weapon2_id: int) -> None:
    payload = bytes([WeaponAction.INIT_WEAPONS, weapon1_id, weapon2_id])
    _sock.sendto(payload, (PC2_IP, UDP_PORT))


def send_slot_change(slot_action: WeaponAction) -> None:
    payload = bytes([slot_action])
    _sock.sendto(payload, (PC2_IP, UDP_PORT))
