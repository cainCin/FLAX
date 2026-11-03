from enum import IntEnum
from typing import Optional, Dict, Tuple


class ObjectClass(IntEnum):
    CHECKMARK_CIRCLE = 0
    CHECKMARK_TICK = 1
    CHECKMARK_LONE_CIRCLE = 2
    STAMP_PERSONAL = 3
    STAMP_RECEIPT = 4
    STAMP_ORGANIZATION = 5
    CHECKMARK_TICK_UNCHECKED = 6
    CHECKMARK_STRIKE_THROUGH = 7
    CHECKMARK_DASH_TICK = 8
    CHECKMARK_DASH_CIRCLE = 9

    @staticmethod
    def get_iter():
        return [
            ObjectClass.CHECKMARK_CIRCLE,
            ObjectClass.DESK,
            ObjectClass.CHECKMARK_TICK,
            ObjectClass.CHECKMARK_LONE_CIRCLE,
            ObjectClass.STAMP_PERSONAL,
            ObjectClass.STAMP_RECEIPT,
            ObjectClass.STAMP_ORGANIZATION,
            ObjectClass.CHECKMARK_TICK_UNCHECKED,
            ObjectClass.CHECKMARK_STRIKE_THROUGH,
            ObjectClass.CHECKMARK_DASH_TICK,
            ObjectClass.CHECKMARK_DASH_CIRCLE,
        ]

    @staticmethod
    def get_colors() -> Dict['ObjectClass', Tuple[int, int, int]]:
        return {
            ObjectClass.CHECKMARK_CIRCLE: (255, 0, 0),  # Red
            ObjectClass.CHECKMARK_TICK: (0, 255, 0),  # Green
            ObjectClass.CHECKMARK_LONE_CIRCLE: (0, 0, 255),  # Blue
            ObjectClass.STAMP_PERSONAL: (255, 255, 0),  # Yellow
            ObjectClass.STAMP_RECEIPT: (255, 0, 255),  # Magenta
            ObjectClass.STAMP_ORGANIZATION: (0, 255, 255),  # Cyan
            ObjectClass.CHECKMARK_TICK_UNCHECKED: (128, 0, 0),  # Maroon
            ObjectClass.CHECKMARK_STRIKE_THROUGH: (128, 128, 0),  # Olive
            ObjectClass.CHECKMARK_DASH_TICK: (0, 128, 128),  # Teal
            ObjectClass.CHECKMARK_DASH_CIRCLE: (128, 0, 128),  # Purple
        }


class AutoObjectClass:
    @staticmethod
    def guess_object_class(object_str: str) -> Optional[ObjectClass]:
        _str_to_cls: Dict[str, ObjectClass] = {
            "cm_type=cm_circle|status=checked": ObjectClass.CHECKMARK_CIRCLE,
            "cm_type=cm_tick|status=checked": ObjectClass.CHECKMARK_TICK,
            "checkmark_lone_circle": ObjectClass.CHECKMARK_LONE_CIRCLE,
            "stamp_personal": ObjectClass.STAMP_PERSONAL,
            "stamp_receipt": ObjectClass.STAMP_RECEIPT,
            "stamp_organization": ObjectClass.STAMP_ORGANIZATION,
            "cm_type=cm_tick|status=unchecked": ObjectClass.CHECKMARK_TICK_UNCHECKED,
            "cm_type=cm_strike_through|status=checked": ObjectClass.CHECKMARK_STRIKE_THROUGH,
            "cm_type=cm_dash_tick|status=unchecked": ObjectClass.CHECKMARK_DASH_TICK,
            "cm_type=cm_dash_circle|status=unchecked": ObjectClass.CHECKMARK_DASH_CIRCLE,
        }
        return _str_to_cls.get(object_str, None)

