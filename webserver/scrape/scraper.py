from seleniumbase import SB
from .parser import fuckOOP
from flask import current_app


def scrape(url: str, option: str) -> dict:
    with SB(uc=True, locale="en", xvfb=True, headless=True) as sb:
        parser = fuckOOP()

        sb.activate_cdp_mode(url)
        sb.sleep(2.1)
        source_code = sb.cdp.get_page_source()
        if option == "movie":
            available = parser.check_if_movie_available(source_code)
            return {"available": available}

        else:
            # do_all_shenanigans_and_land_on_booking_page(sb)
            return get_prasad_slots(sb, parser)


# def do_all_shenanigans_and_land_on_booking_page(sb, fourD=False):
#     book_tix_button = "sc-1vmod7e-2 ixpVNC"
#     sb.cdp.click(f"{book_tix_button}")
#     sb.sleep(2.3)

#     xpath = f"//span[text()='{'4DX' if fourD else '2D'}']"
#     try:
#         age_warning_continue = "sc-ttkokf-2 sc-ttkokf-3 bIIppr hIYQmz"
#         sb.cdp.click(f"{age_warning_continue}")
#         sb.sleep(2.2)
#     except Exception:
#         current_app.logger.info("No warning")

#     try:
#         sb.cdp.click(xpath)
#         sb.sleep(2.4)
#     except Exception:
#         current_app.logger.info("NO option")


def get_prasad_slots(sb: SB, parser: fuckOOP):
    dih = {"available": True}

    while True:
        try:
            url = sb.cdp.get_current_url()
            source_code = sb.cdp.get_page_source()
            sb.sleep(1.3)

            lil_one = parser.prasads_2d_slots(source_code, url)
            slots = lil_one.get("slots")
            next_date = lil_one.get("next_date")

            dih[url[-8:]] = (slots) if slots else "No slots"

            if next_date is None:
                current_app.logger.info("Done")
                break
            else:
                sb.cdp.click(f'//div[id="{next_date}"]')

        except Exception:
            break

    return dih
