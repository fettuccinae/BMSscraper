from seleniumbase import SB
from .parser import parserService
from flask import current_app


def scrape(tix_urls: list[tuple], movie_urls: list[tuple]) -> tuple[list[dict], list[bool]]:
    with SB(uc=True, locale="en", xvfb=True, headless=True) as sb:
        parser = parserService()
        slot_list = []
        available_list = []
        sb.activate_cdp_mode()
        
        for t_url in tix_urls:
            sb.cdp.open(t_url[1])
            source = sb.cdp.get_page_source()
            tries = 0
            while tries < 11:
                if not parser.is_popular_page(source):
                    break
                sb.cdp.open(t_url[1])
                sb.sleep(2.4)
                source = sb.cdp.get_page_source()
                tries+=1
            
            if tries >= 11:
                current_app.logger.error(f"Thi shi is creating problems{t_url[0]}")
                continue


            sb.sleep(2.1)
            slot_list.append((t_url[0], get_prasad_slots(sb, parser)))

        for m_url in movie_urls:
            sb.cdp.open(m_url[1])
            sb.sleep(2.2)
            source = sb.cdp.get_page_source()
            tries = 0
            while tries < 11:
                if not parser.is_popular_page(source):
                    break
                sb.cdp.open(m_url[1])
                sb.sleep(2.4)
                source = sb.cdp.get_page_source()
                tries+=1
            
            if tries >= 11:
                current_app.logger.error(f"Thi shi is creating problems{m_url[0]}")
                continue
            
            available_list.append((m_url[0], parser.check_if_movie_available(source)))

        return (slot_list, available_list)


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


def get_prasad_slots(sb: SB, parser: parserService):
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

        except Exception as err:
            current_app.logger.error(err)

    return dih
