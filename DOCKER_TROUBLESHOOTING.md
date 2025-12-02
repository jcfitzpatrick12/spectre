# Docker Troubleshooting Guide: PNG Image Loading Issue

**Date:** November 22, 2025
**Issue:** Spectrogram PNG images failing to load in web UI with `ERR_CONNECTION_REFUSED`
**Audience:** Developers learning Docker, Flask, and nginx

---

## TL;DR - The Problem

When accessing the Spectre web UI at `http://localhost:8080`, the "Previous Recordings" gallery showed broken image icons instead of spectrogram PNGs. The browser console displayed:

```
Failed to load resource: net::ERR_CONNECTION_REFUSED
2025-11-21T19:44:23_my-config.png:1
```

Clicking on thumbnails did nothing. The images existed in the backend but weren't accessible through the frontend.

---

## The Investigation Journey

### Step 1: Check the API Response

First, we inspected what URLs the backend was returning:

```bash
$ curl http://localhost:5000/spectre-data/batches/?extension=png
```

**Response:**
```json
{
  "data": [
    "http://localhost:5000/spectre-data/batches/2025-11-21T19:44:23_my-config.png",
    "http://localhost:5000/spectre-data/batches/2025-11-22T18:46:12_my-config.png"
  ],
  "status": "success"
}
```

### Step 2: Understanding the Problem

The frontend runs on port **8080** (nginx), but the URLs point to port **5000** (Flask backend). When the browser tries to fetch these images:

1. User visits: `http://localhost:8080` ✅
2. Browser receives URL: `http://localhost:5000/spectre-data/batches/file.png`
3. Browser tries to fetch from port 5000... ❌ **Connection refused!**

Why? The browser makes a **new HTTP request** to port 5000, which in production is not exposed externally. Only the nginx container on port 8080 is accessible.

---

## Root Cause #1: Absolute URLs with Wrong Host/Port

### The Docker Networking Problem

In our Docker setup:

```yaml
services:
  spectre-server:
    ports:
      - 127.0.0.1:5000:5000  # Only accessible on host machine

  spectre-frontend:
    ports:
      - 127.0.0.1:8080:3000  # Main entry point
```

**Key concept:** When Docker containers talk to each other, they use **internal service names** like `spectre-server:5000`. But when your **browser** tries to access resources, it uses **external URLs** like `localhost:8080`.

The Flask backend was generating absolute URLs:
```
http://localhost:5000/spectre-data/batches/file.png
```

But even worse, in some cases it was generating:
```
http://spectre-server:5000/spectre-data/batches/file.png
```

The hostname `spectre-server` **only exists inside the Docker network**. Your browser has no idea what `spectre-server` means!

### Why This Happened: Flask's `url_for(_external=True)`

In `backend/src/spectre_server/routes/batches.py`:

**BEFORE (broken):**
```python
def get_batch_file_endpoint(batch_file_path: str) -> str:
    return flask.url_for(
        "batches.get_batch_file",
        file_name=os.path.basename(batch_file_path),
        _external=True,  # ⚠️ This creates absolute URLs
    )
```

When `_external=True`, Flask builds a full URL including the protocol and hostname. It determines the hostname from the `Host` header in the incoming request.

**The problem:** Depending on how the request arrived (direct to backend, through nginx proxy, etc.), Flask might see:
- `Host: localhost:5000`
- `Host: spectre-server:5000`
- `Host: localhost:8080`

So it generates inconsistent, incorrect absolute URLs.

---

## Fix #1: Return Relative URLs Instead

**AFTER (fixed):**
```python
def get_batch_file_endpoint(batch_file_path: str) -> str:
    return flask.url_for(
        "batches.get_batch_file",
        file_name=os.path.basename(batch_file_path),
        # Removed _external=True
    )
```

**Result:**
```json
{
  "data": [
    "/spectre-data/batches/2025-11-21T19:44:23_my-config.png",
    "/spectre-data/batches/2025-11-22T18:46:12_my-config.png"
  ]
}
```

### Why This Works

**Relative URLs are resolved relative to the current page's origin:**

1. User visits: `http://localhost:8080/`
2. Frontend fetches: `/spectre-data/batches/?extension=png`
3. Gets relative URL: `/spectre-data/batches/file.png`
4. Browser resolves to: `http://localhost:8080/spectre-data/batches/file.png` ✅
5. Nginx proxies to backend ✅

