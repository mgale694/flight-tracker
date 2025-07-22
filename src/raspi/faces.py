import random

# Boot up faces and phrases
SLEEPING = "(-__-)"
WAKING = "(•__•)"
RISING = "(≤__≤)"
DREAMING = "(*__*)"
COFFEE = "(≠__≠)"
YAWNING = "(*__*)"
BOOTING = "(ø__ø)"
STRETCHING = "(#__#)"
GREETING = "(≥__≥)"
READY = "(O__O)"

# Flight tracking faces
SCANNING = "(⚆_⚆)"
DETECTING = "(☉_☉)"
TRACKING = "( ◕‿◕)"
FOCUSED = "(°▃▃°)"
ALERT = "(⌐■_■)"


def get_boot_phrases():
    """Get list of boot phrases with corresponding faces"""
    return [
        (SLEEPING, "Oi I was sleeping!"),
        (WAKING, "Wakey wakey!"),
        (RISING, "Rise and shine!"),
        (DREAMING, "Back from dreamland..."),
        (COFFEE, "Did you bring coffee?"),
        (YAWNING, "Yawn... what's up?"),
        (BOOTING, "Booting up with a smile!"),
        (STRETCHING, "Let me stretch first..."),
        (GREETING, "Good morning, world!"),
        (READY, "Ready for takeoff!"),
    ]


def get_random_boot_face():
    """Get a random boot face and phrase"""
    return random.choice(get_boot_phrases())


def get_tracking_face(state):
    """Get appropriate face for flight tracking state"""
    faces = {
        "scanning": SCANNING,
        "detecting": DETECTING,
        "tracking": TRACKING,
        "focused": FOCUSED,
        "alert": ALERT,
    }
    return faces.get(state, TRACKING)
