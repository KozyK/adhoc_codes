#!/usr/bin/python
# -*- Coding: utf-8 -*-
# Coded by: Koji KITANO
# EMAIL: koji.kitano@outlook.com

import time
from selenium import webdriver
import chromedriver_binary

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options # オプションを使うために必要


def get_all_published_NB(published_years):
    """ 日経ビジネスのすべてのバックナンバーの情報を収集するスクリプト """

    backnumbers = []

    option = Options()                          # オプションを用意
    option.add_argument('--headless')           # ヘッドレスモードの設定を付与
    driver = webdriver.Chrome(options=option)

    for published_year in published_years:

        driver.get('https://business.nikkei.com/magazine/?year='+published_year)
        time.sleep(5)

        # 「もっと見る」をクリックする
        while not(driver.find_element_by_xpath('/html/body/div[1]/div/article/div/section/div[2]').get_attribute('style') == 'display: none;'):
            button_more = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/article/div/section/div[2]/a")))
            button_more.click()
            print('clicked')
            time.sleep(1)

        # すべてのバックナンバー情報を取得する
        magazine_list_items = driver.find_elements_by_xpath('/html/body/div[1]/div/article/div/section/div[1]/div')
        

        for magazine_list_item in magazine_list_items:
            backnumber = {'published': '', 'title': '', 'subtitle': '', 'url': '', 'img_url':''}
            backnumber['published'] = format_date(magazine_list_item.find_element_by_xpath('a/h3').text) # 「**年**月**日号」を取得
            backnumber['title'] = magazine_list_item.find_element_by_xpath('a/h3').text # 「**年**月**日号」を取得
            backnumber['subtitle'] = magazine_list_item.find_element_by_xpath('a/span').text # タイトルを取得
            backnumber['url'] = magazine_list_item.find_element_by_xpath('a').get_attribute('href')
            backnumber['img_url'] = magazine_list_item.find_element_by_xpath('a/img').get_attribute('src') # 画像のURLを取得

            backnumbers.append(backnumber)


        # 年を跨ぐ合併号は重複するため削除
        backnumbers_unique = []
        published_unique = []
        for backnumber in backnumbers:
            
            if not backnumber['published'] in published_unique:
                published_unique.append(backnumber['published'])
                backnumbers_unique.append(backnumber)

    driver.quit()

    return backnumbers_unique

def format_date(date_text):
    year = date_text.split('年')[0]
    month = date_text.split('年')[1].split('月')[0]
    day =  date_text.split('年')[1].split('月')[1].split('日')[0].split('・')[0]   
    return '{0:0>4}-{1:0>2}-{2:0>2}'.format(year,month,day)


if __name__ == '__main__':
    import os
    import csv
    import requests

    published_years = [
        '2011',
        '2012',
        '2013',
        '2014',
        '2015',
        '2016',
        '2017',
        '2018',
        '2019',
        '2020'
    ]

    backnumbers = get_all_published_NB(published_years)

    print('scraping finished')

    with open(os.path.dirname(os.path.abspath(__file__))+'/data/backnumber.csv', 'w', encoding='utf-8') as f:
        w = csv.DictWriter(f, backnumbers[0].keys())
        for backnumber in backnumbers:
            w.writerow(backnumber)
    
    print('saving csv finished')

    for backnumber in backnumbers:
        try:
            response = requests.get(backnumber['img_url'])
            response.raise_for_status()
            with open(os.path.dirname(os.path.abspath(__file__))+'/data/'+backnumber['published']+'.jpg', 'wb') as f:
                f.write(response.content)
    
        except:
            print('failed')
        
    print('saving images finished')


