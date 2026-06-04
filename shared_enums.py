from enum import IntEnum


class WeaponAction(IntEnum):
    HOLSTER = 0x00
    SET_SLOT_1 = 0x01
    SET_SLOT_2 = 0x02
    INIT_WEAPONS = 0x03


class WeaponID(IntEnum):
    NONE = 0
    HAVOC = 1
    HEMLOCK = 2
    FLATLINE = 3
    R301 = 4
    NEMESIS = 5
    ALTERNATOR = 6
    PROWLER = 7
    R99 = 8
    VOLT = 9
    CAR = 10
    DEVOTION = 11
    LSTAR = 12
    SPITFIRE = 13
    RAMPAGE = 14
