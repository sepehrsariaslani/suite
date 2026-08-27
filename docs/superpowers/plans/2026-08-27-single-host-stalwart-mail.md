# Single-Host Stalwart Mail Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy Stalwart for `dehati.ir` on the existing ERP host, connect it to Suite Mail, and provision `info@dehati.ir` without interrupting ERPNext.

**Architecture:** A standalone Docker Compose project owns Stalwart and its persistent data. Docker publishes mail protocols directly while HTTP/JMAP is loopback-only; the existing Nginx terminates HTTPS for `mail.dehati.ir`. Certbot owns certificate renewal, and a deploy hook copies renewed material into Stalwart and reloads TLS.

**Tech Stack:** Docker Compose, Stalwart `v0.16.16`, stalwart-cli `v1.0.12`, Nginx, Certbot, Frappe/Suite Mail, HostIran DNS.

## Global Constraints

- Keep `dehati.ir` and ERP APIs available throughout deployment.
- Do not restart or modify the ERP Docker Compose project except to clear Suite caches if required.
- Store no password, private key, API key, or mailbox secret in Git.
- Bind Stalwart HTTP to `127.0.0.1:18080`; never expose recovery HTTP publicly.
- Expose only TCP 25, 465, 587, 993, and 4190 for mail protocols.
- Pin Stalwart to `v0.16.16` and stalwart-cli to `v1.0.12`.
- Set the initial mailbox quota to 2 GB and disable public signup.
- Do not change MX until local SMTP, JMAP, TLS, and Suite checks pass.
- Preserve persistent Stalwart data during rollback.

---

### Task 1: Baseline And Rollback State

**Files:**
- Create: `/var/backups/stalwart-preflight-20260827/`
- Read: `/etc/nginx/conf.d/frappe-bench.conf`

**Interfaces:**
- Consumes: Running Nginx and ERP services.
- Produces: Health evidence and restorable configuration copies.

- [ ] **Step 1: Verify the baseline**

Run:

```bash
curl -fsS https://dehati.ir/api/method/ping
docker compose -f /home/sepehr/den-v16-docker/docker-compose.yml \
  -f /home/sepehr/den-v16-docker/docker-compose.override.yml ps
sudo nginx -t
ss -ltn | grep -E ':(25|465|587|993|4190|18080) ' || true
```

Expected: ERP responds, containers are running, Nginx validates, and planned Stalwart ports are unused.

- [ ] **Step 2: Back up host configuration and DNS evidence**

Run:

```bash
sudo install -d -m 0700 /var/backups/stalwart-preflight-20260827
sudo cp -a /etc/nginx/conf.d /var/backups/stalwart-preflight-20260827/nginx-conf.d
sudo cp -a /etc/letsencrypt /var/backups/stalwart-preflight-20260827/letsencrypt
{ dig +short dehati.ir A; dig +short dehati.ir MX; dig +short mail.dehati.ir A; dig +short -x 62.60.207.82; } \
  | sudo tee /var/backups/stalwart-preflight-20260827/dns.txt >/dev/null
```

Expected: root-only backup contains the pre-deployment state.

---

### Task 2: Public Certificate

**Files:**
- Create: `/etc/nginx/conf.d/mail.dehati.ir.conf`
- Create: `/var/www/letsencrypt/.well-known/acme-challenge/`
- Create: `/etc/letsencrypt/live/mail.dehati.ir/` through Certbot.

**Interfaces:**
- Consumes: Public DNS for `mail.dehati.ir` and Nginx port 80.
- Produces: Trusted certificate for HTTPS and mail protocols.

- [ ] **Step 1: Add an HTTP-only ACME virtual host**

Create `/etc/nginx/conf.d/mail.dehati.ir.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name mail.dehati.ir;
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
        default_type text/plain;
    }
    location / { return 302 https://mail.dehati.ir$request_uri; }
}
```

- [ ] **Step 2: Validate Nginx and issue the certificate**

Run:

```bash
sudo install -d -m 0755 /var/www/letsencrypt/.well-known/acme-challenge
sudo nginx -t && sudo systemctl reload nginx
sudo certbot certonly --webroot --webroot-path /var/www/letsencrypt \
  --domain mail.dehati.ir --non-interactive --agree-tos --register-unsafely-without-email
sudo certbot certificates | grep -A5 'Certificate Name: mail.dehati.ir'
curl -fsS https://dehati.ir/api/method/ping
```

