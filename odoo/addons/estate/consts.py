class GardenOrientation:
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class EstateState:
    NEW = "new"
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    SOLD = "sold"
    CANCELED = "canceled"


class PropertyOfferStatus:
    NEW = "new"
    ACCEPTED = "accepted"
    REFUSED = "refused"


GARDEN_ORIENTATION_CHOICES = [
    (GardenOrientation.NORTH, "North"),
    (GardenOrientation.SOUTH, "South"),
    (GardenOrientation.EAST, "East"),
    (GardenOrientation.WEST, "West"),
]


ESTATE_STATE_CHOICES = [
    (EstateState.NEW, "New"),
    (EstateState.OFFER_RECEIVED, "Offer Received"),
    (EstateState.OFFER_ACCEPTED, "Offer Accepted"),
    (EstateState.SOLD, "Sold"),
    (EstateState.CANCELED, "Canceled"),
]

PROPERTY_OFFER_STATUS_CHOICES = [
    (PropertyOfferStatus.NEW, "New"),
    (PropertyOfferStatus.ACCEPTED, "Accepted"),
    (PropertyOfferStatus.REFUSED, "Refused"),
]
