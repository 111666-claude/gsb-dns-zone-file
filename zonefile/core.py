"""解析区域记录、叠加与按名查找。"""

SINGLETON = ("A", "AAAA", "CNAME", "SOA", "PTR")

CLASSES = ("IN", "CH", "HS")

RDATA_NAME_FIELDS = {
    "NS": (0,),
    "CNAME": (0,),
    "PTR": (0,),
    "MX": (1,),
    "SOA": (0, 1),
    "SRV": (3,),
}


class Counter:
    """记录比较次数。"""

    def __init__(self):
        self.scanned = 0


def absolutize(name, origin):
    """把相对名与 @ 补成绝对名。"""
    if name == "@":
        return origin or name
    if name.endswith("."):
        return name
    if origin:
        return name + "." + origin
    return name


class Zone:
    def __init__(self):
        self.records = []
        self.by_name = {}
        self._singletons = {}
        self._multi_seen = set()

    def merge(self, records):
        """叠加一个片段：单值类型跨片段后者覆盖前者，多值类型保留全部并去重。"""
        preexisting = set(self._singletons)
        for record in records:
            rtype = record["type"]
            if rtype in SINGLETON:
                key = (record["name"], rtype)
                if key in preexisting:
                    kept = self._singletons[key]
                    kept["ttl"] = record["ttl"]
                    kept["rdata"] = record["rdata"]
                    continue
                if key not in self._singletons:
                    self._singletons[key] = record
            else:
                key = (record["name"], record["ttl"], rtype, record["rdata"])
                if key in self._multi_seen:
                    continue
                self._multi_seen.add(key)
            self.records.append(record)
            self.by_name.setdefault(record["name"], []).append(record)

    def lookup(self, name, counter):
        counter.scanned += 1
        return list(self.by_name.get(name, ()))


def parse(fragments, counter):
    zone = Zone()
    origin = ""
    default_ttl = 0
    last_owner = None
    for text in fragments:
        records = []
        for raw in text.splitlines():
            line = raw.split(";", 1)[0]
            if not line.strip():
                continue
            counter.scanned += 1
            parts = line.split()
            head = parts[0].upper()
            if head == "$ORIGIN":
                if len(parts) > 1:
                    origin = absolutize(parts[1], origin)
                continue
            if head == "$TTL":
                if len(parts) > 1 and parts[1].isdigit():
                    default_ttl = int(parts[1])
                continue
            if line[0].isspace():
                if last_owner is None:
                    continue
                name = last_owner
                tokens = parts
            else:
                name = absolutize(parts[0], origin)
                last_owner = name
                tokens = parts[1:]
            ttl = None
            while tokens:
                token = tokens[0]
                if ttl is None and token.isdigit():
                    ttl = int(token)
                elif token.upper() in CLASSES:
                    pass
                else:
                    break
                tokens = tokens[1:]
            if not tokens:
                continue
            rtype = tokens[0].upper()
            fields = tokens[1:]
            for index in RDATA_NAME_FIELDS.get(rtype, ()):
                if index < len(fields):
                    fields[index] = absolutize(fields[index], origin)
            records.append({
                "name": name,
                "ttl": ttl if ttl is not None else default_ttl,
                "type": rtype,
                "rdata": " ".join(fields),
            })
        zone.merge(records)
    return zone
