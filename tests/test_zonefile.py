import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zonefile import core


class ZonefileTest(unittest.TestCase):
    def test_single_absolute_record(self):
        zone = core.parse(["www.example.com. 60 IN A 1.2.3.4\n"], core.Counter())
        self.assertEqual((zone.records[0]["type"], zone.records[0]["rdata"]), ("A", "1.2.3.4"))

    def test_explicit_ttl(self):
        zone = core.parse(["www.example.com. 60 A 1.2.3.4\n"], core.Counter())
        self.assertEqual(zone.records[0]["ttl"], 60)

    def test_absolute_name_kept(self):
        zone = core.parse(["www.example.com. A 1.2.3.4\n"], core.Counter())
        self.assertEqual(zone.records[0]["name"], "www.example.com.")

    def test_comment_skipped(self):
        zone = core.parse(["www.example.com. A 1.2.3.4 ; c\n"], core.Counter())
        self.assertEqual(len(zone.records), 1)

    def test_lookup_unknown(self):
        zone = core.parse(["www.example.com. A 1.2.3.4\n"], core.Counter())
        self.assertEqual(zone.lookup("zzz", core.Counter()), [])

    def test_counter_counts(self):
        counter = core.Counter()
        core.parse(["www.example.com. A 1.2.3.4\n"], counter)
        self.assertGreater(counter.scanned, 0)


if __name__ == "__main__":
    unittest.main()
