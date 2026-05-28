"""Deploy app-11 to VM and run smoke tests."""
import paramiko
import time
import json

HOST = "192.168.96.110"
USER = "yolo1"
PASS = "yolo1"
APP_DIR = "/home/yolo1/app-11-social-analytics"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, look_for_keys=False)

def run(cmd, timeout=30):
    print(f"$ {cmd}")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out[:2000])
    if err:
        print(f"[STDERR] {err[:500]}")
    if exit_code != 0:
        raise RuntimeError(f"Command failed (exit {exit_code}): {cmd}")
    return out

try:
    # Clean any previous deployment
    run("docker compose down -v 2>/dev/null; docker system prune -a -f --volumes 2>/dev/null; rm -rf ~/app-11-social-analytics")

    # Create app directory and copy files
    run(f"mkdir -p {APP_DIR}")
    
    # Use tar/ssh to copy files
    import os
    import tarfile
    import io
    
    base = r"D:\work\secure-code-hunt\apps\typescript\app-11-social-analytics"
    exclude = {"node_modules", "dist", ".git", "deploy_test.py"}
    
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for root, dirs, files in os.walk(base):
            rel = os.path.relpath(root, base)
            if rel == ".":
                rel = ""
            # Skip excluded
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in files:
                if f in exclude or f.endswith(".pyc"):
                    continue
                fpath = os.path.join(root, f)
                arcname = os.path.join(rel, f) if rel else f
                tar.add(fpath, arcname=arcname)
    
    buf.seek(0)
    sftp = client.open_sftp()
    remote_path = f"{APP_DIR}/app.tar.gz"
    with sftp.open(remote_path, "wb") as f:
        f.write(buf.read())
    sftp.close()
    
    run(f"cd {APP_DIR} && tar xzf app.tar.gz && rm app.tar.gz")
    
    # Start docker compose (Dockerfile handles npm install + build inside container)
    run(f"cd {APP_DIR} && docker compose up --build -d", timeout=120)
    
    # Wait for web healthcheck
    print("Waiting for services to become healthy...")
    for i in range(60):
        time.sleep(5)
        try:
            _, stdout, _ = client.exec_command(
                f"curl -fsS http://localhost:8011/api/health", timeout=5
            )
            out = stdout.read().decode().strip()
            data = json.loads(out)
            print(f"  health check: {data}")
            if data.get("postgres") == "connected" and data.get("redis") == "connected":
                print("All services healthy!")
                break
        except Exception as e:
            print(f"  attempt {i+1}: {e}")
    else:
        raise RuntimeError("Services did not become healthy within timeout")
    
    # Run smoke tests
    print("\n--- Running smoke tests ---")
    
    # Health check
    _, stdout, _ = client.exec_command("curl -fsS http://localhost:8011/api/health", timeout=5)
    health = json.loads(stdout.read().decode())
    assert health["status"] == "ok", f"Health check failed: {health}"
    assert health["postgres"] == "connected", f"PG not connected: {health}"
    assert health["redis"] == "connected", f"Redis not connected: {health}"
    print(f"  GET /api/health -> {health}")
    
    # Debug config (existing A05)
    _, stdout, _ = client.exec_command("curl -fsS http://localhost:8011/api/debug/config", timeout=5)
    config = json.loads(stdout.read().decode())
    assert "internalSearchUrl" in config, f"Debug config missing fields: {config}"
    print(f"  GET /api/debug/config -> A05 leak confirmed (has internalSearchUrl)")
    
    # Login
    _, stdout, _ = client.exec_command(
        "curl -fsS -X POST http://localhost:8011/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"alice\",\"password\":\"alice123\"}' -c /tmp/cookies.txt",
        timeout=5
    )
    login = json.loads(stdout.read().decode())
    assert "user" in login, f"Login failed: {login}"
    print(f"  POST /api/auth/login -> {login['user']['username']} logged in")
    
    # Widgets
    _, stdout, _ = client.exec_command(
        "curl -fsS http://localhost:8011/api/widgets -b /tmp/cookies.txt", timeout=5
    )
    widgets = json.loads(stdout.read().decode())
    assert len(widgets) > 0, f"No widgets returned: {widgets}"
    print(f"  GET /api/widgets -> {len(widgets)} widgets")
    
    # Create widget
    _, stdout, _ = client.exec_command(
        "curl -fsS -X POST http://localhost:8011/api/widgets -H 'Content-Type: application/json' -b /tmp/cookies.txt -d '{\"title\":\"Test Widget\",\"type\":\"metric\",\"value\":\"99%\"}'",
        timeout=5
    )
    created = json.loads(stdout.read().decode())
    assert created.get("title") == "Test Widget", f"Create widget failed: {created}"
    print(f"  POST /api/widgets -> created widget id={created.get('id')}")
    
    # SSRF (existing A10) — hit Elasticsearch which speaks HTTP on port 9200
    stdin, stdout, stderr = client.exec_command(
        "curl -Ss -X POST http://localhost:8011/api/preview -H 'Content-Type: application/json' -d '{\"url\":\"http://elasticsearch:9200\"}' --write-out ' %{http_code}'",
        timeout=10
    )
    raw = stdout.read().decode().strip()
    parts = raw.rsplit(' ', 1)
    body = parts[0].strip() if len(parts) > 1 else raw
    code = parts[1].strip() if len(parts) > 1 else '?'
    if body:
        ssrf_data = json.loads(body)
        assert ssrf_data.get("success"), f"SSRF failed: {ssrf_data}"
        print(f"  POST /api/preview -> SSRF confirmed (reached elasticsearch, code {code})")
    else:
        print(f"  POST /api/preview -> empty body (code {code})")
    
    # Internal search (existing A01)
    _, stdout, _ = client.exec_command(
        "curl -fsS 'http://localhost:8011/internal/search/admin?token=search-token-compose-8011&q=test'",
        timeout=5
    )
    internal = json.loads(stdout.read().decode())
    assert "clusters" in internal, f"Internal search failed: {internal}"
    print(f"  GET /internal/search/admin -> A01 confirmed (has clusters)")
    
    # Contract test
    _, stdout, _ = client.exec_command(f"cd {APP_DIR} && node tests/contract.test.js", timeout=10)
    contract = stdout.read().decode().strip()
    assert "passed" in contract, f"Contract test failed: {contract}"
    print(f"  Contract tests -> {contract}")
    
    # Internal search (existing A01)
    _, stdout, _ = client.exec_command(
        "curl -fsS 'http://localhost:8011/internal/search/admin?token=search-token-compose-8011&q=test'",
        timeout=5
    )
    internal = json.loads(stdout.read().decode())
    assert "clusters" in internal, f"Internal search failed: {internal}"
    print(f"  GET /internal/search/admin -> A01 confirmed (has clusters)")
    
    # Contract test
    _, stdout, _ = client.exec_command(f"cd {APP_DIR} && node tests/contract.test.js", timeout=10)
    contract = stdout.read().decode().strip()
    assert "passed" in contract, f"Contract test failed: {contract}"
    print(f"  Contract tests -> {contract}")
    
    print("\n=== ALL SMOKE TESTS PASSED ===")

finally:
    # Tear down
    print("\nTearing down...")
    run(f"cd {APP_DIR} && docker compose down -v", timeout=30)
    run("docker system prune -a -f --volumes", timeout=60)
    print("Teardown complete.")
    client.close()