The browser automatically uses the **same host and port** it's already connected to. No hardcoded ports, no internal Docker hostnames. Just works™.

### Files Changed

We applied the same fix to three route files:

- `backend/src/spectre_server/routes/batches.py` (line 26)
- `backend/src/spectre_server/routes/logs.py` (line 24)
- `backend/src/spectre_server/routes/configs.py` (line 27)

---

## Root Cause #2: Nginx Configuration Priority

After fixing the backend, images **still** didn't load! New error in nginx logs:

```
[error] open() "/usr/share/nginx/html/spectre-data/batches/file.png"
failed (2: No such file or directory)
```

Nginx was trying to serve the PNG from its **local filesystem** instead of **proxying** to the backend!

### Understanding Nginx Location Matching

Nginx evaluates location blocks in this order:

1. **Exact match** `location = /path` - Highest priority
2. **Priority prefix** `location ^~ /path` - Stops regex matching
3. **Regex match** `location ~ pattern` - Case-sensitive regex
4. **Regex match** `location ~* pattern` - Case-insensitive regex
5. **Prefix match** `location /path` - Lowest priority

Our nginx.conf had:

**BEFORE (broken):**
```nginx
location /spectre-data {  # Regular prefix match (LOW priority)
    proxy_pass http://spectre-server:5000;
}

location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {  # Regex (HIGHER priority!)
    expires 1y;
    add_header Cache-Control "public, immutable";
    # This implicitly tries to serve from root (local filesystem)
}
```

**What happened:**
1. Request for `/spectre-data/batches/file.png` arrives
2. Nginx checks exact matches - none found
3. Nginx checks priority prefixes - none found
4. Nginx checks **regex matches** - `~* \.png$` **matches!** ✅
5. Nginx tries to serve from `/usr/share/nginx/html/spectre-data/...`
6. File doesn't exist locally → **404 Not Found**

The `/spectre-data` proxy block was **never even evaluated** because the regex matched first!

---

## Fix #2: Use Priority Prefix Matching

**AFTER (fixed):**
```nginx
location ^~ /spectre-data {  # Added ^~ for PRIORITY
    proxy_pass http://spectre-server:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Why `^~` Works

The `^~` modifier means:
> "This is a **priority prefix match**. If this matches, **stop** searching for regex matches."

**New flow:**
1. Request for `/spectre-data/batches/file.png` arrives
2. Nginx checks exact matches - none
3. Nginx checks priority prefixes - `^~ /spectre-data` **matches!** ✅
4. **Nginx stops here**, doesn't check regex patterns
5. Proxies request to `http://spectre-server:5000` ✅
6. Backend serves the file ✅

### Visual Comparison

```
Before: Browser → Nginx → Regex match → Try local filesystem → 404

After:  Browser → Nginx → Priority prefix → Proxy to backend → 200 OK!
```

---

## Root Cause #3: Docker Entrypoint Shell Mismatch

While debugging, we had to rebuild the backend image. The container kept **exiting immediately** with no error logs:

```bash
$ docker ps -a
NAMES            STATUS
spectre-server   Exited (0) 5 seconds ago  # Exit code 0 = "success" but... why?
```

### The Multi-Stage Dockerfile Confusion

The backend `Dockerfile` has multiple build stages:

```dockerfile
FROM base AS spectre_server
# ... builds Python dependencies

FROM base AS runtime
# ... production runtime with entrypoint
ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["/app/cmd.sh"]

FROM runtime AS root_runtime
# ... variant for root user

FROM base AS development
# ... development tools
CMD ["/bin/bash"]  # Just bash, no server!
```

**Problem:** When we built without specifying `--target`, Docker built **all stages** and tagged the **last one** (`development`) with our image name.

```bash
$ docker build -t jcfitzpatrick12/spectre-server:2.0.0-alpha .
# Built "development" stage → just runs bash → exits immediately
```

### The entrypoint.sh Script Issue

Even after targeting the right stage, the container exited. The `entrypoint.sh` script has a **bash shebang**:

```bash
#!/bin/bash
# ... script uses bash features
```

But the Dockerfile specified:
```dockerfile
ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
```

**`/bin/sh` is not always bash!** In Alpine Linux (our base), `/bin/sh` is a minimal shell that doesn't support all bash features. This caused silent failures.

---

## Fix #3: Explicit Entrypoint in docker-compose.yml