Expected: certificate files exist and ERP remains healthy.

---

### Task 3: Standalone Stalwart Bootstrap

**Files:**
- Create: `/etc/stalwart/mail.dehati.ir/docker-compose.yml`
- Create: `/etc/stalwart/mail.dehati.ir/stalwart.env`
- Create: `/etc/stalwart/mail.dehati.ir/bootstrap.ndjson`
- Create: `/etc/stalwart/mail.dehati.ir/secrets.env`
- Create: `/etc/stalwart/mail.dehati.ir/certs/`
- Create: `/etc/stalwart/mail.dehati.ir/stalwart-cli`

**Interfaces:**
- Consumes: Pinned Stalwart image, Suite-compatible bootstrap schema, certificate files.
- Produces: Persistent Stalwart reachable at `127.0.0.1:18080` and direct mail ports.

- [ ] **Step 1: Create directories and generated secrets**

Run as root:

```bash
install -d -o 2000 -g 2000 -m 0750 /etc/stalwart/mail.dehati.ir/{data,logs,certs}
umask 077
printf 'STALWART_ADMIN_USER=admin\nSTALWART_ADMIN_PASSWORD=%s\nMAILBOX_PASSWORD=%s\n' \
  "$(openssl rand -base64 36 | tr -d '\n')" "$(openssl rand -base64 24 | tr -d '\n')" \
  > /etc/stalwart/mail.dehati.ir/secrets.env
chown root:root /etc/stalwart/mail.dehati.ir/secrets.env
chmod 0600 /etc/stalwart/mail.dehati.ir/secrets.env
install -o 2000 -g 2000 -m 0640 /etc/letsencrypt/live/mail.dehati.ir/fullchain.pem \
  /etc/stalwart/mail.dehati.ir/certs/fullchain.pem
install -o 2000 -g 2000 -m 0640 /etc/letsencrypt/live/mail.dehati.ir/privkey.pem \
  /etc/stalwart/mail.dehati.ir/certs/privkey.pem
```

- [ ] **Step 2: Create the standalone Compose file**

```yaml
services:
  stalwart:
    image: stalwartlabs/stalwart:v0.16.16
    container_name: stalwart-mail-dehati
    restart: unless-stopped
    env_file: [./stalwart.env]
    ports:
      - "25:25"
      - "465:465"
      - "587:587"
      - "993:993"
      - "4190:4190"
      - "127.0.0.1:18080:8080"
    volumes:
      - /etc/stalwart/mail.dehati.ir:/etc/stalwart
```

- [ ] **Step 3: Create recovery environment without logging secrets**

Load `secrets.env` and write `stalwart.env` with owner `2000:2000`, mode `0640`, and these values:

```text
STALWART_HOSTNAME=mail.dehati.ir
STALWART_PUBLIC_URL=https://mail.dehati.ir/
STALWART_RECOVERY_MODE=0
STALWART_RECOVERY_MODE_PORT=8080
STALWART_RECOVERY_MODE_LOG_LEVEL=info
STALWART_RECOVERY_ADMIN=admin:<generated STALWART_ADMIN_PASSWORD>
```

- [ ] **Step 4: Create the Suite-compatible bootstrap operation**

Write this single line to `bootstrap.ndjson`, owner `2000:2000`, mode `0640`:

```json
{"@type":"update","object":"Bootstrap","id":"singleton","value":{"serverHostname":"mail.dehati.ir","defaultDomain":"dehati.ir","requestTlsCertificate":false,"generateDkimKeys":true,"dataStore":{"@type":"RocksDb","path":"/etc/stalwart/data","blobSize":16834,"bufferSize":134217728,"poolWorkers":1},"blobStore":{"@type":"Default"},"searchStore":{"@type":"Default"},"inMemoryStore":{"@type":"Default"},"directory":{"@type":"Internal"},"tracer":{"@type":"Log","ansi":false,"enable":true,"eventsPolicy":"exclude","level":"info","prefix":"stalwart","rotate":"daily","path":"/etc/stalwart/logs"},"dnsServer":{"@type":"Manual"}}}
```

- [ ] **Step 5: Install and verify stalwart-cli**

