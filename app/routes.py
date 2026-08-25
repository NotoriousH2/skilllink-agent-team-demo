from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

from app.db import connect
from app.labels import (
    APPLICATION_STATUS_LABELS,
    CATEGORY_LABELS,
    LISTING_STATUS_LABELS,
    TYPE_LABELS,
)
from app.seed import now

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
_jinja_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=True,
)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env = _jinja_env

CATEGORIES = ("study", "repair", "cooking", "tech", "other")
TYPES = ("offer", "request")
LISTING_STATUSES = ("open", "matched", "completed", "cancelled")
APP_STATUSES = ("pending", "accepted", "rejected", "cancelled")
SELECT_VALUES = ("1", "2", "3", "4", "operator")
PAGE_SIZE = 10


def current_user(request: Request):
    value = request.cookies.get("current_user_id", "1")
    if value == "operator":
        return "operator", None
    try:
        uid = int(value)
    except ValueError:
        return "1", None
    if uid not in (1, 2, 3, 4):
        return "1", None
    return value, uid


def render(request: Request, name: str, status_code: int = 200, **ctx):
    value, uid = current_user(request)
    ctx.setdefault("current_value", value)
    ctx.setdefault("current_uid", uid)
    ctx.setdefault("is_operator", value == "operator")
    ctx.setdefault("current_name", "운영자" if value == "operator" else f"사용자 {value}")
    ctx.setdefault("category_labels", CATEGORY_LABELS)
    ctx.setdefault("type_labels", TYPE_LABELS)
    ctx.setdefault("listing_status_labels", LISTING_STATUS_LABELS)
    ctx.setdefault("application_status_labels", APPLICATION_STATUS_LABELS)
    return templates.TemplateResponse(request, name, status_code=status_code, context=ctx)


def error_page(request: Request, status_code: int, message: str):
    return render(request, "error.html", status_code=status_code, message=message)


