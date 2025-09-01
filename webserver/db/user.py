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


def i_run_through_them_all(frequency: int) -> dict:

    time_rn = datetime.now(timezone.utc)
    delta = f"{frequency} hour"
    query = text("SELECT * FROM user_notification WHERE  :time_rn + :delta >= last_check_time AND notification_sent = false")
    with db.engine.connect() as conn:
        res = conn.execute(query, {"time_rn": time_rn, "delta": delta})
        return res.mappings().fetchall()
    
def update_notifications(list_of_tuples_for_tickets: list[tuple[int, dict]], list_of_tuples_for_movies: list[tuple[int, bool]]):
    real_ones = []
    query = text(
        """
            WITH updated AS (
                UPDATE user_notification
                SET detail = :yeah,
                    last_check_time = NOW(),
                    notification_sent = CASE
                        WHEN
                            detail != :yeah
                        THEN
                            true
                        ELSE
                            false
                    END

                WHERE rem_id = :id
                RETURNING rem_id, detail, notification_sent
            )

            SELECT rem_id
            FROM updated
            WHERE notification_sent = true
        """
    )
    with db.engine.connect() as conn:
        for i in list_of_tuples_for_tickets:
            res = conn.execute(query, {"yeah": json.dumps(i[1]), "id": i[0]})
            real_ones.append(res.scalar())

        for j in (
            list_of_tuples_for_movies
        ):  # there might be a good reason to not use single name variables. maybe bugs.
            res = conn.execute(query, {"yeah": json.dumps({"available": j[1]}), "id": j[0]})
            real_ones.append(res.scalar())

        conn.commit()
    return real_ones


def get_notifications_by_rem_ids(rem_ids: list[int]):
    query = text(
        """SELECT detail, rem_id, mail_id, scrape_url FROM user_notification JOIN "user" ON user_notification.user_id = "user".id WHERE rem_id IN :rem_ids"""
    )
    with db.engine.connect() as conn:
        res = conn.execute(query, {"rem_ids": tuple(rem_ids)})
        return res.mappings().fetchall()