Download `stalwart-cli-x86_64-unknown-linux-gnu.tar.xz` from release `v1.0.12`, extract it to a temporary directory, install the binary as `/etc/stalwart/mail.dehati.ir/stalwart-cli` mode `0755`, and verify `stalwart-cli --help` exits zero.

- [ ] **Step 6: Start and bootstrap**

From `/etc/stalwart/mail.dehati.ir`, load `secrets.env` and run:

```bash
docker compose config -q
docker compose pull
docker compose up -d
timeout 180 bash -c 'until curl -sS http://127.0.0.1:18080/ >/dev/null; do sleep 2; done'
STALWART_URL=http://127.0.0.1:18080 STALWART_USER="$STALWART_ADMIN_USER" \
STALWART_PASSWORD="$STALWART_ADMIN_PASSWORD" \
  ./stalwart-cli apply --file ./bootstrap.ndjson --json
docker compose restart stalwart
timeout 180 bash -c 'until curl -sS http://127.0.0.1:18080/.well-known/jmap >/dev/null; do sleep 2; done'
```

Expected: bootstrap applies once and JMAP discovery responds after restart.

---

### Task 4: Trusted TLS And Renewal

**Files:**
- Create: `/etc/letsencrypt/renewal-hooks/deploy/stalwart-mail-dehati.sh`
- Modify: Stalwart `Certificate` and `SystemSettings` objects through stalwart-cli.

**Interfaces:**
- Consumes: Certbot certificate and generated admin credential.
- Produces: Trusted SMTP/IMAP TLS with automated renewal reload.

- [ ] **Step 1: Create a file-backed Certificate object**

Using admin credentials against `http://127.0.0.1:18080`, run:

```bash
stalwart-cli create Certificate \
  --field 'certificate={"@type":"File","filePath":"/etc/stalwart/certs/fullchain.pem"}' \
  --field 'privateKey={"@type":"File","filePath":"/etc/stalwart/certs/privkey.pem"}' --json
```

Capture the created id as `CERTIFICATE_ID`, then run:

```bash
stalwart-cli update SystemSettings singleton --field "defaultCertificateId=$CERTIFICATE_ID" --json
stalwart-cli create action/ReloadTlsCertificates --json
```

- [ ] **Step 2: Add the Certbot deploy hook**

Create a root-owned mode-`0750` hook that acts only for `/etc/letsencrypt/live/mail.dehati.ir`, copies both PEM files into the Stalwart cert directory as owner `2000:2000` mode `0640`, loads root-only admin credentials, and calls `action/ReloadTlsCertificates` against loopback.

- [ ] **Step 3: Verify protocol certificates**

Run `openssl s_client` against `127.0.0.1:465` and `127.0.0.1:993` with SNI `mail.dehati.ir`; pipe each certificate to `openssl x509 -noout -issuer -ext subjectAltName`.

Expected: both listeners present the public certificate for `mail.dehati.ir`.

---

### Task 5: Nginx HTTPS/JMAP

**Files:**
- Modify: `/etc/nginx/conf.d/mail.dehati.ir.conf`

**Interfaces:**
- Consumes: `127.0.0.1:18080` and the Certbot certificate.
- Produces: Public `https://mail.dehati.ir`.

- [ ] **Step 1: Add the TLS reverse proxy**

Keep the ACME server and add a 443 server using the `mail.dehati.ir` certificate. Proxy `/` to `http://127.0.0.1:18080`; set `Host`, `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Proto`; disable buffering; allow 50 MB bodies; set a 300-second read timeout.

- [ ] **Step 2: Validate before reload**

Run:

```bash
sudo nginx -t
curl -sS -H 'Host: mail.dehati.ir' http://127.0.0.1:18080/.well-known/jmap >/dev/null
sudo systemctl reload nginx
curl -fsS https://mail.dehati.ir/.well-known/jmap | python3 -m json.tool >/dev/null
curl -fsS https://dehati.ir/api/method/ping
```

Expected: JMAP and ERP both succeed.

---

### Task 6: Suite Configuration And Mailbox Provisioning

**Files:**
- Modify: `Mail Settings` singleton in `dehati.ir`.
- Create: Stalwart/Suite account state for `info@dehati.ir`.

**Interfaces:**
- Consumes: Public JMAP and generated secrets.
- Produces: Suite-managed 2 GB mailbox.

- [ ] **Step 1: Configure encrypted Mail Settings**

