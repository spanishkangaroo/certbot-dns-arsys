## ADDED Requirements

### Requirement: Poller resolves authoritative nameservers for the zone
The propagation poller SHALL resolve the zone's `NS` records to obtain authoritative nameserver hostnames, then resolve each hostname to its `A` record. It SHALL filter out RFC-1918 private IP addresses. If at least one public IP is found, it SHALL configure `dnspython`'s resolver to use those IPs exclusively.

#### Scenario: Public NS IPs found
- **WHEN** the zone has NS records that resolve to public IP addresses
- **THEN** the poller SHALL use those IPs as the resolver's nameservers

#### Scenario: All NS IPs are private (Arsys internal infrastructure)
- **WHEN** all NS record IPs fall within RFC-1918 ranges (10.x, 172.16–31.x, 192.168.x)
- **THEN** the poller SHALL log an informational message and fall back to the system resolver

#### Scenario: NS resolution fails entirely
- **WHEN** `dnspython` raises any exception resolving NS records for the zone
- **THEN** the poller SHALL log a warning and fall back to the system resolver

---

### Requirement: Poller queries for TXT record presence every 15 seconds
After initializing the resolver, the poller SHALL query for the `_acme-challenge` TXT record every 15 seconds until either:
- The expected `value` is found in the TXT record data, OR
- The elapsed time exceeds `timeout` seconds

#### Scenario: TXT record appears before timeout
- **WHEN** the TXT record with the correct value becomes visible in DNS before `timeout` seconds
- **THEN** the poller SHALL return immediately without sleeping further

#### Scenario: Multiple TXT values present (concurrent challenges)
- **WHEN** the DNS response contains multiple TXT strings for the same name
- **THEN** the poller SHALL return successfully as long as the expected `value` is among them

#### Scenario: Timeout reached before TXT record appears
- **WHEN** `timeout` seconds elapse and the record has not been confirmed
- **THEN** the poller SHALL log a warning stating that propagation was not confirmed and return (do not raise; certbot will retry if validation fails)

---

### Requirement: Poller gracefully handles dnspython import failure
If `dnspython` is not installed, the poller SHALL fall back to a fixed sleep of `timeout` seconds and log a warning instructing the user to install `dnspython`.

#### Scenario: dnspython unavailable
- **WHEN** `import dns.resolver` raises `ImportError`
- **THEN** the poller SHALL sleep for `timeout` seconds and log a warning about the missing dependency

---

### Requirement: Poller logs progress at each poll interval
At each 15-second poll, the poller SHALL log the elapsed time and either the TXT values found or the exception type encountered (e.g., `NXDOMAIN`, `NoAnswer`, timeout).

#### Scenario: Logging during polling
- **WHEN** the poller issues a DNS query and receives a response
- **THEN** it SHALL log the elapsed time in seconds and the TXT values observed

#### Scenario: Logging on DNS exception
- **WHEN** a DNS query raises an exception
- **THEN** it SHALL log the elapsed time and the exception type and message
