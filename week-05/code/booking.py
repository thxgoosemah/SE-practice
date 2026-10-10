def can_book(start, end, now, blocked, existing):
    # AC1: valid range inside the day
    if not (0 <= start < end <= 1440):
        return False
    # AC1: the booking must start after the current time
    if start <= now:
        return False
    # AC2: at most 120 minutes
    if end - start > 120:
        return False
    # AC3: the room must not be blocked
    if blocked:
        return False
    # AC4: no overlap with an existing booking (touching endpoints are allowed)
    for existing_start, existing_end in existing:
        if start < existing_end and existing_start < end:
            return False
    # AC5: all of AC1-AC4 hold
    return True
