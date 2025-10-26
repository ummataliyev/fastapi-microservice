"""
Enums for apartment table
"""

from enum import Enum


class Property(str, Enum):
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"


class Status(str, Enum):
    FREE = "free"
    RESERVED = "reserved"
    SOLD = "sold"
    DELETED = "deleted"


class Type(str, Enum):
    STUDIO = "studio"
    ONE_ROOM = "one_room"
    TWO_ROOM = "two_room"
    THREE_ROOM = "three_room"
    FOUR_ROOM = "four_room"
    DUPLEX = "duplex"


class Addition(str, Enum):
    YARD = "yard"
    BALCONY = "balcony"
    NO_BALCONY = "no_balcony"
