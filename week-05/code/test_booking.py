import unittest
from booking import can_book

# Base input unless a test says otherwise: now=540, blocked=False, existing=[(600, 660)]


class BookingTests(unittest.TestCase):
    # --- the six cases from the handout ---
    def test_touching_end_is_allowed(self):  # AC4
        self.assertIs(can_book(660, 720, 540, False, [(600, 660)]), True)

    def test_overlap_is_rejected(self):  # AC4
        self.assertIs(can_book(630, 690, 540, False, [(600, 660)]), False)

    def test_blocked_room_is_rejected(self):  # AC3
        self.assertIs(can_book(660, 720, 540, True, [(600, 660)]), False)

    def test_exactly_two_hours_is_allowed(self):  # AC2
        self.assertIs(can_book(720, 840, 540, False, [(600, 660)]), True)

    def test_over_two_hours_is_rejected(self):  # AC2
        self.assertIs(can_book(720, 841, 540, False, [(600, 660)]), False)

    def test_start_equal_to_now_is_rejected(self):  # AC1 (start > now)
        self.assertIs(can_book(540, 570, 540, False, [(600, 660)]), False)

    # --- zero-length and reversed times ---
    def test_zero_length_is_rejected(self):  # AC1 (start < end)
        self.assertIs(can_book(700, 700, 540, False, [(600, 660)]), False)

    def test_reversed_times_are_rejected(self):  # AC1 (start < end)
        self.assertIs(can_book(720, 700, 540, False, [(600, 660)]), False)

    # --- the day bounds ---
    def test_negative_start_is_rejected(self):  # AC1 (0 <= start)
        self.assertIs(can_book(-10, 30, 0, False, []), False)

    def test_end_after_midnight_is_rejected(self):  # AC1 (end <= 1440); duration is only 41
        self.assertIs(can_book(1400, 1441, 540, False, []), False)

    def test_end_exactly_1440_is_allowed(self):  # AC1 (end <= 1440)
        self.assertIs(can_book(1380, 1440, 540, False, []), True)

    def test_start_one_minute_after_now_is_allowed(self):  # AC1 (start > now)
        self.assertIs(can_book(541, 571, 540, False, [(600, 660)]), True)

    # --- empty list and several bookings ---
    def test_empty_existing_is_allowed(self):  # AC4
        self.assertIs(can_book(700, 760, 540, False, []), True)

    def test_several_existing_fits_in_gap(self):  # AC4 (touches both neighbours)
        existing = [(600, 660), (720, 780), (900, 960)]
        self.assertIs(can_book(660, 720, 540, False, existing), True)

    def test_several_existing_overlaps_middle_one(self):  # AC4
        existing = [(600, 660), (720, 780), (900, 960)]
        self.assertIs(can_book(700, 760, 540, False, existing), False)

    def test_several_existing_overlaps_last_one(self):  # AC4 (the last item is checked too)
        existing = [(600, 660), (720, 780), (900, 960)]
        self.assertIs(can_book(950, 1010, 540, False, existing), False)

    # --- the other overlap relationships ---
    def test_touching_start_is_allowed(self):  # AC4
        self.assertIs(can_book(540, 600, 500, False, [(600, 660)]), True)

    def test_request_inside_existing_is_rejected(self):  # AC4
        self.assertIs(can_book(610, 640, 540, False, [(600, 660)]), False)

    def test_request_contains_existing_is_rejected(self):  # AC4
        self.assertIs(can_book(590, 700, 540, False, [(600, 660)]), False)

    def test_identical_interval_is_rejected(self):  # AC4
        self.assertIs(can_book(600, 660, 540, False, [(600, 660)]), False)

    def test_overlap_at_start_side_is_rejected(self):  # AC4
        self.assertIs(can_book(570, 630, 540, False, [(600, 660)]), False)

    # --- unchanged input ---
    def test_existing_is_not_modified_on_accept(self):  # AC5
        existing = [(720, 780), (600, 660)]
        snapshot = list(existing)
        can_book(660, 720, 540, False, existing)
        self.assertEqual(existing, snapshot)

    def test_existing_is_not_modified_on_reject(self):  # AC5
        existing = [(720, 780), (600, 660)]
        snapshot = list(existing)
        can_book(630, 690, 540, False, existing)
        self.assertEqual(existing, snapshot)


if __name__ == "__main__":
    unittest.main()
