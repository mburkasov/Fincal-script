import time
import pandas as pd
import datetime
import pyscreenshot
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#Chrome setup
def chromesetup():
    chrome_options = webdriver.ChromeOptions();
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']);
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--user-data-dir=C:/User Data")
    chrome_options.add_argument("--profile-directory=Profile 2")
    chrome_options.add_argument("--load-extension=C:/Users/mikhail/AppData/Local/Google/Chrome/User Data/Profile 2/Extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm/1.24.4_1")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def agree(driver):
    try:
        driver.find_element_by_link_text('Согласен').click()
        time.sleep(1)
    except:
        pass

#opens option window
def open_option(code, driver, name, type):
    driver.get(f'https://www.moex.com/ru/contract.aspx?code={code}')
    agree(driver)
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'endOfDayDate')))
    screensave(name, type, code, screenshot())

#open and scroll main
def open_main(code, driver, name, all):
    driver.get(f'https://www.moex.com/ru/derivatives/optionsdesk.aspx?code={code}&sid=2&sby=1&c1=on&c2=on&c3=on&c4=on&c5=on&c6=on&c7=on&submit=submit')
    agree(driver)
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'table-scroller')))
    height = driver.execute_script("return document.body.scrollHeight")
    if (height>1500):   #approx your monitor height
        screensave(name, 'main', 'main', screenshot())
    #burns
    all = sickburn(driver, all, name)

    if (all != []):
        fc = all[0]
        lp = all[len(all)-1]
        #call
        element = driver.find_element_by_xpath(f'//a[text()[contains(.,"{fc}")]]')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        screensave(name, 'main', 'main_call', screenshot())
        #put
        if (fc!=lp):
            element = driver.find_element_by_xpath(f'//a[text()[contains(.,"{lp}")]]')
            driver.execute_script("arguments[0].scrollIntoView();", element)
            screensave(name, 'main', 'main_put', screenshot())
    #in case no options left
    else:
        element = driver.find_element_by_xpath(f'//table//a[1]')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        screensave(name, 'main', 'main_call', screenshot())
        #put
        element = driver.find_element_by_xpath(f'//table//a[last()]')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        screensave(name, 'main', 'main_put', screenshot())

def sickburn(driver, all, name):
    new = all[:]
    for code in all:
        try:
            driver.find_element_by_xpath(f'//a[text()[contains(.,"{code}")]]')
        except:
            print('Sorry,',name,', but',code,'has burnt')
            new.remove(code)
            continue
    return new

#saves screenshot with given name
def screensave(name,type,code,im):
    date = datetime.datetime.now()-datetime.timedelta(hours=7)
    date = date.strftime("%m.%d.")
    if (type=='main'):
        Path(f'./screenshots/{name}').mkdir(parents=True, exist_ok=True)
        im.save(f'./screenshots/{name}/{date}-{code}.png')
    else:
        Path(f'./screenshots/{name}/{type}/{code}').mkdir(parents=True, exist_ok=True)
        im.save(f'./screenshots/{name}/{type}/{code}/{date}-{code}.png')

def screenshot():
    im = pyscreenshot.grab()
    return im

#main
driver = chromesetup()
prev_name = ''
db = pd.read_csv('db.csv', header=None, encoding = 'utf8', delimiter=';', names=['name','type','code'])
for index, row in db.iterrows():
    if (row['name']!=prev_name):
        all = []
        prev_name = row['name']
    if (row['type']=='main'):
        open_main(row['code'], driver, row['name'], all)
    else:
        all.append(row['code'])
        open_option(row['code'], driver, row['name'], row['type'])

driver.quit()
