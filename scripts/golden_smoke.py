import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, build_opener


def fail(step: str):
    print(f"GOLDEN SMOKE FAIL: {step}")
    sys.exit(1)


def main():
    tmpdir = tempfile.mkdtemp(prefix="skilllink_smoke_")
    db_path = Path(tmpdir) / "smoke.db"
    env = dict(os.environ, SKILLLINK_DB=str(db_path))
    proc = subprocess.Popen(
        [
            "uv",
            "run",
            "python",
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8322",
        ],
        env=env,
        cwd=Path(__file__).resolve().parent.parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        # 1. health
        deadline = time.time() + 30
        ok = False
        while time.time() < deadline:
            try:
                with urllib.request.urlopen("http://127.0.0.1:8322/health", timeout=2) as r:
                    if r.status == 200 and r.read().decode() == '{"status":"ok"}':
                        ok = True
                        break
            except Exception:  # noqa: S110,BLE001
                pass
            time.sleep(0.5)
        if not ok:
            fail("health")

        jar = CookieJar()
        opener = build_opener(urllib.request.HTTPCookieProcessor(jar))

        # 2. home
        with opener.open("http://127.0.0.1:8322/", timeout=5) as r:
            body = r.read().decode()
            if (
                r.status != 200
                or "파이썬 기초 과외" not in body
                or "카페에서 사진 촬영" not in body
            ):
                fail("home")

        # 3. XSS listing create
        jar.clear()
        opener = build_opener(urllib.request.HTTPCookieProcessor(jar))
        jar.set_cookie(_cookie("current_user_id", "1"))
        data = urlencode(
            {
                "title": "<script>alert('smoke')</script> 제목",
                "description": "설명",
                "category": "other",
                "type": "offer",
            }
        ).encode()
        req = Request("http://127.0.0.1:8322/listings", data=data, method="POST")
        opener2 = build_opener(urllib.request.HTTPCookieProcessor(jar), NoRedirect())
        try:
            with opener2.open(req, timeout=5) as r:
                if r.status != 302:
                    fail("create_xss_listing")
                loc = r.headers.get("Location")
        except urllib.error.HTTPError as e:
            if e.code != 302:
                fail("create_xss_listing")
            loc = e.headers.get("Location")
        new_id = loc.split("/")[-1]
        with opener.open(f"http://127.0.0.1:8322/listings/{new_id}", timeout=5) as r:
            body = r.read().decode()
            if r.status != 200:
                fail("xss_detail_status")
            if "<script>alert('smoke')</script>" in body:
                fail("xss_raw_script")
            if "&lt;script&gt;" not in body:
                fail("xss_escaped_missing")

        # 4. application by user 2
        jar.clear()
        opener = build_opener(urllib.request.HTTPCookieProcessor(jar))
        jar.set_cookie(_cookie("current_user_id", "2"))
        data = urlencode({"listing_id": "1", "message": "스모크 신청 메시지"}).encode()
        req = Request("http://127.0.0.1:8322/applications", data=data, method="POST")
        opener2 = build_opener(urllib.request.HTTPCookieProcessor(jar), NoRedirect())
        try:
            with opener2.open(req, timeout=5) as r:
                if r.status != 302:
                    fail("apply")
        except urllib.error.HTTPError as e:
            if e.code != 302:
                fail("apply")
        with opener.open("http://127.0.0.1:8322/listings/1", timeout=5) as r:
            body = r.read().decode()
            if r.status != 200 or "스모크 신청 메시지" not in body:
                fail("apply_detail")

        # 5. duplicate apply 409
        data = urlencode({"listing_id": "1", "message": "중복 신청"}).encode()
        req = Request("http://127.0.0.1:8322/applications", data=data, method="POST")
        try:
            opener.open(req, timeout=5)
            fail("duplicate_apply_expected_409")
        except urllib.error.HTTPError as e:
            if e.code != 409:
                fail("duplicate_apply_expected_409")

        # 6. accept application 4 (smoke application)
        jar.clear()
        opener = build_opener(urllib.request.HTTPCookieProcessor(jar))
        jar.set_cookie(_cookie("current_user_id", "1"))
        req = Request("http://127.0.0.1:8322/applications/4/accept", method="POST")
        opener2 = build_opener(urllib.request.HTTPCookieProcessor(jar), NoRedirect())
        try:
            with opener2.open(req, timeout=5) as r:
                if r.status != 302:
                    fail("accept")
        except urllib.error.HTTPError as e:
            if e.code != 302:
                fail("accept")
        with opener.open("http://127.0.0.1:8322/listings/1", timeout=5) as r:
            body = r.read().decode()
            if r.status != 200 or "매칭 완료" not in body:
                fail("matched_badge")

        print("GOLDEN SMOKE PASS")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _cookie(name: str, value: str):
    from http.cookiejar import Cookie

    return Cookie(
        0,
        name,
        value,
        None,
        False,
        "127.0.0.1",
        True,
        False,
        "/",
        True,
        False,
        None,
        False,
        None,
        None,
        {},
    )


if __name__ == "__main__":
    main()
