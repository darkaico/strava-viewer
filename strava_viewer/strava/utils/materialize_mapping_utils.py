DEFAULT_ICON = "local_play"

ICONS_BY_ACTIVITY = {
    "Ride": "directions_bike",
    "Run": "directions_run",
    "Swim": DEFAULT_ICON,
    "Walk": "directions_walk",
    "Hike": DEFAULT_ICON,
    "Alpine Ski": DEFAULT_ICON,
    "Backcountry Ski": DEFAULT_ICON,
    "Canoe": DEFAULT_ICON,
    "Crossfit": DEFAULT_ICON,
    "E-Bike Ride": DEFAULT_ICON,
    "Elliptical": DEFAULT_ICON,
    "Handcycle": DEFAULT_ICON,
    "Ice Skate": DEFAULT_ICON,
    "Inline Skate": DEFAULT_ICON,
    "Kayak": DEFAULT_ICON,
    "Kitesurf Session": DEFAULT_ICON,
    "Nordic Ski": DEFAULT_ICON,
    "Rock Climb": DEFAULT_ICON,
    "Roller Ski": DEFAULT_ICON,
    "Row": DEFAULT_ICON,
    "Snowboard": DEFAULT_ICON,
    "Snowshoe": DEFAULT_ICON,
    "Stair Stepper": DEFAULT_ICON,
    "Stand Up Paddle": DEFAULT_ICON,
    "Surf": DEFAULT_ICON,
    "Virtual Ride": DEFAULT_ICON,
    "Virtual Run": DEFAULT_ICON,
    "Weight Training": DEFAULT_ICON,
    "Windsurf Session": DEFAULT_ICON,
    "Wheelchair": DEFAULT_ICON,
    "Workout": DEFAULT_ICON,
    "Yoga": DEFAULT_ICON,
}


def get_icon_by_activity(activity_type):
    return ICONS_BY_ACTIVITY.get(activity_type, DEFAULT_ICON)
