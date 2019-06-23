## 프로젝트 기간
## 참여인원
 
import os
os.chdir(r'C:\Github\Project_Social_Bigdata_Assignment')
#%% 모듈 및 사용자 함수.
# 모듈

from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import pandas  as pd
import pickle
import urllib.request
import urllib.parse
from dateutil.parser import parse
import matplotlib.pyplot as plt
from selenium import webdriver

plt.rcParams["font.family"] = 'NanumGothic'

def codeClear(bill_codes):
    for i,ele in enumerate(bill_codes):
        bill_code = ele.find('a')['href']
        m = re.search("javascript:fGoDetail\('(.*?)', 'billSimpleSearch'\)", bill_code)
        bill_code = m.group(1)
        bill_codes[i] = bill_code
    return bill_codes 


#%% (1) 데이터 수집
# 모든 법률 코드 리스트

# 1단계: 의안법호, 제안일자, 법률코드 크롤링 raw1
driver = webdriver.Chrome('C:/Users/dongkeon/Documents/chromedriver')

driver.get('http://likms.assembly.go.kr/bill/BillSearchResult.do')
driver.find_element_by_xpath("//select/option[@value='법률안']").click()
driver.find_element_by_xpath("//select/option[@value='의원']").click()
driver.find_element_by_xpath("//select/option[@value='공동발의']").click()
driver.find_element_by_xpath('//*[@id="srchForm"]/div/div[6]/button[1]').click()
driver.find_element_by_xpath("//select/option[@value='100']").click()

bill_num =[]
bill_date = []
bill_codes = []
for i in tqdm(range(1,30)):
    driver.find_element_by_css_selector("a[href*='javascript:GoPage("+str(i)+")']").click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    bill_codes_sub = soup.findAll("div", {"class": "pl25"})
    bill_num_sub = soup.select('body > div > div.contentWrap > div.subContents > div > div.tableCol01 > table > tbody > tr > td:nth-of-type(1)') 
    bill_date_sub = soup.select('body > div > div.contentWrap > div.subContents > div > div.tableCol01 > table > tbody > tr > td:nth-of-type(4)') 
    bill_codes.extend(bill_codes_sub)
    bill_num.extend(bill_num_sub)
    bill_date.extend(bill_date_sub)

# 데이터 클렌징.

for i in range(len(bill_num)):
    bill_num[i] = bill_num[i].text
    bill_date[i] = bill_date[i].text        
    
bill_codes = codeClear(bill_codes)

df = pd.DataFrame({'num':bill_num,'date':bill_date,'code':bill_codes})

# save
with open('Data/raw1.pickle', 'wb') as f:
    pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)
    
# 2단계 의원 리스트 가져오기. raw2
with open('Data/raw1.pickle', 'rb') as f:
    raw1 = pickle.load(f)

members = []

for i in tqdm(raw1.code):    
    with urllib.request.urlopen('http://likms.assembly.go.kr/bill/coactorListPopup.do?billId='+i) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        each_members = soup.select('#periodDiv > div.layerInScroll.coaTxtScroll > div > a')
        each_members = list(map(lambda x: x.text, each_members))                                
        members.append(each_members)


# 중간저장. # 오래걸리는 데이터는 원본으로 고유한 이름을 두고 그대로 두자...
with open('Data/members.pickle', 'wb') as f:
    pickle.dump(members, f, pickle.HIGHEST_PROTOCOL)


# 데이터 클렌징
raw2 = pd.DataFrame({'code':raw1.code,'date':raw1.date,'members':members})


raw2.date =  list(map(lambda x: parse(x), raw2.date))

p = re.compile('[^(/)]+')

for i in tqdm(raw2.members):
        for idxj,j in enumerate(i):
            tmp = p.findall(j)
            i[idxj] = tmp

#최종저장
with open('Data/raw2.pickle', 'wb') as f:
    pickle.dump(raw2, f, pickle.HIGHEST_PROTOCOL)

