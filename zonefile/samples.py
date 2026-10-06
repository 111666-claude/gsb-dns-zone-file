"""固定场景，用来复现题面里的锚点。"""

import json

from . import core

BASE = "$ORIGIN example.com.\n"


def _line(obj):
    print(json.dumps(obj, ensure_ascii=False))


def run(name):
    if name == "origin":
        zone = core.parse([BASE + "www A 1.2.3.4\n"], core.Counter())
        _line({"name": zone.records[0]["name"]})
        return 0
    if name == "owner":
        text = BASE + "@ 60 IN A 1.2.3.4\n    IN A 5.6.7.8\n"
        zone = core.parse([text], core.Counter())
        _line({"first": zone.records[0]["name"], "second": zone.records[1]["name"]})
        return 0
    if name == "rdata":
        zone = core.parse([BASE + "www CNAME mail\n"], core.Counter())
        _line({"rdata": zone.records[0]["rdata"]})
        return 0
    if name == "override":
        zone = core.parse([BASE + "www A 1.1.1.1\n", BASE + "www A 2.2.2.2\n"], core.Counter())
        _line({"rdata": zone.records[0]["rdata"], "records": len(zone.records)})
        return 0
    if name == "multi":
        zone = core.parse([BASE + "@ NS ns1\n@ NS ns2\n"], core.Counter())
        _line({"records": len(zone.records)})
        return 0
    if name == "work":
        lines = ["h%04d A 1.2.3.4" % i for i in range(800)]
        zone = core.parse(["\n".join(lines) + "\n"], core.Counter())
        counter = core.Counter()
        for i in range(800):
            zone.lookup("h%04d" % i, counter)
        _line({"records": 800, "scanned": counter.scanned})
        return 0
    raise SystemExit("未知场景：" + name)