def listing_card_rows(conn, q=None, category=None, type_=None, status=None, page=1):
    sql = "SELECT l.*, u.name AS owner_name FROM listings l JOIN users u ON u.id = l.owner_id WHERE 1=1"
    params = []
    if q:
        sql += " AND (l.title LIKE ? OR l.description LIKE ?)"
        like = f"%{q}%"
        params += [like, like]
    if category:
        sql += " AND l.category = ?"
        params.append(category)
    if type_:
        sql += " AND l.type = ?"
        params.append(type_)
    if status:
        sql += " AND l.status = ?"
        params.append(status)
    sql += " ORDER BY l.id DESC"
    count_sql = sql.replace("SELECT l.*, u.name AS owner_name", "SELECT COUNT(*)")
    count_row = conn.execute(count_sql, params).fetchone()[0]
    total_pages = max(1, (count_row + PAGE_SIZE - 1) // PAGE_SIZE)
    offset = (page - 1) * PAGE_SIZE
    rows = conn.execute(sql + " LIMIT ? OFFSET ?", params + [PAGE_SIZE, offset]).fetchall()
    return rows, count_row, total_pages


@router.get("/")
def home(request: Request):
    q = request.query_params.get("q")
    category = request.query_params.get("category")
    type_ = request.query_params.get("type")
    status = request.query_params.get("status")
    page_raw = request.query_params.get("page", "1")
    if q is not None and len(q) > 200:
        return error_page(request, 422, "검색어는 200자 이하만 가능합니다.")
    if category is not None and category not in CATEGORIES:
        return error_page(request, 422, "카테고리가 올바르지 않습니다.")
    if type_ is not None and type_ not in TYPES:
        return error_page(request, 422, "유형이 올바르지 않습니다.")
    if status is not None and status not in LISTING_STATUSES:
        return error_page(request, 422, "상태가 올바르지 않습니다.")
    try:
        page = int(page_raw)
    except ValueError:
        return error_page(request, 422, "페이지 번호가 올바르지 않습니다.")
    if page < 1:
        return error_page(request, 422, "페이지 번호는 1 이상이어야 합니다.")
    conn = connect()
    try:
        rows, count, total_pages = listing_card_rows(conn, q, category, type_, status, page)
    finally:
        conn.close()
    cards = []
    for r in rows:
        desc = r["description"]
        cards.append(
            {
                "id": r["id"],
                "title": r["title"],
                "owner_name": r["owner_name"],
                "type": r["type"],
                "category": r["category"],
                "status": r["status"],
                "description": desc[:60] + ("…" if len(desc) > 60 else ""),
            }
        )
    return render(
        request,
        "home.html",
        cards=cards,
        q=q or "",
        category=category or "",
        type_=type_ or "",
        status=status or "",
        page=page,
        total_pages=total_pages,
        count=count,
    )


@router.get("/health")
def health():
    return JSONResponse({"status": "ok"})


@router.get("/activity")
def activity(request: Request):
    value, uid = current_user(request)
    if value == "operator":
        return error_page(request, 403, "운영자는 활동 페이지를 볼 수 없습니다.")
    conn = connect()
    try:
        my_listings = conn.execute(
            "SELECT l.*, u.name AS owner_name FROM listings l JOIN users u ON u.id = l.owner_id WHERE l.owner_id = ? ORDER BY l.id DESC",
            (uid,),
        ).fetchall()
        my_apps = conn.execute(
            "SELECT a.*, l.title AS listing_title FROM applications a JOIN listings l ON l.id = a.listing_id WHERE a.applicant_id = ? ORDER BY a.id DESC",
            (uid,),
        ).fetchall()
    finally:
        conn.close()
    return render(request, "activity.html", my_listings=my_listings, my_apps=my_apps)


@router.get("/admin")
def admin(request: Request):
    value, _ = current_user(request)
    if value != "operator":
        return error_page(request, 403, "관리자 페이지는 운영자만 볼 수 있습니다.")
    conn = connect()
    try:
        total_listings = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        by_status = {
            s: conn.execute("SELECT COUNT(*) FROM listings WHERE status = ?", (s,)).fetchone()[0]
            for s in LISTING_STATUSES
        }
        by_category = {
            c: conn.execute("SELECT COUNT(*) FROM listings WHERE category = ?", (c,)).fetchone()[0]
            for c in CATEGORIES
        }
        by_type = {
            t: conn.execute("SELECT COUNT(*) FROM listings WHERE type = ?", (t,)).fetchone()[0]
            for t in TYPES
        }
        app_by_status = {
            s: conn.execute("SELECT COUNT(*) FROM applications WHERE status = ?", (s,)).fetchone()[
                0
            ]
            for s in APP_STATUSES
        }
        recent_apps = conn.execute(
            "SELECT a.*, l.title AS listing_title, u.name AS applicant_name FROM applications a JOIN listings l ON l.id = a.listing_id JOIN users u ON u.id = a.applicant_id ORDER BY a.id DESC LIMIT 10"
        ).fetchall()
    finally:
        conn.close()
    return render(
        request,
        "admin.html",
        total_listings=total_listings,
        by_status=by_status,
        by_category=by_category,
        by_type=by_type,
        app_by_status=app_by_status,
        recent_apps=recent_apps,
    )


@router.get("/users/select/{value}")
def select_user(request: Request, value: str):
    if value not in SELECT_VALUES:
        return error_page(request, 422, "존재하지 않는 사용자입니다.")
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie(
        "current_user_id", value, path="/", httponly=True, samesite="lax", max_age=2592000
    )
    return resp


@router.get("/listings/new")
def listing_new(request: Request):
    value, _ = current_user(request)
    if value == "operator":
        return error_page(request, 403, "운영자는 게시물을 만들 수 없습니다.")
    return render(request, "listing_form.html", listing=None)


@router.get("/listings/{id}")
def listing_detail(request: Request, id: int):
    conn = connect()
    try:
        row = conn.execute(
            "SELECT l.*, u.name AS owner_name FROM listings l JOIN users u ON u.id = l.owner_id WHERE l.id = ?",
            (id,),
        ).fetchone()
        if row is None:
            return error_page(request, 404, "게시물을 찾을 수 없습니다.")
        apps = conn.execute(
            "SELECT a.*, u.name AS applicant_name FROM applications a JOIN users u ON u.id = a.applicant_id WHERE a.listing_id = ? ORDER BY a.id",
            (id,),
        ).fetchall()
        value, uid = current_user(request)
        accepted = conn.execute(
            "SELECT applicant_id FROM applications WHERE listing_id=? AND status='accepted'", (id,)
        ).fetchone()
        accepted_applicant_id = accepted["applicant_id"] if accepted else None
    finally:
        conn.close()
    return render(
        request,
        "listing_detail.html",
        listing=row,
        apps=apps,
        viewer_uid=uid,
        is_operator=value == "operator",
        accepted_applicant_id=accepted_applicant_id,
    )


@router.get("/listings/{id}/edit")
def listing_edit(request: Request, id: int):
    _, uid = current_user(request)
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM listings WHERE id = ?", (id,)).fetchone()
    finally:
        conn.close()
    if row is None:
        return error_page(request, 404, "게시물을 찾을 수 없습니다.")
    if uid != row["owner_id"]:
        return error_page(request, 403, "본인 게시물만 수정할 수 있습니다.")
    if row["status"] != "open":
        return error_page(request, 409, "진행 중인 게시물만 수정할 수 있습니다.")
    return render(request, "listing_form.html", listing=row)


@router.post("/listings")
def listing_create(
    request: Request,
    title: str = Form(""),
    description: str = Form(""),
    category: str = Form(""),
    type: str = Form(""),
):
    value, uid = current_user(request)
    if value == "operator":
        return error_page(request, 403, "운영자는 게시물을 만들 수 없습니다.")
    title = title.strip()
    if not (1 <= len(title) <= 80):
        return error_page(request, 422, "제목은 1~80자여야 합니다.")
    if not (1 <= len(description) <= 1000):
        return error_page(request, 422, "설명은 1~1000자여야 합니다.")
    if category not in CATEGORIES:
        return error_page(request, 422, "카테고리가 올바르지 않습니다.")
    if type not in TYPES:
        return error_page(request, 422, "유형이 올바르지 않습니다.")
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO listings (owner_id, title, description, category, type, status, created_at) VALUES (?,?,?,?,?,?,?)",
            (uid, title, description, category, type, "open", now()),
        )
        new_id = cur.lastrowid
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/listings/{new_id}", status_code=302)