#%% 국회의원 현황 자료. 
status = open("Data\현황.txt", "r")

status = [ x[0:3] for x in status]
status = [ x.replace(' ','') for x in status]

delete_list = ['김경수','김종인','문미옥','박남춘','양승조','자유한','권석창','김종태','박찬우',
               '배덕광','이군현','이완영','이우현','이철우','바른미','송기석','안철수','오세정','최명길',
               '민주평','박준영','정의당','노회찬','윤종오','민중당','대한애','무소속']

for i in delete_list:
    status.remove(i)
    
with open('Data/remove_list.pickle', 'wb') as f:
    pickle.dump(delete_list, f, pickle.HIGHEST_PROTOCOL)
    
#%% 현황 자료 상세.
url = 'http://apis.data.go.kr/9710000/NationalAssemblyInfoService/getMemberCurrStateList?serviceKey=SiQ0MWpF2K6paqhGzxa9lCZTHTetbIDf0FqmxLIhcFq0o47AWRji1dUAGIA69pl34sOq0cbW5T18KE%2F9D9Wzeg%3D%3D&numOfRows=298&pageNo=1'
with urllib.request.urlopen(url) as response:
    html = response.read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')


hangle_name = list(map(lambda x: x.text, soup.find_all('empnm')))   
hanja_name = list(map(lambda x: x.text, soup.find_all('hjnm')))   
regin = list(map(lambda x: x.text, soup.find_all('orignm')))   
regin1 =  list(map(lambda x: x[0:2], regin))   
re_elect = list(map(lambda x: x.text, soup.find_all('reelegbnnm')))   

Status = pd.DataFrame({'name':hangle_name, 'hanja':hanja_name,'region':regin1,'region_sep':regin,'re_elect':re_elect})
with open('Data/Status.pickle', 'wb') as f:
    pickle.dump(Status, f, pickle.HIGHEST_PROTOCOL)
    
#%% 고향, 나이, 학교 상세.
    
hangle_name

driver = webdriver.Chrome('C:/Users/dongkeon/Documents/chromedriver')


status2 = []

for i in tqdm(hangle_name):
    driver.get('https://people.search.naver.com/search.naver?sm=tab_hty&where=nexearch&query=&ie=utf8&x=0&y=0')
    driver.find_element_by_xpath("//*[@id='nx_query']").send_keys('')
    driver.find_element_by_xpath("//*[@id='nx_query']").send_keys('국회의원 '+i)
    driver.find_element_by_xpath("//*[@id='search_form']/fieldset/input").click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    count_sub = soup.select('#content > div > h2 > em ')
    driver.find_element_by_xpath("//*[@id='content']/div/div[2]/div[2]/div/div/div/div/a/strong").click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    age_sub = soup.select('div > div.profile_wrap > div.profile_dsc > dl.who > dd.dft > span ')
    birth_sub = soup.select('#content > div > div.profile_wrap > div.profile_dsc > dl.dsc > dd:nth-child(2)')
    school_sub = soup.select('#content > div > div.record_wrap > div:nth-child(4) > dl')
    
    status2.append([i,count_sub,age_sub,birth_sub,school_sub])
                   
    
name = [x[0] for x in status2]               
count = [int(x[1][0].text) for x in status2]     
birth = [x[3][0].text for x in status2]             

age = []
school = []
for i in status2:
    try:
        age_sub = i[2][0].text       
        age.append(age_sub)
    except:
        age.append(None)
    try:
        school_sub = i[4][0].text
        school.append(school_sub)
    except:
        school.append(None)
        
status2 = pd.DataFrame({'name':name,'hanja':hanja_name,'count':count,'age':age,'birth':birth,'school':school,})


## 동명이인 문제 몇개 안되니까 수작업으로 해결!!
    
## 최종저장.
with open('Data/status2.pickle', 'wb') as f:
    pickle.dump(status2, f, pickle.HIGHEST_PROTOCOL)        


    