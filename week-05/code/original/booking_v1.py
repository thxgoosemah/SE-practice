def can_book(start, end, now, blocked, existing):
    """Return True only when the request satisfies AC1-AC5."""
    # AC1: valid range within the day, and strictly after now
    if not (0 <= start < end <= 1440):
        return False
    if start <= now:
        return False
    # AC2: at most 120 minutes
    if end - start > 120:
        return False
    # AC3: room must not be blocked
    if blocked:
        return False
    # AC4: no overlap; touching endpoints allowed (end exclusive)
    for b_start, b_end in existing:
        if start < b_end and b_start < end:
            return False
    # AC5: all conditions hold; existing is never modified
    return True
