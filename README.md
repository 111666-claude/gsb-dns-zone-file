# dns-zone-file

解析 DNS 区域文件：`$ORIGIN` / `$TTL` 跨片段生效、相对名与 `@` 补全、省略 owner 继承、RDATA 里的域名按类型展开，并在多片段叠加时区分单值覆盖与多值保留。只用 Python 标准库。

```
python3 -m unittest discover -s tests
python3 -m zonefile --sample=origin
python3 -m zonefile --sample=owner
python3 -m zonefile --sample=rdata
python3 -m zonefile --sample=override
python3 -m zonefile --sample=multi
python3 -m zonefile --sample=work
```

## 口径

- **源与默认 TTL**：`$ORIGIN` / `$TTL` 设定后对后续记录生效，可以中途改变，也跨片段保留。
- **owner**：`@` 表示区域源；以点结尾是绝对名；否则补成"相对名 + 源"；整行以空白开头时继承上一条记录的 owner。
- **RDATA 域名**：`NS` / `CNAME` / `PTR` 的第一个字段、`MX` 的第二个、`SOA` 的前两个、`SRV` 的第四个按相对名补全。
- **叠加**：单值类型（`A` / `AAAA` / `CNAME` / `SOA` / `PTR`）同名同类型后者覆盖前者；多值类型（`NS` / `MX` / `TXT` / `SRV`）保留全部，四要素完全相同的去掉重复。
- **查找**：按名查找走索引，不逐条比较。

## 不变量

- 记录名都是绝对名，RDATA 里的域名也都是绝对名。
- 单值类型每个名字只有一条；多值类型没有四要素重复项。
- `scanned` 不随记录数乘查询次数放大：八百条记录查八百次的 `scanned` 不超过 6000。

## 输出契约

记录含 `name` / `ttl` / `type` / `rdata` 四个字段；场景打印一行 JSON。
`--sample=work` 打印 `{"records": N, "scanned": N}`。
