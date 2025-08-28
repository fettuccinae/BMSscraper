import json

from sqlalchemy import text
from datetime import datetime, timezone

from webserver import db


def check_if_user_name_is_unique(user_name: str) -> bool:
    query = 'SELECT user_name FROM "user" WHERE user_name = :user_name'
    with db.engine.connect() as conn:
        res = conn.execute(text(query), {"user_name": user_name})
        if res.rowcount == 0:
            return True
        else:
            return False


def register_user(user_name: str, password_hash: str):
    mail_id = user_name
    query = 'INSERT INTO "user" (user_name, password_hash, mail_id) VALUES (:user_name, :password_hash, :mail_id)'
    with db.engine.begin() as conn:
        conn.execute(
            text(query),
            {"user_name": user_name, "password_hash": password_hash, "mail_id": mail_id},
        )


def get_user(user_name: str, user_id: str = None):
    query = 'SELECT * FROM "user" WHERE (:user_name IS NULL OR user_name=:user_name) AND (:user_id IS NULL OR id = :user_id)'
    with db.engine.connect() as conn:
        res = conn.execute(text(query), {"user_name": user_name, "user_id": user_id})
        return res.mappings().fetchone()


def add_new_notification_event(user_id: int, url: str, option: str, frequency: int) -> dict:
    query = text(
        """
        INSERT INTO 
        user_notification (user_id, scrape_url, scrape_option, notification_frequency)
        VALUES (:user_id, :url, :option, :frequency)
        RETURNING *
        """
    )
    params = {
        "user_id": user_id,
        "url": url,
        "option": option,
        "frequency": frequency,
    }
    with db.engine.begin() as conn:
        res = conn.execute(query, params)
        res2 = conn.execute(
            text('SELECT mail_id FROM "user" WHERE id=:user_id'), {"user_id": user_id}
        )

        result = dict(res.mappings().fetchone())
        result["mail_id"] = res2.scalar()

        return result


def get_user_notifications(user_id: int) -> dict:
    query = text("SELECT * FROM user_notification WHERE user_id = :user_id")
    with db.engine.connect() as conn:
        res = conn.execute(query, {"user_id": user_id})
        return res.mappings().fetchall()


def add_notification_detail(rem_id: int, detail: dict) -> dict:
    detail = json.dumps(detail)
    query = text(
        "UPDATE user_notification SET detail = :detail, last_check_time = :time WHERE rem_id = :rem_id"
    )

    with db.engine.begin() as conn:
        conn.execute(
            query, {"detail": detail, "time": datetime.now(timezone.utc), "rem_id": rem_id}
        )
