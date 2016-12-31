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
    login_data = {'username': username,
                  'password': conf['USER-SETTINGS']['PASSWORD'], }
    jar = conf['PROGRAM-SETTINGS']['COOKIE_JAR']
    pause = (2, 4)

    def __init__(self):
        self.load_session_cookies()
        self.load_session_headers()
        self.update_session_cookies()

    def session_get(self, url, pause=pause):
        time.sleep(random.randint(pause[0], pause[1]))
        self.session.headers.update({'Referer': url})
        resp = self.session.get(url)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            print('Log: Connection error.')
        if self.check_login(resp) is not True:
            self.login()
            resp = self.session.get(url)
            self.check_login(resp)
        else:
            return resp

    def session_post(self, url, data=None, pause=pause):
        time.sleep(random.randint(pause[0], pause[1]))
        self.session.headers.update({'Referer': url})
        if data is None:
            resp = self.session.post(url)
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError:
                print('Log: Connection error.')
            if self.check_login(resp) is not True:
                self.login()
                resp = self.session.post(url)
                self.check_login(resp)
            else:
                return resp
        else:
            resp = self.session.post(url, data)
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError:
                print('Log: Connection error.')
            if self.check_login(resp) is not True:
                self.login()
                resp = self.session.post(url, data)
                self.check_login(resp)
            else:
                return resp

    def update_session_cookies(self):
        if os.path.isfile(self.jar):
            with open(self.jar, 'wb') as jar:
                pickle.dump(self.session.cookies, jar)

    def load_session_cookies(self):
        if os.path.isfile(self.jar):
            with open(self.jar, 'rb') as jar:
                session_cookies = pickle.load(jar)
                self.session.cookies.update(session_cookies)

    def load_session_headers(self):
        with open(self.conf['PROGRAM-SETTINGS']['HEADERS'], 'r') as headers:
            session_headers = json.load(headers)
            self.session.headers.update(session_headers)

    def check_login(self, resp):
        for test in range(2):
            if 'Welcome, <a href="/userlookup.phtml?user={}">'.format(
                    self.username) not in resp.text:
                self.login()
            else:
                print('Log: Login check passed.')
                return True
                pass
        print('Log: Login check failed.')
        sys.exit(1)

    def login(self):
        '''Log-in to neopets.com'''
        url = 'http://www.neopets.com/login'
        resp = self.session_get(url)
        self.session.headers.update({'Referer': url})
        if self.check_login(resp) is not True:
            if os.path.isfile(self.jar) is not True:
                os.system('touch neopets.cookies')
                self.session_cookies = resp.cookies
                return self.session_cookies
            url = 'http://www.neopets.com/login.phtml'
            self.session_post(url, self.login_data)
            print('Login successful.')


def main():
    NeoSession()


if __name__ == '__main__':
    main()
