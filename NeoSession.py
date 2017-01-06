#!/usr/bin/env python3
'''
Mimics a neopets websession, handles cookies, headers, updating referer
header and human-like pauses.

Part of naps (neopets automation program suite)
'''


import requests
import pickle
import json
import os
import sys
import random
import time
import configparser as cp


class NeoSession:
    '''Login to neopets.com'''
    conf = cp.ConfigParser()
    conf.read('settings.conf')
    session = requests.Session()
    username = conf['USER-SETTINGS']['USERNAME']
    login_data = {'username': username, 'password': conf['USER-SETTINGS']['PASSWORD'], 'destination': '%2Findex.phtml'}
    jar = conf['PROGRAM-SETTINGS']['COOKIE_JAR']
    pause_tuple = (2, 4)

    def __init__(self):
        self.load_cookies()
        self.load_headers()

    def get(self, url, pause=pause_tuple):
        time.sleep(random.randint(pause[0], pause[1]))
        resp = self.session.get(url)
        self.session.headers.update({'Referer': resp.url})

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            print('Log: Connection error.')

        if self.login_status(resp) is not True:
            self.login()
        else:
            return resp

    def post(self, url, data=None, pause=pause_tuple):
        time.sleep(random.randint(pause[0], pause[1]))

        if data is None:
            resp = self.session.post(url)
            self.session.headers.update({'Referer': resp.url})

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError:
                print('Log: Connection error.')

            if self.login_status(resp) is False:
                print('Log: Logging in.')
                self.login()
            else:
                return resp
        else:
            resp = self.session.post(url, data)
            print(resp.url)
            self.session.headers.update({'Referer': resp.url})

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError:
                print('Log: Connection error.')

            if self.login_status(resp) is False:
                self.login()
            else:
                return resp

    def update_cookies(self):
        if os.path.isfile(self.jar):
            with open(self.jar, 'wb') as jar:
                pickle.dump(self.session.cookies, jar)

    def load_cookies(self):
        if os.path.isfile(self.jar):
            if os.path.getsize(self.jar) is not 0:
                with open(self.jar, 'rb') as jar:
                    session_cookies = pickle.load(jar)
                    self.session.cookies.update(session_cookies)

    def load_headers(self):
        with open(self.conf['PROGRAM-SETTINGS']['HEADERS'], 'r') as headers:
            session_headers = json.load(headers)
            self.session.headers.update(session_headers)

    def login_status(self, resp):
        if 'Welcome, <a href="/userlookup.phtml?user={}">'.format(
                self.username) not in resp.text:
            print('Log: Logging in.')
            self.login()
            return False

        if 'Welcome, <a href="/userlookup.phtml?user={}">'.format(
                self.username) in resp.text:
            print('Log: Login check passed. [{}]'.format(resp.url))
            self.update_cookies()
            return True

        else:
            print('Log: Login check failed.')
            sys.exit(1)

    def login(self):
        '''Log-in to neopets.com'''
        url = 'http://www.neopets.com/login.phtml'
        resp = self.post(url, data=self.login_data)
        self.session.headers.update({'Referer': resp.url})

        if os.path.isfile(self.jar) is not True:
            os.system('touch neopets.cookies')
            self.session_cookies = resp.cookies

        self.update_cookies(self.session.cookies)
        print('Login successful.')


def main():
    NeoSession()


if __name__ == '__main__':
    main()
