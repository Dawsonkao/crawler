from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
import os
import random

'''
待解決問題：
發文者時間：發文者時間有變動性（可能會顯示幾天內），需要抓取滑鼠移動到時間上才會顯示的時間
留言者時間：尚未確認問題
留言內容：定位方法需要修正，故結果並沒有留言內容
'''
username=""
password=""
path=""
#設定webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
options = Options()
options.add_argument("--headless")  # 啟用無頭模式
service = Service(path)
driver = webdriver.Firefox(service=service, options=options)



#啟動、登入、切換到欲爬蟲頁面
driver.get("https://www.facebook.com")
time.sleep(1)
elem = driver.find_element(By.ID,"email")
elem.send_keys(username)
time.sleep(1)
elem = driver.find_element(By.ID,"pass")
elem.send_keys(password)
time.sleep(1)
button = driver.find_element(By.NAME,'login')
button.click()
time.sleep(3)

driver.get('https://www.facebook.com/groups/443709852472133?locale=zh_TW')#目標網站
import time

# 滑動頁面，載入更多貼文
scroll_times = 30  #滑動字數

last_height = driver.execute_script("return document.body.scrollHeight")

for i in range(scroll_times):
    scroll_pause_time = random.randint(1,3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

    try:
        # 點擊查看更多按鈕
        more_button = driver.find_element(
            By.XPATH,
            './/div[@role="button" and contains(text(), "查看更多")]'
        )
        more_button.click()

        # 休眠
        import time
        time.sleep(scroll_pause_time)

    except Exception as e:
        # 如果找不到「查看更多」，就忽略（代表這篇本來就短）
        pass
    
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 取得網頁內容
result=pd.DataFrame()
soup = BeautifulSoup(driver.page_source, 'html.parser')
posts=soup.find_all('div',class_="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z")
name_class="html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs"
time_class="xmper1u xt0psk2 xjb2p0i x1qlqyl8 x15bjb6t x1n2onr6 x17ihmo5 x1g77sc7"

posts2 = driver.find_elements("xpath", "//div[@role='feed']//div[@data-ad-preview='message']")
for idx, post in enumerate(posts):
    try:
        #print(f"第 {idx+1} 篇：")
        
        # 找發文者
        try:
            author_name = post.find('span',class_=name_class).text
            #print("發文者名稱:", author_name)  # 加入調試輸出
        except Exception as e:
            #print("發文者名稱抓取失敗:", e)
            author_name = ""

        # 找發文時間
        try:
            timestamp = post.find('span',class_=time_class).text
        except:
            timestamp = ""
        # 找發文內容
        try:
            content = posts2[idx].text
        except:
            content = ""
               
        # 找留言
        comments = post.find_all('div', {'role': 'article'})  # 假設留言也是一個 article 結構（常見）
        for c_idx, comment in enumerate(comments):
            try:
                comment_author = comment.find('span', class_=name_class)
                comment_author_name = comment_author.text if comment_author else None
                    
                comment_content = comment.find('div', {'data-ad-preview': 'message'})
                comment_text = comment_content.text if comment_content else ""
                
                if comment_author_name=='作者':
                    comment_author_name=author_name
                """
                #測試用
                if comment_author !="":
                    print(f"留言 {c_idx+1}：")
                    print("留言者:", comment_author_name)
                    print("留言內容:", comment_text)
                    print("-"*30)
                """
            except Exception as e:
                print(f"第 {c_idx+1} 則留言解析失敗：", e)
        """
        #測試用
        print("類型: 主文")
        print("內容:", content)
        print("時間:", timestamp)
        print("發文者:", author_name)
        print("="*50)
        """
        #輸出
        post_dict={'類型':'主文','內容':content,'時間':timestamp,'發文者/留言者':author_name}
        post=pd.DataFrame([post_dict],index=[0])
        result=pd.concat([result,post])
        if comment_author != None:#留言者帳號不為空才輸出
            comm_dict={'類型':'留言','內容':comment_text,'時間':"",'發文者/留言者':comment_author_name}
            comm=pd.DataFrame([comm_dict],index=[0])
            result=pd.concat([result,comm])
    except Exception as e:
        print(f"第 {idx+1} 篇解析失敗：", e)

result.to_csv("result.csv",index=False)
driver.quit()
