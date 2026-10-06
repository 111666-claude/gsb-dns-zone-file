"""解析区域记录、叠加与按名查找。"""

SINGLETON = ("A", "AAAA", "CNAME", "SOA", "PTR")


class Counter:
    """记录比较次数。"""

    def __init__(self):
        self.scanned = 0


class Zone:
    def __init__(self):
        self.records = []
        self.by_key = {}

    def add(self, record):
        key = (record["name"], record["type"])
        if key in self.by_key:
            return
        self.by_key[key] = record
        self.records.append(record)

    def lookup(self, name, counter):
        out = []
        for record in self.records:
            counter.scanned += 1
            if record["name"] == name:
                out.append(record)
        return out


def parse(fragments, counter):
    zone = Zone()
    for text in fragments:
        for raw in text.splitlines():
            line = raw.split(";", 1)[0].strip()
            if not line:
                continue
            counter.scanned += 1
            parts = line.split()
            head = parts[0].upper()
            if head == "$ORIGIN" or head == "$TTL":
                continue
            if len(parts) < 3:
                continue
            name = parts[0]
            rest = parts[1:]
            ttl = 0
            if rest[0].isdigit():
                ttl = int(rest[0])
                rest = rest[1:]
            if rest[0].upper() in ("IN", "CH", "HS"):
                rest = rest[1:]
            zone.add({
                "name": name,
                "ttl": ttl,
                "type": rest[0].upper(),
                "rdata": " ".join(rest[1:]),
            })
    return zone
