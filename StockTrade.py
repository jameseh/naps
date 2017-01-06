#!/usr/bin/env python3
'''
Automatically buy and sell stocks.

Part of naps (neopets automation program suite)
'''


import bs4
import re
import sqlite3
import time
from NeoSession import NeoSession


class TradeStocks(NeoSession):
    stock_list = []
    portfolio_list = []

    def __init__(self):
        self.buy_volume = '1000'
        self.parse_stocks()
        self.write_data_db()
        # self.lowest_stock = self.find_lowest_stock()
        # self.buy_stock()

    def write_data_db(self):
        stock_data = sqlite3.connect('stockdata.db')
        cur = stock_data.cursor()
        try:
            cur.execute('''CREATE TABLE stocks
                                               (ticker TEXT, volume INTEGER, open INTEGER, curr INTEGER, change TEXT, time FLOAT)''')
            cur.execute('''CREATE TABLE portfolio
                                               (ticker TEXT, volume INTEGER, price INTEGER, time FLOAT)''')
        except sqlite3.OperationalError:
            for stocks in self.stock_list:
                cur.execute('''INSERT INTO stocks (ticker, volume, open, curr, change, time) VALUES (?, ?, ?, ?, ?, ?)''', (stocks['ticker'], stocks['volume'], stocks['open'], stocks['curr'], stocks['change'], stocks['time']))
                cur.execute('''INSERT INTO portfolio (ticker, volume, price, time) VALUES (?, ?, ?, ?)''', (stocks['ticker'], stocks['volume'], stocks['curr'], stocks['time']))
            stock_data.commit()
            cur.close()

    def buy_stock(self):
        url = 'http://www.neopets.com/stockmarket.phtml?type=buy&ticker={}' \
            .format(self.lowest_stock['ticker'])
        resp = self.get(url)
        ref_ck = re.search(r"'&_ref_ck=(\w*)';", resp.text).group(1)
        url = 'http://www.neopets.com/process_stockmarket.phtml'
        resp = self.post(url, data={'type': 'buy', 'ticker_symbol': self.lowest_stock['ticker'], 'amount_shares': buy_volume, '_ref_ck': ref_ck})

        if 'Error: Sorry, that would' in resp.text:
            print('Over daily 1000 shares.')
            pass
        else:
            self.get('http://www.neopets.com/stockmarket.phtml?type=portfolio')
            print('{} shares of {} bought.'.format(self.buy_volume, self.lowest_stock['ticker']))

    def parse_stocks(self):
        url = 'http://www.neopets.com/stockmarket.phtml?type=list&full=true'
        resp = self.get(url)
        soup = bs4.BeautifulSoup(resp.text, 'lxml')
        table = soup.findAll('table')[7]
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            self.stock_list.append({'ticker': cells[1].string.strip(),
                                    'link': cells[1].string.strip(),
                                    'volume': cells[3].string.strip(),
                                    'open': cells[4].string.strip(),
                                    'curr': cells[5].string.strip(),
                                    'change': cells[6].string.strip(),
                                    'time': time.time()})
            print(stock_list)
            return stock_list

    def find_lowest_stock(self):
        negative_stocks = []
        for stocks in self.stock_list:
            if '-' in stocks['change']:
                if int(stocks['volume']) >= 1000:
                    if int(stocks['curr']) >= 15:
                        if int(stocks['curr']) <= 17:
                            negative_stocks.append(stocks)
            if len(negative_stocks) == 0:
                 pass
            else:
                self.lowest_stock = negative_stocks[0]
                return self.lowest_stock
            if len(negative_stocks) > 1:
                lowest_stock = negative_stocks[0][1]
                if float(negative_stocks[1]) > float(lowest_stock[1]):
                    self.lowest_stock = stocks
                return self.lowest_stock


def main():
    TradeStocks()


if __name__ == '__main__':
    main()