Use a Frappe console transaction to save these values, assigning the generated admin secret through the Password field so it is encrypted:

```text
server_url = https://mail.dehati.ir
username = admin
password = generated STALWART_ADMIN_PASSWORD
verify_ssl = 1
root_domain_name = dehati.ir
default_disk_quota_gb = 2
allow_signup = 0
stalwart_version = v0.16.16
stalwart_cli_version = v1.0.12
```

Commit, clear Frappe/Redis caches, and verify `is_stalwart_configured()` is true without printing the password.

- [ ] **Step 2: Verify the default domain**

Use Suite's domain service to assert enabled domain `dehati.ir` exists. If bootstrap did not create it, invoke `suite.mail.api.admin.add_domain("dehati.ir", "Dehati Mail")` as Administrator exactly once.

- [ ] **Step 3: Provision `info@dehati.ir`**

Resolve a valid enabled System Manager email privately as the backup address. Invoke `suite.mail.api.admin.add_member` as Administrator with username `info`, domain `dehati.ir`, admin enabled, invite disabled, generated mailbox password, quota `2`, locale `fa`, and timezone `Asia/Tehran`.

Expected: Frappe User, User Settings, JMAP account, app password, default mailboxes, and Suite Admin role exist.

- [ ] **Step 4: Run targeted integration tests**

Run Suite admin domain/member reads and:

```bash
bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_admin_members
```

Expected: the domain and mailbox are returned and integration tests pass.

---

### Task 7: DNS And External Delivery

**Files:**
- Create: `/root/dehati-mail-dns-records.json`
- Create: `/root/dehati-mail-credentials.txt`

**Interfaces:**
- Consumes: Stalwart-generated domain zone.
- Produces: Exact HostIran changes and one-time mailbox handoff.

- [ ] **Step 1: Export the generated DNS zone**

Resolve the domain id with Suite and save `get_domain_dns_json` output to `/root/dehati-mail-dns-records.json` mode `0600`.

- [ ] **Step 2: Apply the required HostIran records**

Replace the `mail` CNAME with `A mail.dehati.ir -> 62.60.207.82`. Replace MX with priority 10 targeting `mail.dehati.ir`. Add the exact Stalwart SPF, DKIM, DMARC, SRV, TLS reporting, and discovery records without creating a second SPF record.

- [ ] **Step 3: Verify DNS and PTR**

Run `dig` for mail A, domain MX/TXT, `_dmarc` TXT, DKIM selector TXT, and reverse IP. Forward and MX must match. If PTR is still HostIran's default, inbound mail may be tested but outbound delivery is not production-ready.

- [ ] **Step 4: Test real delivery**

Send one authenticated message from `info@dehati.ir` through port 465 to an external mailbox and inspect SPF/DKIM/DMARC headers. Reply externally and confirm the response appears in Suite Mail. Inspect queue/logs if either direction exceeds two minutes.

- [ ] **Step 5: Save one-time user credentials**

Write only the mailbox address and generated mailbox password to `/root/dehati-mail-credentials.txt` mode `0600`. Never include Stalwart recovery/admin credentials in the handoff.

---

### Task 8: Monitoring, Persistence, And Final Verification

**Files:**
- Create: `/etc/systemd/system/stalwart-disk-check.service`
- Create: `/etc/systemd/system/stalwart-disk-check.timer`

**Interfaces:**
- Consumes: Root filesystem usage and Stalwart health.
- Produces: Disk warning and verified restart/rollback behavior.

- [ ] **Step 1: Add an 85% disk warning**

Create a root oneshot service that logs through `logger -p mail.crit` when `/` usage is at least 85%, and a persistent timer that runs every 15 minutes.

- [ ] **Step 2: Verify restart persistence and ERP isolation**

Restart only the standalone Stalwart Compose service. Verify JMAP, `info@dehati.ir`, Nginx, ERP ping, and the disk timer. Do not use `docker compose down -v`.

- [ ] **Step 3: Verify rollback safety**

Confirm the saved Nginx configuration validates and that Stalwart can stop/start without deleting `/etc/stalwart/mail.dehati.ir/data`. Record that DNS MX rollback is independent from ERP.

- [ ] **Step 4: Final repository checks and commit**

Run `git diff --check` and `git status --short --branch` in Suite. Commit only documentation changes to `develop`; all secrets and host configuration stay outside Git.
