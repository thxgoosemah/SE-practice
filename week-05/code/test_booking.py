import copy
import unittest
from booking import can_book

BASE = [(600, 660)]  # 10:00-11:00; base input: now=540, blocked=False


class BookingTests(unittest.TestCase):
    # ---- the six table cases ----
    def test_touching_end_is_allowed(self):
        result = can_book(660, 720, 540, False, [(600, 660)])
        self.assertIs(result, True)  # AC4

    def test_partial_overlap_rejected(self):
        self.assertIs(can_book(630, 690, 540, False, BASE), False)  # AC4

    def test_blocked_room_rejected(self):
        self.assertIs(can_book(660, 720, 540, True, BASE), False)  # AC3

    def test_exactly_two_hours_allowed(self):
        self.assertIs(can_book(720, 840, 540, False, BASE), True)  # AC2

    def test_over_two_hours_rejected(self):
        self.assertIs(can_book(720, 841, 540, False, BASE), False)  # AC2

    def test_start_equal_now_rejected(self):
        self.assertIs(can_book(540, 570, 540, False, BASE), False)  # AC1

    # ---- start versus now ----
    def test_start_before_now_rejected(self):
        self.assertIs(can_book(500, 530, 540, False, BASE), False)  # AC1

    def test_start_one_minute_after_now_allowed(self):
        self.assertIs(can_book(541, 560, 540, False, BASE), True)  # AC1

    # ---- zero-length and reversed ----
    def test_zero_length_rejected(self):
        self.assertIs(can_book(700, 700, 540, False, BASE), False)  # AC1 start<end

    def test_reversed_times_rejected(self):
        self.assertIs(can_book(800, 700, 540, False, BASE), False)  # AC1 start<end

    # ---- day bounds ----
    def test_end_at_1440_allowed(self):
        self.assertIs(can_book(1380, 1440, 540, False, BASE), True)  # AC1 end<=1440

    def test_end_after_1440_rejected(self):
        # duration 61, no overlap: only end<=1440 can reject it
        self.assertIs(can_book(1380, 1441, 540, False, BASE), False)  # AC1

    # ---- existing: empty and several ----
    def test_empty_existing_allowed(self):
        self.assertIs(can_book(600, 660, 540, False, []), True)  # AC4

    def test_gap_between_several_bookings_allowed(self):
        existing = [(600, 660), (700, 760), (900, 960)]
        self.assertIs(can_book(780, 840, 540, False, existing), True)  # AC4

    def test_overlap_with_last_of_several_rejected(self):
        existing = [(600, 660), (700, 760), (900, 960)]
        self.assertIs(can_book(910, 950, 540, False, existing), False)  # AC4

    # ---- other overlap relationships ----
    def test_inside_existing_rejected(self):
        self.assertIs(can_book(615, 645, 540, False, BASE), False)  # AC4

    def test_contains_existing_rejected(self):
        self.assertIs(can_book(570, 690, 540, False, BASE), False)  # AC4

    def test_touching_start_is_allowed(self):
        self.assertIs(can_book(570, 600, 540, False, BASE), True)  # AC4

    def test_identical_interval_rejected(self):
        self.assertIs(can_book(600, 660, 540, False, BASE), False)  # AC4

    # ---- input unchanged ----
    def test_existing_unchanged_when_true(self):
        existing = [(900, 960), (600, 660), (700, 760)]  # deliberately unsorted
        snapshot = copy.deepcopy(existing)
        self.assertIs(can_book(780, 840, 540, False, existing), True)
        self.assertEqual(existing, snapshot)  # AC5

    def test_existing_unchanged_when_false(self):
        existing = [(900, 960), (600, 660), (700, 760)]
        snapshot = copy.deepcopy(existing)
        self.assertIs(can_book(630, 690, 540, False, existing), False)
        self.assertEqual(existing, snapshot)  # AC5


if __name__ == "__main__":
    unittest.main()