@router.post("/listings/{id}")
def listing_update(
    request: Request,
    id: int,
    title: str = Form(""),
    description: str = Form(""),
    category: str = Form(""),
    type: str = Form(""),
):
    _, uid = current_user(request)
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM listings WHERE id = ?", (id,)).fetchone()
        if row is None:
            return error_page(request, 404, "게시물을 찾을 수 없습니다.")
        if uid != row["owner_id"]:
            return error_page(request, 403, "본인 게시물만 수정할 수 있습니다.")
        if row["status"] != "open":
            return error_page(request, 409, "진행 중인 게시물만 수정할 수 있습니다.")
        title = title.strip()
        if not (1 <= len(title) <= 80):
            return error_page(request, 422, "제목은 1~80자여야 합니다.")
        if not (1 <= len(description) <= 1000):
            return error_page(request, 422, "설명은 1~1000자여야 합니다.")
        if category not in CATEGORIES:
            return error_page(request, 422, "카테고리가 올바르지 않습니다.")
        if type not in TYPES:
            return error_page(request, 422, "유형이 올바르지 않습니다.")
        conn.execute(
            "UPDATE listings SET title=?, description=?, category=?, type=? WHERE id=?",
            (title, description, category, type, id),
        )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/listings/{id}", status_code=302)


@router.post("/listings/{id}/cancel")
def listing_cancel(request: Request, id: int):
    _, uid = current_user(request)
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM listings WHERE id = ?", (id,)).fetchone()
        if row is None:
            return error_page(request, 404, "게시물을 찾을 수 없습니다.")
        if uid != row["owner_id"]:
            return error_page(request, 403, "본인 게시물만 취소할 수 있습니다.")
        if row["status"] not in ("open", "matched"):
            return error_page(request, 409, "취소할 수 없는 상태입니다.")
        conn.execute("UPDATE listings SET status='cancelled' WHERE id=?", (id,))
        conn.execute(
            "UPDATE applications SET status='rejected' WHERE listing_id=? AND status='pending'",
            (id,),
        )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/listings/{id}", status_code=302)


@router.post("/listings/{id}/complete")
def listing_complete(request: Request, id: int):
    _, uid = current_user(request)
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM listings WHERE id = ?", (id,)).fetchone()
        if row is None:
            return error_page(request, 404, "게시물을 찾을 수 없습니다.")
        if row["status"] != "matched":
            return error_page(request, 409, "완료할 수 없는 상태입니다.")
        accepted_applicant = conn.execute(
            "SELECT applicant_id FROM applications WHERE listing_id=? AND status='accepted'", (id,)
        ).fetchone()
        is_accepted_applicant = (
            accepted_applicant is not None and uid == accepted_applicant["applicant_id"]
        )
        if uid != row["owner_id"] and not is_accepted_applicant:
            return error_page(request, 403, "완료할 권한이 없습니다.")
        conn.execute("UPDATE listings SET status='completed' WHERE id=?", (id,))
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/listings/{id}", status_code=302)


