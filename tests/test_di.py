import unittest
from datetime import datetime, timezone, timedelta
from tally.clock import RealClock, FakeClock
from tally.notifier import RealOutput, FakeOutput

class TestDependencyInjection(unittest.TestCase):
    def test_fake_clock_provides_controlled_time(self):
        fixed_time = datetime(2023, 10, 25, 14, 30, tzinfo=timezone.utc)
        clock = FakeClock(fixed_time)
        
        self.assertEqual(clock.now(), fixed_time)
        
        clock.advance(timedelta(hours=1))
        expected_time = datetime(2023, 10, 25, 15, 30, tzinfo=timezone.utc)
        self.assertEqual(clock.now(), expected_time)

    def test_real_clock_provides_current_time(self):
        clock = RealClock()
        now = clock.now()
        # Should be a timezone-aware datetime close to real current time
        self.assertIsNotNone(now.tzinfo)
        self.assertAlmostEqual(now.timestamp(), datetime.now(timezone.utc).timestamp(), delta=5)

    def test_fake_output_captures_messages(self):
        output = FakeOutput()
        output.write("Hello")
        output.write("World")
        
        self.assertEqual(output.messages, ["Hello", "World"])

if __name__ == '__main__':
    unittest.main()