Instead of fixing the Dockerfile (which would require pushing new images), we **overrode** the entrypoint in `docker-compose.yml`:

**AFTER (fixed):**
```yaml
services:
  spectre-server:
    image: jcfitzpatrick12/spectre-server:2.0.0-alpha
    entrypoint: ["/bin/bash", "/app/entrypoint.sh"]  # ✅ Use bash explicitly
    command: ["/app/cmd.sh"]                         # ✅ Explicit command
    # ... rest of config
```

### Why This Works

1. **`entrypoint: ["/bin/bash", "/app/entrypoint.sh"]`**
   - Runs bash (not sh)
   - Passes `/app/entrypoint.sh` as an argument to bash
   - Bash executes the script properly

2. **`command: ["/app/cmd.sh"]`**
   - Gets passed as `$@` to the entrypoint script
   - The entrypoint does setup (create groups, change ownership)
   - Then runs: `exec gosu appuser /app/cmd.sh`

3. **`cmd.sh` starts the actual server:**
   ```bash
   sdrplay_apiService &
   python3 -m gunicorn -c gunicorn.conf.py "spectre_server.__main__:make_app()"
   ```

---

## How It All Works Now: End-to-End Flow

Let's trace a request for a PNG image from start to finish:

```
1. USER'S BROWSER
   ↓
   Opens: http://localhost:8080/

2. NGINX CONTAINER (port 8080)
   ↓
   Serves: /usr/share/nginx/html/index.html (React app)

3. REACT APP (in browser)
   ↓
   Fetches: GET http://localhost:8080/spectre-data/batches/?extension=png

4. NGINX (receives request)
   ↓
   Matches: location ^~ /spectre-data
   ↓
   Proxies to: http://spectre-server:5000/spectre-data/batches/?extension=png

5. FLASK BACKEND (spectre-server container)
   ↓
   Routes to: batches.get_batch_files()
   ↓
   Returns JSON: {
     "data": ["/spectre-data/batches/2025-11-21T19:44:23_my-config.png"],
     "status": "success"
   }

6. NGINX → BROWSER
   ↓
   Passes JSON response back

7. REACT APP (parses response)
   ↓
   Creates <img> tags with: src="/spectre-data/batches/2025-11-21T19:44:23_my-config.png"

8. BROWSER (loads images)
   ↓
   Requests: GET http://localhost:8080/spectre-data/batches/2025-11-21T19:44:23_my-config.png

9. NGINX (receives image request)
   ↓
   Matches: location ^~ /spectre-data (priority prefix!)
   ↓
   Does NOT match: location ~* \.png$ (stopped by ^~)
   ↓
   Proxies to: http://spectre-server:5000/spectre-data/batches/2025-11-21T19:44:23_my-config.png

10. FLASK BACKEND
    ↓
    Routes to: batches.get_batch_file("2025-11-21T19:44:23_my-config.png")
    ↓
    Uses: flask.send_from_directory()
    ↓
    Serves: PNG file from /app/.spectre-data/batches/.../file.png

11. NGINX → BROWSER
    ↓
    Streams PNG data
    ↓
    Sets: Content-Type: image/png

12. BROWSER
    ↓
    Renders image! 🎉
```

**Key points:**
- Relative URLs (`/spectre-data/...`) automatically use the browser's current origin
- Nginx proxies **both API calls and file requests** to the backend
- Priority prefix `^~` ensures proxying happens before static file matching
- Everything stays on port 8080 from the browser's perspective

---

## Key Learnings for Developers

### 1. Docker Networking: Internal vs External

**Internal (container-to-container):**
```yaml
services:
  frontend:
    # Can access: http://backend:5000
  backend:
    # Service name becomes hostname
```

**External (browser to container):**
```yaml
services:
  frontend:
    ports:
      - 8080:3000  # Browser uses: http://localhost:8080
```

**Rule of thumb:** Never hardcode URLs in your API responses. Use relative URLs so they work regardless of how the client accesses your service.

### 2. Flask URL Generation Best Practices

```python
# ❌ BAD: Absolute URLs break in proxied environments
flask.url_for('endpoint', _external=True)
# Returns: http://internal-hostname:5000/path

# ✅ GOOD: Relative URLs work everywhere
flask.url_for('endpoint')
# Returns: /path
```

**Exception:** Email links, webhooks, or redirects that need to work outside the current request context genuinely need absolute URLs. In those cases, use a configurable `BASE_URL` environment variable, not `_external=True`.

