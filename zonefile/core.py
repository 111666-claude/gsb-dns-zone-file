"""解析区域记录、叠加与按名查找。"""

SINGLETON = ("A", "AAAA", "CNAME", "SOA", "PTR")

DOMAIN_FIELDS = {
    "NS": (0,),
    "CNAME": (0,),
    "PTR": (0,),
    "MX": (1,),
    "SOA": (0, 1),
    "SRV": (3,),
}

CLASSES = ("IN", "CH", "HS")


class Counter:
    """记录比较次数。"""

    def __init__(self):
        self.scanned = 0


def _absolutize(name, origin):
    if name.endswith("."):
        return name
    if name == "@":
        return origin if origin else name
    if origin:
        return name + "." + origin
    return name


class Zone:
    def __init__(self):
        self.records = []
        self.by_name = {}
        self.singletons = {}
        self.seen = set()

    def _append(self, record):
        self.records.append(record)
        self.by_name.setdefault(record["name"], []).append(record)

    def _replace(self, old, new):
        self.records[self.records.index(old)] = new
        bucket = self.by_name[new["name"]]
        bucket[bucket.index(old)] = new

    def merge(self, staged):
        """叠加一个片段：单值类型后者覆盖前者，多值类型保留并去重。"""
        prior = dict(self.singletons)
        for record in staged:
            if record["type"] in SINGLETON:
                key = (record["name"], record["type"])
                old = prior.get(key)
                if old is not None:
                    self._replace(old, record)
                    self.singletons[key] = record
                    continue
                self.singletons[key] = record
                self._append(record)
            else:
                key4 = (record["name"], record["ttl"], record["type"], record["rdata"])
                if key4 in self.seen:
                    continue
                self.seen.add(key4)
                self._append(record)

    def lookup(self, name, counter):
        out = []
        for record in self.by_name.get(name, ()):
            counter.scanned += 1
            out.append(record)
        return out


def parse(fragments, counter):
    zone = Zone()
    origin = None
    default_ttl = 0
    last_owner = None
    for text in fragments:
        staged = []
        for raw in text.splitlines():
            line = raw.split(";", 1)[0]
            if not line.strip():
                continue
            counter.scanned += 1
            indented = line[:1].isspace()
            parts = line.split()
            head = parts[0].upper()
            if head == "$ORIGIN":
                new = parts[1]
                if new.endswith("."):
                    origin = new
                elif origin:
                    origin = new + "." + origin
                else:
                    origin = new + "."
                continue
            if head == "$TTL":
                default_ttl = int(parts[1])
                continue
            if indented and last_owner is not None:
                owner = last_owner
                rest = parts
            else:
                owner = _absolutize(parts[0], origin)
                rest = parts[1:]
            ttl = default_ttl
            if rest and rest[0].isdigit():
                ttl = int(rest[0])
                rest = rest[1:]
            if rest and rest[0].upper() in CLASSES:
                rest = rest[1:]
            if len(rest) < 2:
                continue
            rtype = rest[0].upper()
            rdata = rest[1:]
            for index in DOMAIN_FIELDS.get(rtype, ()):
                if index < len(rdata):
                    rdata[index] = _absolutize(rdata[index], origin)
            last_owner = owner
            staged.append({
                "name": owner,
                "ttl": ttl,
                "type": rtype,
                "rdata": " ".join(rdata),
            })
        zone.merge(staged)
    return zone
