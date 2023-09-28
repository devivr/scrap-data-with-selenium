from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import datetime
import csv 
import scrapy
import shutil
import requests
from scrapy.http import TextResponse
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
import os
import re


class ScrapBingJobs():
    def __init__(self,param):
        self.param=param
        try:
            shutil.rmtree('./local_folder')
            print("removing old filestore")
        except OSError:
            pass
        time.sleep(0.5)
        try:
            os.makedirs('./local_folder')
            print("making new filestore")
        except OSError:
            pass

    def content_bing(self,param):
        self.param=param
        browser = webdriver.Firefox()
        browser.get('https://www.bing.com/jobs')
        time.sleep(1)
        search = browser.find_elements("xpath",'//*[@id="sb_form_q"]')
        search[0].send_keys(self.param)
        sech=browser.find_elements("xpath",'//*[@id="sb_form_go"]')
        sech[0].click()
        print(browser.current_url)
        time.sleep(1)
        print("Search Successful")
        sech1=browser.find_elements("xpath",'//div[@class="jb_card_img"]')
        sech1[0].click()
        actions = ActionChains(browser)
        for _ in range(8):
            actions.send_keys(Keys.SPACE).perform()
            time.sleep(2)
            cname=browser.find_element("xpath",'//div[@class="jb_l2_cardlist"]')
            #print(cname.text)
        textr = browser.page_source
        sech1=browser.find_elements("xpath",'//div[@class="jb_l2_cardlist"]/div')
        print(len(sech1))
        description=[]
        applyurl=[]
        duration=[]
        for i in range(len(sech1)):
            sech1[i].click()
            textr = browser.page_source
            response=Selector(text=textr)
            description.append(response.xpath("//div[@class='jbpnl_desc jb_short']//text()").getall())
            applyurl.append(response.xpath("//div[@class='jb_applyBtnContainer']//@href").getall())
            duration.append(response.xpath("//div[@class='jbpnl_desc jb_long']//p[2]").getall())
            time.sleep(0.5)  
        browser.close()
        return textr,description,applyurl,duration
    
    def get_data(self,param):
            self.param=param
            textr,description,applyurl,duration=self.content_bing(param)
            s = Selector(text=textr)         
            response=s
            searchword=[]
            company_name=response.xpath("//div[@class='jb_l2_cardlist']//@data-company").getall()
            job_title=response.xpath("//div[@class='jb_l2_cardlist']//@data-stdtitle").getall()
            posted_date=response.xpath("//div[@class='b_footnote jb_postedDate']/text()").getall()
            location=response.xpath("//li//div[@class='jbovrly_lj b_snippet']/text()").getall()
            img_url=response.xpath("//div[@class='cico']//@src").getall()
            for i in range(len(img_url)):
                img_url[i]='https://www.bing.com/'+img_url[i]+'.jpg'
                page = requests.get(img_url[i])
                f_ext = '.jpg'
                f_name = 'img'+company_name[i]+'{}'.format(f_ext)
                with open("local_folder/"+f_name, 'wb') as f:
                    f.write(page.content)
                searchword.append(param)
            A=[self.splitting(i) for i in location]
            df=pd.DataFrame(A)
            location1=df[0]
            type_job=df[1]
            salary_list=[]
            pattern = r'\₹\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            for i in range(len(description)):
                salary_list.append(re.findall(pattern, description[i]))
    
            
            data=list(zip(company_name,job_title,posted_date,location1,type_job,img_url,searchword,applyurl,salary_list,duration,description))
            
            return data
    def splitting(self,str1):
            self.str1=str1
            str12=[]
            index = self.str1.find('·') 
            if index!=-1:
                str1_spit=self.str1.split('·')
                str11=str1_spit[0]
                str12=str1_spit[1]
            else:
                str11=self.str1
            return str11,str12
    def create_table(self,param):
            self.param=param
            data=self.get_data(param)            
            column=['company_name','job_title','posted date','location','type_job','logoimage_url','searchword','applyurl','Salary','duration','description']
            job_table=pd.DataFrame(data,columns=column)
            return job_table
    def final_table(self,parameter):
        self.parameter=parameter
        Dictionary = {}
        for i in range(len(parameter)):        
            Dictionary[i]=self.create_table(parameter[i])
        newtable=pd.concat([Dictionary[i] for i in range(len(parameter))], ignore_index=True)
        return newtable
    
     

    
          
parameter=['data scientist']#,'AI','HR','java developer','python developer']


time1=datetime.datetime.now().strftime("%H_%M_%S")
filename=parameter[0].replace(" ","")+time1+'.csv'
search=ScrapBingJobs(parameter)
newtable=search.final_table(parameter)
newtable.to_csv(filename)
    

print('scroll successfully')

  
