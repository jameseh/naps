#!/usr/bin/env python3
'''
Purchase items from user-shops via shop wizard.

Part of naps (neopets automation program suite)
'''

import re
from NeoSession import NeoSession


class ShopWizard(NeoSession):

    def buy_item(self, search_query=None):
        url = 'http://www.neopets.com/market.phtml?type=wizard'
        resp = self.get(url)
        url = 'http://www.neopets.com/market.phtml'
        data = {'type': 'process_wizard', 'feedset': '0',
                                       'shopwizard': search_query,
                                       'table': 'shop', 'criteria': 'exact',
                                       'min_price': '0', 'max_price': '99999'}
        self.session.headers.update({'Origin': 'http://www.neopets.com'})
        resp = self.post(url, data)
        if search_query not in resp.text:
            print('Log: ShopWizard - Search query failed.')
        else:
            link = re.search(r'(<a href=")(/browseshop\.phtml\?owner=.*?&buy_o'
                             r'bj_info_id=\d+?&buy_cost_neopoints=\d+?)("><b>)',
                             resp.text)
            url = 'http://www.neopets.com{}'.format(link.group(2))
            resp = self.get(url)
            find_url = re.search(
                r'(<A href=")(buy_item\.phtml\?lower=0&owner=.*?)(" onClick='
                r'.*?<b>{}</b>)'.format(search_query), resp.text)
            url = 'http://www.neopets.com/{}'.format(find_url.group(2))
            resp = self.get(url)
            print('Log: ShopWizard - Bought {}'.format(search_query))


def main():
    ShopWizard()


if __name__ == '__main__':
    main()