@router.post("/applications")
def application_create(request: Request, listing_id: int = Form(0), message: str = Form("")):
    value, uid = current_user(request)

    if value == "operator":
        return error_page(request, 403, "운영자는 신청할 수 없습니다.")
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
        if row is None:
            return error_page(request, 404, "게시물을 찾을 수 없습니다.")
        if uid == row["owner_id"]:
            return error_page(request, 403, "본인 게시물에는 신청할 수 없습니다.")
        if row["status"] != "open":
            return error_page(request, 409, "신청할 수 없는 상태입니다.")
        existing = conn.execute(
            "SELECT id FROM applications WHERE listing_id=? AND applicant_id=? AND status='pending'",
            (listing_id, uid),
        ).fetchone()
        if existing is not None:
            return error_page(request, 409, "이미 대기 중인 신청이 있습니다.")
        if not (1 <= len(message) <= 500):
            return error_page(request, 422, "메시지는 1~500자여야 합니다.")
        conn.execute(
            "INSERT INTO applications (listing_id, applicant_id, message, status, created_at) VALUES (?,?,?,?,?)",
            (listing_id, uid, message, "pending", now()),
        )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/listings/{listing_id}", status_code=302)


@router.post("/applications/{id}/accept")
def application_accept(request: Request, id: int):
    _, uid = current_user(request)
    conn = connect()
    try:
        app = conn.execute(
            "SELECT a.*, l.owner_id FROM applications a JOIN listings l ON l.id = a.listing_id WHERE a.id = ?",
            (id,),
        ).fetchone()
        if app is None:
            return error_page(request, 404, "신청을 찾을 수 없습니다.")
        if uid != app["owner_id"]:
            return error_page(request, 403, "게시물 소유자만 수락할 수 있습니다.")
        listing = conn.execute("SELECT * FROM listings WHERE id=?", (app["listing_id"],)).fetchone()
        if app["status"] != "pending" or listing["status"] != "open":
            return error_page(request, 409, "수락할 수 없는 상태입니다.")
        conn.execute("UPDATE applications SET status='accepted' WHERE id=?", (id,))
        conn.execute(
            "UPDATE applications SET status='rejected' WHERE listing_id=? AND status='pending' AND id != ?",
            (app["listing_id"], id),
        )
        conn.execute("UPDATE listings SET status='matched' WHERE id=?", (app["listing_id"],))
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/listings/{app['listing_id']}", status_code=302)


@router.post("/applications/{id}/reject")
def application_reject(request: Request, id: int):
    _, uid = current_user(request)
    conn = connect()
    try:
        app = conn.execute(
            "SELECT a.*, l.owner_id FROM applications a JOIN listings l ON l.id = a.listing_id WHERE a.id = ?",
            (id,),
        ).fetchone()
        if app is None:
            return error_page(request, 404, "신청을 찾을 수 없습니다.")
        if uid != app["owner_id"]:
            return error_page(request, 403, "게시물 소유자만 거절할 수 있습니다.")
        if app["status"] != "pending":
            return error_page(request, 409, "거절할 수 없는 상태입니다.")
        conn.execute("UPDATE applications SET status='rejected' WHERE id=?", (id,))
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/listings/{app['listing_id']}", status_code=302)


@router.post("/applications/{id}/cancel")
def application_cancel(request: Request, id: int):
    _, uid = current_user(request)
    conn = connect()
    try:
        app = conn.execute(
            "SELECT a.* FROM applications a WHERE a.id = ?",
            (id,),
        ).fetchone()
        if app is None:
            return error_page(request, 404, "신청을 찾을 수 없습니다.")
        if uid != app["applicant_id"]:
            return error_page(request, 403, "본인 신청만 취소할 수 있습니다.")
        if app["status"] != "pending":
            return error_page(request, 409, "취소할 수 없는 상태입니다.")
        conn.execute("UPDATE applications SET status='cancelled' WHERE id=?", (id,))
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse(f"/listings/{app['listing_id']}", status_code=302)
