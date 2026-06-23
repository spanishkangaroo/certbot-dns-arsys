## ADDED Requirements

### Requirement: Client initializes with API credentials
The `_ArsysClient` class SHALL accept `api_url`, `api_login`, `api_key`, and `domain` as constructor parameters and store them for use in subsequent API calls. Authentication SHALL be performed via HTTP Basic Auth, encoding `{api_login}:{api_key}` in Base64 and sending it as the `Authorization: Basic {credentials}` header on every request.

#### Scenario: Client initializes successfully
- **WHEN** `_ArsysClient` is constructed with valid `api_url`, `api_login`, `api_key`, and `domain`
- **THEN** the client stores all parameters and pre-computes the Base64-encoded auth header

#### Scenario: Client rejects empty credentials
- **WHEN** `api_login` or `api_key` is an empty string
- **THEN** the constructor SHALL raise `ValueError`

---

### Requirement: Client sends well-formed SOAP requests
The client SHALL construct SOAP 1.1 envelopes using string templates. Every request SHALL use `Content-Type: text/xml; charset=ISO-8859-1` and a `SOAPAction` header set to the operation name. Request bodies SHALL be encoded as ISO-8859-1 bytes before transmission.

#### Scenario: SOAP envelope is structurally valid
- **WHEN** the client calls any SOAP operation
- **THEN** the outgoing request body SHALL be parseable as valid XML with a `soap:Envelope` root and a `soap:Body` child containing the operation element

#### Scenario: Parameters are XML-escaped
- **WHEN** a TXT record value contains characters like `<`, `>`, `&`, or `"`
- **THEN** those characters SHALL be XML-escaped in the SOAP body before transmission

---

### Requirement: Client creates a DNS TXT record
`_ArsysClient.create_txt_record(name: str, value: str)` SHALL call the Arsys `CreateDNSEntry` SOAP operation with `dns=name`, `domain=self.domain`, `type="TXT"`, and `value=value`.

#### Scenario: Successful TXT record creation
- **WHEN** `create_txt_record("_acme-challenge.example.com", "abc123")` is called and the API returns `errorCode=0`
- **THEN** the method SHALL return without raising an exception

#### Scenario: API returns error code
- **WHEN** the API responds with `errorCode` != 0
- **THEN** the method SHALL raise `certbot.errors.PluginError` with a message including the `errorCode` and `errorMsg` values from the response

#### Scenario: Network timeout
- **WHEN** the SOAP endpoint does not respond within 30 seconds
- **THEN** the method SHALL raise `certbot.errors.PluginError` wrapping the underlying `urllib.error.URLError`

---

### Requirement: Client deletes a DNS TXT record
`_ArsysClient.delete_txt_record(name: str, value: str)` SHALL call the Arsys `DeleteDNSEntry` SOAP operation with `dns=name`, `domain=self.domain`, `type="TXT"`, and `value=value`.

#### Scenario: Successful TXT record deletion
- **WHEN** `delete_txt_record("_acme-challenge.example.com", "abc123")` is called and the API returns `errorCode=0`
- **THEN** the method SHALL return without raising an exception

#### Scenario: Record not found on delete
- **WHEN** the API responds with an error indicating the record does not exist
- **THEN** the method SHALL log a warning and return without raising an exception (idempotent cleanup)

#### Scenario: HTTP non-200 response on delete
- **WHEN** the SOAP endpoint returns HTTP 4xx or 5xx
- **THEN** the method SHALL raise `certbot.errors.PluginError` with the HTTP status code in the message

---

### Requirement: Client parses SOAP response for error codes
The client SHALL parse the SOAP XML response and extract the `errorCode` and `errorMsg` elements from the response body. A `errorCode` value of `0` SHALL be treated as success. Any other value SHALL be treated as failure.

#### Scenario: Response with errorCode 0 is success
- **WHEN** the SOAP response contains `<errorCode>0</errorCode>`
- **THEN** the client SHALL treat the operation as successful

#### Scenario: Response with non-zero errorCode raises PluginError
- **WHEN** the SOAP response contains `<errorCode>42</errorCode><errorMsg>Unauthorized</errorMsg>`
- **THEN** the client SHALL raise `certbot.errors.PluginError` containing both the code and the message

#### Scenario: Malformed XML response
- **WHEN** the API returns a response that is not valid XML
- **THEN** the client SHALL raise `certbot.errors.PluginError` with a parse error message
