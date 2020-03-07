import requests
from bs4 import BeautifulSoup as bs
import os
import urllib.request

class downloadBahaPostImage:
    def __init__(self):
        self.url = "https://forum.gamer.com.tw/"

        self.folder_path = ""              #main_folder名/文章標題名字
        self.soup = ""

        self.user_floor = 1
        self.maxPages = 1
        
        #User Setting:
        self.main_folder = "巴哈油圖"            #資料夾名稱，可自行設置，例：油圖
        self.bsn = "60076"                   #巴哈版，60076是場外休憩區
        self.post = "snA=4953068&tnum=1106"  #Copy巴哈文章最後字串，例如:snA=4953068&tnum=1106 或 snA=5516855&tnum=40 
        self.current_page = 1                #本程式默認從文章第1頁開始下載，若要由第10頁開始下載，可以將此數值設置為10
        self.max_download_page = 3           #由第1頁開始計算的話，下載至第3頁圖片，請設置為3　；　如果打算由第10頁下載至第30頁的話，請將此數值設置為30

        #Download Setting:
        self.isDownload = True               #True = 搜尋+下載       False = 只搜尋出結果不下載
        self.download_invalid_link = True     #建議設置為True，True=有可能會下載到死圖，但速度較快　；　False=不下載死圖，但有些網頁的圖片不能下載(如pixiv.cat)，不過速度較慢
        self.no_sub_floder = True            #預設為True，True=自動建立跟文章標題一樣的Folder ； False=不建立文章Folder(如設置為False，下面的sort_image請設置為False，不然圖片會被其他文章的新圖片覆蓋)
        self.sort_image = True               #預設為True，True=圖片名字會以[頁數、樓數、張數](Image1-1-1)另存檔案 ； False=圖片名稱會以[混亂英文字串]另存檔案

        #Other Setting:
        self.isFilterBp = True               #True = BP超過overBp值(預設是30)就不下載圖片  測試BP過濾的文章: snA=5189932&tnum=318
        self.overBp = 30                     #預設為30

        #其他問題: 文章名稱有特別字元導致出現ERROR:[檔案名稱、目錄名稱或磁碟區標籤語法錯誤] 例如: snA=5260865&tnum=16，這時候將no_sub_floder設置為False就可以

    def begin(self):
            url_target = "{}C.php?page={}&bsn={}&{}".format(self.url, self.current_page, self.bsn, self.post)
            request = requests.get(url_target)
            content = request.content
            self.soup = bs(content, "html.parser")

            self.search_maxPages()

    def search_maxPages(self):
        self.maxPages = int(self.soup.find("p", {"class": "BH-pagebtnA"}).select("a")[-1].text)
        print("此文章總共有{}頁".format(self.maxPages))

        self.search_topic_title()

    def search_topic_title(self):
        url_target = "{}C.php?page={}&bsn={}&{}".format(self.url, 1, self.bsn, self.post)
        request = requests.get(url_target)
        content = request.content
        soup = bs(content, "html.parser")

        topic_title = soup.find("h1", {"class": "c-post__header__title"}).text
        print("文章標題為{}".format(topic_title))

        if self.no_sub_floder == True:
            self.folder_path = "{}/{}".format(self.main_folder, topic_title)
        else:
            self.folder_path = "{}/".format(self.main_folder)


    def createSoup(self):
        if self.max_download_page > self.maxPages:
            print("ERROR: 欲下載頁數(max_download_page)超出文章最大的頁數")
            print("請將max_download_page的數值調整至{}或以下".format(self.maxPages))
        else:
            if self.max_download_page < self.current_page:
                print("請將max_download_page的數值調整至{}或以上".format(self.current_page))
            for i in range (self.current_page-1, self.max_download_page):        
                self.current_page = i+1
                url_target ="{}C.php?page={}&bsn={}&{}".format(self.url, self.current_page, self.bsn, self.post)
                request = requests.get(url_target)
                content = request.content
                self.soup = bs(content, "html.parser")
                print("\n第{}頁文章搜尋成功，開始分析中".format(self.current_page))

                self.search_userInfo()

                if self.isDownload == True:
                    print("\n第{}頁文章的圖片下載完成".format(self.current_page))
                else:
                    print("\n第{}頁文章的圖片搜尋完成".format(self.current_page))

                print("----------------------------")
    
    def search_userInfo(self):
        post = self.soup.find_all("div", {"class": "c-section__main c-post"})   #普通文章:c-section__main c-post 精華文章:c-section__main c-post c-post--feature
        
        images_counter = self.soup.select(".photoswipe-image")
        print("此頁文章總共搜尋到{}張圖片".format(len(images_counter)))
        
        for user in post:
            userInfo = user.select(".c-post__header__author")
            self.user_floor = userInfo[0].select("a")[0].get("data-floor")
            user_name = userInfo[0].select("a")[1].text
            user_id = userInfo[0].select("a")[2].text

            userCount = user.select(".postcount")
            user_getGp = userCount[0].select("span")[1].text
            user_getBp = userCount[0].select("span")[-1].text

            print("\n第{}頁 - {}樓發文者的名稱: {} ID: {}".format(self.current_page, self.user_floor, user_name, user_id), end=" ")
            print("GP數:{} BP數:{}".format(user_getGp, user_getBp))

            user_images = user.select(".photoswipe-image")    
            print("第{}頁 - {}樓發文者的圖片數量: {}".format(self.current_page, self.user_floor, len(user_images)))

            if self.isFilterBp == True and user_getBp != "-" and user_getBp != "X":
                if int(user_getBp) >= self.overBp:
                    if self.isDownload == True:
                        print("由於此樓BP數超過30，無視此樓：不下載此樓的圖片!")
                    else:
                        print("由於此樓BP數超過30，無視此樓：不搜尋此樓的圖片!")
            else:
                self.search_images(user_images)

    def search_images(self, user_images):
        for images_no, images in enumerate(user_images):
            image_url = images.get("href")
        
            if self.isDownload == False:
                print("成功搜尋第{}樓 - 第{}張圖片: {}".format(self.user_floor, images_no+1, image_url))
            else:
                print("正在下載第{}樓 - 第{}張圖片: {}".format(self.user_floor, images_no+1, image_url))
                self.download_jpg(image_url, images_no+1)       

    def download_jpg(self, image_url, images_no):

        if self.sort_image == True:
            images_name = "Image{}-{}-{}.jpg".format(self.current_page, self.user_floor, images_no)   #將圖片名字改成[頁數、樓數、張數]排序
        else:
            images_name = image_url.split('/')[-1] #不改圖片名字


        download_path = "{}/{}".format(self.folder_path, images_name)
        #download_path = "自定義名字/{}".format(images_name)

        image = requests.get(image_url)

        if (os.path.exists(self.folder_path) == False):
            os.makedirs(self.folder_path)
        
        try:
            if (self.download_invalid_link == False):
                urllib.request.urlretrieve(image_url, download_path)
            else:
                with open(download_path, "wb") as file:
                    file.write(image.content)
                    file.flush()
        except Exception:
            print("第{}樓的第{}張圖片下載失敗，跳過至下一張".format(self.user_floor, images_no))
            pass
        
if __name__ == "__main__":
    main = downloadBahaPostImage()
    main.begin()
    main.createSoup()