### 3. Nginx Location Directive Priority

**Remember the order:**
1. Exact: `location = /exact`
2. Priority prefix: `location ^~ /prefix`
3. Regex: `location ~ regex` or `location ~* regex`
4. Prefix: `location /prefix`

**Common mistake:** Putting broad regex patterns (like `~* \.png$`) without realizing they'll intercept more specific paths.

**Fix:** Use `^~` for API/proxy paths to prevent regex interception.

### 4. Multi-Stage Dockerfiles

```dockerfile
FROM base AS build
# Build-time dependencies

FROM base AS runtime
# Minimal runtime

FROM base AS development
# Dev tools
```

**When building:**
```bash
# ❌ Builds ALL stages, tags the LAST one
docker build -t myapp .

# ✅ Builds specific stage
docker build --target runtime -t myapp .
```

**Pro tip:** Always specify `--target` in CI/CD to avoid surprises.

### 5. Shell Compatibility

```dockerfile
# ❌ Assumes /bin/sh is bash
ENTRYPOINT ["/bin/sh", "script.sh"]

# ✅ Explicit bash
ENTRYPOINT ["/bin/bash", "/app/script.sh"]

# ✅✅ Best: Make script executable with shebang
ENTRYPOINT ["/app/script.sh"]
# script.sh:
#!/bin/bash
```

**Alpine Linux gotcha:** `/bin/sh` → BusyBox `ash`, not `bash`. If your script uses bash features (`[[`, arrays, etc.), explicitly use `/bin/bash`.

---

## Debugging Checklist for Similar Issues

If images/assets fail to load in a Dockerized web app:

- [ ] **Check browser console** - What's the exact error? Network tab?
- [ ] **Inspect API responses** - Are URLs absolute or relative?
- [ ] **Test backend directly** - Does `curl http://localhost:5000/path` work?
- [ ] **Test through proxy** - Does `curl http://localhost:8080/path` work?
- [ ] **Check nginx logs** - Is it trying local filesystem or proxying?
- [ ] **Verify nginx config** - Do location blocks have correct priority?
- [ ] **Check Docker networking** - Can containers reach each other?
- [ ] **Verify container is running** - `docker ps` shows it healthy?
- [ ] **Check container logs** - `docker logs container-name`

---

## Summary of Changes

| File | Change | Why |
|------|--------|-----|
| `backend/src/spectre_server/routes/batches.py` | Removed `_external=True` from line 26 | Return relative URLs instead of absolute |
| `backend/src/spectre_server/routes/logs.py` | Removed `_external=True` from line 24 | Consistency with batches.py |
| `backend/src/spectre_server/routes/configs.py` | Removed `_external=True` from line 27 | Consistency with batches.py |
| `frontend/nginx.conf` | Changed `location /spectre-data` to `location ^~ /spectre-data` | Priority prefix prevents regex interception |
| `docker-compose.yml` | Added explicit `entrypoint` and `command` for spectre-server | Ensure bash is used, not sh |

---

## Testing the Fix

```bash
# 1. Rebuild backend with changes
cd backend
docker build --target runtime -t jcfitzpatrick12/spectre-server:2.0.0-alpha .

# 2. Rebuild frontend
cd ../frontend
docker build --target production -t spectre-frontend:latest .

# 3. Restart stack
cd ..
docker compose -f docker-compose.yml restart

# 4. Verify API returns relative URLs
curl http://localhost:5000/spectre-data/batches/?extension=png
# Should see: "/spectre-data/batches/file.png"

# 5. Verify images load through nginx
curl -I http://localhost:8080/spectre-data/batches/2025-11-21T19:44:23_my-config.png
# Should see: HTTP/1.1 200 OK
#             Content-Type: image/png

# 6. Test in browser
# Open: http://localhost:8080
# Images should load in "Previous Recordings" section
```

---

## Additional Resources

- [Docker Networking Overview](https://docs.docker.com/network/)
- [Flask url_for Documentation](https://flask.palletsprojects.com/en/2.3.x/api/#flask.url_for)
- [Nginx Location Directive](https://nginx.org/en/docs/http/ngx_http_core_module.html#location)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

---

**Questions?** This guide is meant to help you understand not just *what* we changed, but *why* each change was necessary. If something's unclear, dig into the linked resources or experiment with the code!
