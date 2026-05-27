import math

DIRECTION_SPACING = 25
SWITCH_ABBREVIATIONS = ["sr", "sl"]
CURVE_ABBREVIATIONS = ["cr", "cl"]

def get_curve_edge_position(a_coords: list, a_heading: float, angle: float, radius: float, dir: str, from_a: bool, DIRECTION_SPACING: float = 25):

    # if either transition starts at a-end of right curve or at b-end (c-end in case of switch) of left curve
    signed_direction_spacing = -DIRECTION_SPACING/2 if from_a != (dir == "l") else DIRECTION_SPACING/2

    a_x, a_y = a_coords

    if dir == "r":
        return (
            a_x + radius * math.sin(math.radians(a_heading + 90)) + (radius + signed_direction_spacing) * math.sin(math.radians(a_heading + 270 + angle/2)),
            a_y + radius * math.cos(math.radians(a_heading + 90)) + (radius + signed_direction_spacing) * math.cos(math.radians(a_heading + 270 + angle/2))
        )
    else:
        return (
            a_x + radius * math.sin(math.radians(a_heading + 270)) + (radius + signed_direction_spacing) * math.sin(math.radians(a_heading + 90 - angle/2)),
            a_y + radius * math.cos(math.radians(a_heading + 270)) + (radius + signed_direction_spacing) * math.cos(math.radians(a_heading + 90 - angle/2))
        )
    
def get_straight_edge_position(a_coords: list, a_heading: float, length: float, from_a: bool, DIRECTION_SPACING: float = 25):
    signed_direction_spacing = DIRECTION_SPACING/2 if from_a else -DIRECTION_SPACING/2   
    return (
        a_coords[0] + length/2 * math.sin(math.radians(a_heading)) + signed_direction_spacing * math.cos(math.radians(a_heading)),
        a_coords[1] + length/2 * math.cos(math.radians(a_heading)) - signed_direction_spacing * math.sin(math.radians(a_heading))
    )

def get_edge_position(segment: object, from_end: str, to_end: str):
    segment_type = segment["type"]

    coords = segment["location"]["a"]
    heading = segment["metadata"]["coords"][2]
    starting_end = segment["metadata"]["starting_end"]

    if segment_type in CURVE_ABBREVIATIONS or segment_type in SWITCH_ABBREVIATIONS:
        dir = segment["metadata"]["dir"]
        radius = segment["metadata"]["radius"]
        angle = segment["metadata"]["angle"]

    # straight
    if segment_type == "st":
        if starting_end == "b": heading += 180
        return get_straight_edge_position(coords, heading, segment["metadata"]["length_a.b"], from_end == "a")
    
    # curve
    elif segment_type in CURVE_ABBREVIATIONS:
        if starting_end == "b":
            if segment["metadata"]["dir"] == "r": heading += 150
            else: heading += 210
        return get_curve_edge_position(coords, heading, angle, radius, dir, from_end == "a")
    
    # switch
    elif segment_type in SWITCH_ABBREVIATIONS:
        # transition is for straight segment of switch
        if starting_end == "b": heading += 180
        elif starting_end == "c":
            if segment["metadata"]["dir"] == "r": heading += 150
            else: heading += 210
        # transition for curve segment of switch
        if from_end in ["a", "b"] and to_end in ["a", "b"]:
            return get_straight_edge_position(coords, heading, segment["metadata"]["length_a.b"], from_end == "a")
        else:
            return get_curve_edge_position(coords, heading, angle, radius, dir, from_end == "a")

