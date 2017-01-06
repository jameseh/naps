#!/usr/bin/env python3
'''
Auto trainer for the ninja training school.

Part of naps (neopets automation program suite)
'''


import re
from NeoSession import NeoSession
from ShopWizard import ShopWizard


class NinjaTrain(NeoSession):
    pet = NeoSession.conf['USER-SETTINGS']['PET-NAME']

    def __init__(self):
        resp = self.parse_status()
        self.course_type = self.determine_course(resp)
        self.run(resp)
        #self.check_buy_codestone()

    def check_inventory(self):
        url = 'http://www.neopets.com/island/fight_training.phtml?type=status'
        resp = self.get(url)
        codestone = re.search(r'(.+ codestone)', resp.text).group(1)
        url = 'http://www.neopets.com/inventory.phtml'
        resp = self.get(url)
        #if codestone not in resp.text:
            #ShowWizard.buy_item(codestone)

    def parse_status(self):
        url = 'http://www.neopets.com/island/fight_training.phtml?type=status'
        resp = self.get(url)
        return resp

    def determine_course(self, resp):
        level = int(re.search(r'(Lvl : <font color=green><b>)(\d*)', resp.text).group(2))
        strength = int(re.search(r'(Str : <b>)(\d*)', resp.text).group(2))
        defence = int(re.search(r'(Def : <b>)(\d*)', resp.text).group(2))
        hp = int(re.search(r'(Hp  : <b>)(\d*) / (\d*)</b>', resp.text).group(3))
        if hp < (level * 2) - 20:
            course_type = 'Endurance'
            return course_type
        else:
            if strength and defence < (level * 2) - 20:
                if strength < defence:
                    course_type = 'Strength'
                    return course_type
                else:
                    course_type = 'Defence'
                    return course_type
            else:
                course_type = 'Level'
                return course_type

    def run(self, resp):
        if 'Time till course finishes' in resp.text:
            print('Log: Already in course.')
        elif 'This course has not been paid' in resp.text:
            self.make_payment()
            print('Log: Course has not been paid.')
        elif 'Course Finished!' in resp.text:
            self.complete_course()
            print('Log: Course finished!')
            self.train_pet()
            self.make_payment()
            print('Log: {} is training {}.'.format(self.pet, self.course_type))
        else:
            self.train_pet()
            self.make_payment()
            print('Log: {} is training {}.'.format(self.pet, self.course_type))

    def train_pet(self):
        url = 'http://www.neopets.com/island/process_fight_training.phtml'
        self.post(url, data={'type': 'start', 'course_type': self.course_type, 'pet_name': self.pet})

    def make_payment(self):
        url = 'http://www.neopets.com/island/process_fight_training.phtml?type=pay&' \
              'pet_name={}'.format(self.pet)
        resp = self.get(url)
        if 'Time till course finishes :' in resp.text:
            return True

    def complete_course(self):
        url = 'http://www.neopets.com/island/process_fight_training.phtml'
        self.post(url, data={'type': 'complete', 'pet_name': self.pet})


def main():
    NeoSession()
    NinjaTrain()


if __name__ == '__main__':
    main()
