from flask import (
    Blueprint,
    url_for,
    request,
    flash,
    current_app,
    render_template,
    g,
    redirect,
    jsonify,
)
import re
import json
from webserver.decorators import login_required
from webserver.db.user import (
    add_new_notification_event,
    get_user_notifications,
    add_notification_detail,
)
from webserver.scrape.scraper import scrape
from webserver.mail import send_mail

tix_bp = Blueprint("tix", __name__)


@tix_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_event():
    if request.method == "POST":
        url = request.form.get("scrape_url")
        option = request.form.get("scrape_option")
        frequency = request.form.get("frequency")
        # from_ts = _convert_string_time_to_int(request.form.get("from_time"))
        # to_ts = _convert_string_time_to_int(request.form.get("till_time"))

        if not url or not option or not frequency:
            flash("Please select errthing")

        elif (
            option not in ("tickets", "movie")
            or re.search(r"(https:\/\/in\.bookmyshow\.com\/movies\/hyderabad)(.*)", url).group(1)
            != "https://in.bookmyshow.com/movies/hyderabad"
        ):
            flash("what the helli")

        else:
            try:
                notification = add_new_notification_event(g.user["id"], url, option, frequency)

                detail = scrape(notification["scrape_url"], notification["scrape_option"])
                add_notification_detail(notification["rem_id"], detail)
                if detail["available"] is True:
                    name = re.search(r"(.*\/hyderabad\/)([^\/]+)(\/.*)", url).group(2)
                    send_mail(
                        f"Update for {name} in BMS", json.dumps(detail), notification["mail_id"]
                    )
                else:
                    current_app.logger.info("NOT YET BRO")

                flash("When its available, A mail will be sent on your mail id")

                return redirect(url_for("tix.index"))
            except Exception as err:
                flash("SOME ERROR SHAW")
                current_app.logger.error(err)

    return render_template("tix/add_event.html")


@tix_bp.get("/")
@login_required
def index():
    all_notifications = get_user_notifications(g.user["id"])
    return render_template("tix/index.html", notifications=all_notifications)


@tix_bp.get("/cron-jobs")
def cron():
    secret = request.args.get("secret")
    if not secret or secret != current_app.config["CRON_SECRET"]:
        return jsonify({"status": "nah"}), 401
    else:
        run_hourly_job()
        return jsonify({"status": "aight"})


def _convert_string_time_to_int(time: str) -> int:
    return int(time[:2] + time[3:])


def run_hourly_job():
    current_app.logger.info("HELLO")
