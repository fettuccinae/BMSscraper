from lxml.html import fromstring


class fuckOOP:
    def prasads_2d_slots(self, html_content, curr_url) -> dict:
        lxed_html = fromstring(html_content)

        theatres_and_times = "sc-e8nk8f-3 hStBrg"
        time_class = "sc-1vhizuf-2 jIiAgZ"
        dates_pane = "sc-9bxw9f-5 iterBd"
        active_dates_pane = "sc-6bpksa-0 gJVIzf"
        curr_date = int(curr_url[-8:])

        # finding theatre.
        t_name = "Prasads Multiplex: Hyderabad"

        all_intersting_shit = lxed_html.xpath(f'//div[@class="{theatres_and_times}"]')
        shit_we_need = self.find_shit_and_return_subtree(all_intersting_shit, t_name)

        available_slots = self.return_all_times(shit_we_need, time_class) if len(shit_we_need) else None
        next_date = self.next_date_or_nah(lxed_html, dates_pane, active_dates_pane, curr_date)

        return {"slots": available_slots, "next_date": next_date}

    def find_shit_and_return_subtree(self, nodes, target):
        for node in nodes:
            name = node.xpath(f'.//span[text()="{target}"]')
            if name:
                return node

        return None

    def check_if_movie_available(self, source):
        bruh = fromstring(source).xpath('//span[text()="Book tickets"]')
        if not bruh:
            return False
        return True

    def return_all_times(self, node, time_class):
        all_the_times = node.xpath(f'.//div[@class="{time_class}"]/text()')
        return all_the_times

    def next_date_or_nah(self, lxed_html, dates_pane, active_dates_pane, curr_date):
        next_date_ids = lxed_html.xpath(
            f'//div[@class="{dates_pane}"]/div/div[@class="{active_dates_pane}"]/@id'
        )
        for next_date in next_date_ids:
            if int(next_date) > curr_date:
                return int(next_date)
        return None
