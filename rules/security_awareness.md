# Security Guide OWASP Top 10

## What Is OWASP Top 10?

-The OWASP Top 10 lists the ten most critical web application security risks identified by the Open Web Application Security Project (OWASP).
-It serves as a baseline for developers and testers to identify and prevent major vulnerabilities.

---

## Vulnerability Categories & Warnings

12: ### 1. Broken Access Control [SEVERITY: CRITICAL]
13: **Risk:** Unrestricted access to sensitive data, resources, or functions.  
14: **Example:** Viewing user profiles without authentication.

**Warning Checklist:**
- [ ] Ensure all data access routes are protected with proper authentication/authorization.
- [ ] Validate all input parameters before access is granted.
- [ ] Use role-based access control (RBAC) logic explicitly.
- [ ] Avoid direct exposure of internal system files or endpoints.

22: ### 2. Injection (SQL, NoSQL, Command) [SEVERITY: CRITICAL]
23: **Risk:** Execution of unwanted code through input manipulation.  
24: **Example:** SQL injection via unfiltered user input.

**Warning Checklist:**
- [ ] Use parameterized queries or ORM tools; avoid string concatenation.
- [ ] Validate input data against a whitelist of allowed characters/values.
- [ ] Avoid use of OS or shell commands in untrusted input contexts.

31: ### 3. Insecure Cryptographic Practices [SEVERITY: CRITICAL]
32: **Risk:** Data exposure via weak or misused encryption.  
33: **Example:** Plaintext storage or weak key management.

**Warning Checklist:**
- [ ] Use established encryption standards (e.g., AES-256, TLS 1.3+).
- [ ] Do not hardcode keys or secrets; use environment variables or secure secret management.
- [ ] Never use deprecated algorithms (e.g., MD5, SHA-1).

### 4. Broken Authentication and Session Management
**Risk:** Unauthorized access due to flawed authentication mechanisms.  
**Example:** Session hijacking or weak token validation.

**Warning Checklist:**
- [ ] Enforce multi-factor authentication (MFA) where feasible.
- [ ] Implement secure session tokens and proper timeout policies.
- [ ] Avoid storing sensitive info in cookies; use HttpOnly flags.

### 5. Cross-Site Scripting (XSS)
**Risk:** Malicious scripts injected into web pages.  
**Example:** Storing attacker scripts in a user profile and rendering them.

**Warning Checklist:**
- [ ] Validate and encode all HTML content before rendering.
- [ ] Use Content Security Policy (CSP) headers.
- [ ] Avoid embedding external scripts from untrusted sources.

### 6. Insecure Design
**Risk:** Critical architectural flaws in application security logic.  
**Example:** Allowing public access to administrative interfaces.

**Warning Checklist:**
- [ ] Apply security by design from the initial phase.
- [ ] Avoid insecure defaults; ensure secure configuration by default.
- [ ] Do not design interfaces that expose internal APIs publicly.

### 7. Security Misconfiguration
**Risk:** Default configurations or exposed components.  
**Example:** HTTP debug modes left on.

**Warning Checklist:**
- [ ] Ensure all default ports are disabled or protected.
- [ ] Use secure configurations and avoid production debug settings.
- [ ] Keep all software components up to date and patched.

76: ### 8. Sensitive Data Exposure [SEVERITY: CRITICAL]
77: **Risk:** Leakage of credentials, PII, or API keys.  
78: **Example:** Log files containing passwords or API tokens.

**Warning Checklist:**
- [ ] Avoid logging sensitive data like passwords or tokens.
- [ ] Use secure data storage formats (e.g., hashing for passwords).
- [ ] Remove debug logs from production environments.

### 9. Cross-Site Request Forgery (CSRF)
**Risk:** Execution of actions by a victim's session.  
**Example:** Unauthorized payment or account changes.

**Warning Checklist:**
- [ ] Implement anti-CSRF tokens on state-changing requests.
- [ ] Use same-origin enforcement in browser policies.
- [ ] Avoid relying solely on HTTP methods for security.

### 10. Insufficient Logging and Monitoring
**Risk:** Inability to detect or investigate security events.  
**Example:** No monitoring on failed login attempts.

**Warning Checklist:**
- [ ] Enable audit logging for all privileged operations.
- [ ] Include correlation of logs for security incident investigation.
- [ ] Ensure all logs are stored securely and are not tamper-prone.

---

## Quick Reference Security Checklist (For Code Review Agents)

- [ ] **Input Validation**: All user inputs are sanitized.
- [ ] **Authentication & Authorization**: All protected routes use proper access controls.
- [ ] **Secure Communication**: Data is encrypted in transit (HTTPS) and at rest.
- [ ] **Secret Management**: No hardcoded secrets; use secure vaults.
- [ ] **Logging & Monitoring**: Security events are logged and monitored.
- [ ] **Component Updates**: Dependencies are checked for known vulnerabilities.
- [ ] **Security Headers**: Headers such as CSP, HSTS, X-Frame-Options are used.

---

## Final Security Best Practices

- **Never trust client input**, always validate it.
- **Use secure coding practices** for all components.
- **Keep dependencies updated** and review for vulnerabilities regularly.
- **Perform regular security audits** and penetration tests.
- **Enable security-focused CI pipelines** for automated scanning and reporting.

---