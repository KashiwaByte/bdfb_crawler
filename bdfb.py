import base64,json,os,random,re,time,requests
from urllib.parse import urljoin
import cv2
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from fake_useragent import UserAgent
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import pprint
import ddddocr


def init_driver():
    """
    初始化驱动

    :return: driver
    """
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-service-autorun')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--password-store=basic')
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('user-agent=%s' % UserAgent().random)
    chrome_options.add_argument('user-agent=%s' % "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0")
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    #chrome_options.add_argument('--headless')
    # 请求头生效
    #dep = r"C:\Users\wangt\Downloads\chromedriver-win64\chromedriver.exe"
    dep = r"C:\Users\47131\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    driver = uc.Chrome(driver_executable_path=dep,options=chrome_options)
    driver.maximize_window()
    # driver.set_window_size(1024,768)

    # driver.find_element(By.ID, "#code").send_keys("网络犯罪")
    # driver.switch_to.window(driver.window_handles[1].)
    

    return driver

def captcha(url, html):
    """
    图片验证码识别

    :param url: 根地址
    :param html: 网页源码
    :return: 识别结果
    """

    def get_pic(url, html):
        """
        获取图片

        :param url: 根网址
        :param html: 网页源码
        :return:
        """

        soup = BeautifulSoup(html, 'lxml')
        pic_url_t = soup.find('img', align='absmiddle').attrs['src']
        pic_url = urljoin(url, pic_url_t)
        # headers = {"user-agent": UserAgent().random}
        headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}
        pic = requests.get(pic_url,headers=headers)
        with open('./captcha.png', 'wb') as f:
            f.write(pic.content)

    def convert_binary(img, threshold):
        """
        图片二值化
        :param img: 图片
        :param threshold: 二值化阈值
        :return: 二值化图片
        """
        img = img.convert('L')
        pixele = img.load()
        # 二值字典
        t2val = {}
        for x in range(img.width):
            for y in range(img.height):
                if pixele[x, y] > threshold:
                    pixele[x, y] = 255
                    t2val[(x, y)] = 1
                else:
                    pixele[x, y] = 0
                    t2val[(x, y)] = 0
        # img.show()
        return img

    def clear_noise(img, n, z):
        """
        图片降噪

        :param img: 二值化的图片
        :param n: 降噪阈值 0-8
        :param z: 降噪次数
        :return: 降噪后的图片
        """
        pixele = img.load()
        for i in range(0, z):
            for x in range(1, img.size[0] - 1):
                for y in range(1, img.size[1] - 1):
                    neardots = 0
                    ll = pixele[x, y]
                    if ll == pixele[x - 1, y - 1]:
                        neardots += 1
                    if ll == pixele[x - 1, y]:
                        neardots += 1
                    if ll == pixele[x - 1, y + 1]:
                        neardots += 1
                    if ll == pixele[x, y - 1]:
                        neardots += 1
                    if ll == pixele[x, y + 1]:
                        neardots += 1
                    if ll == pixele[x + 1, y - 1]:
                        neardots += 1
                    if ll == pixele[x + 1, y]:
                        neardots += 1
                    if ll == pixele[x + 1, y + 1]:
                        neardots += 1

                    if neardots < n:
                        pixele[x, y] = 255
        return img

    get_pic(url, html)
    img_1 = convert_binary(Image.open('./captcha.png'), 150)
    img_2 = clear_noise(img_1, 4, 1)
    img_2.show()
    result = pytesseract.image_to_string(img_2)
    print(result)
    return result

def recognize():
    ocr = ddddocr.DdddOcr()
    with open(r".\img.jpg", 'rb') as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)
    print(res)
    return res

def to_bdfb(driver,entrance=11):
    """
    跳转北大法宝页面

    :param driver: 驱动
    :return: 驱动
    """
    key = '072508574177'
    pwd = '392573'
    user_name = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.ID, 'user_name'))
    user_name.click()
    user_name.send_keys(key)  # 用户名
    password = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.ID, 'password'))
    password.click()
    password.send_keys(pwd)  # 密码
    screenshot = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.CSS_SELECTOR, "#form1 > p:nth-child(6) > img"))
    screenshot.screenshot(r".\img.jpg") 
    code = recognize()
    code_input = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.ID, "code"))
    code_input.send_keys(code)
    ok = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.ID, "ok"))
    ok.click()
    
    '''
    while True:
        try:
            denglu = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.XPATH, '//*[@id="main"]/div[1]/div[1]/div[2]/div/div/font/b')) 
            if key in denglu.text:
                zylb = WebDriverWait(driver, 10, 0.5).until(
                    lambda x: x.find_element(By.XPATH, '//*[@id="menu_2"]/a')) 
                zylb.click()
                break
        except:
            pass
    
    while True:
        if 'classid=61' in driver.current_url:
            flsjk = WebDriverWait(driver, 10, 0.5).until(
                lambda x: x.find_element(By.XPATH, '//*[@id="faqmenu"]/li[3]/a'))
            flsjk.click()
            break
    while True:
        if 'classid=64' in driver.current_url:
            bdfb1 = WebDriverWait(driver, 10, 0.5).until(
                lambda x: x.find_element(By.XPATH, '//*[@id="broadcast"]/div/div[2]/a[1]'))
            bdfb1.click()
            break
    while True:
        if 'classid=73' in driver.current_url:
            bdfb2 = WebDriverWait(driver, 10, 0.5).until(
                lambda x: x.find_element(By.XPATH, f'//*[@id="broadcast"]/div[2]/div[2]/a[{entrance}]'))
            bdfb2.click()
            time.sleep(2)
            all_window = driver.window_handles
            if len(all_window) > 1:
                driver.switch_to.window(all_window[1])
                time.sleep(1)
                driver.close()
                driver.switch_to.window(all_window[0])
                bdfb2 = WebDriverWait(driver, 10, 0.5).until(
                lambda x: x.find_element(By.XPATH, f'//*[@id="broadcast"]/div[2]/div[2]/a[{entrance}]'))
                bdfb2.click()
            break
    '''
    time.sleep(50)
    print("开始采集")
    all_window = driver.window_handles
    if len(all_window) > 1:
        driver.switch_to.window(all_window[1])
        time.sleep(1)
  
    # while True:
    #     all_window = driver.window_handles
    #     if len(all_window) > 1:
    #         driver.switch_to.window(all_window[1])
    #         time.sleep(15)
    #         # grad = WebDriverWait(driver, 10, 0.5,ignored_exceptions=True).until(lambda x: x.find_element(By.CSS_SELECTOR, "#upgradeul+div>a"))
    #         # grad.click() 
    #         break
    
    return driver

def to_datalist_page(driver,search_key,del_search_key,keyword="谣言"):
    """
    北大法宝页面筛选数据

    :param driver: 驱动
    :return: 驱动
    """
    # driver = uc.Chrome()
    while True:
        try:
            script = f'''
                document.querySelector('body > div.column-search > div > div.search-rect > div.search-wrap > div.search-panel > div.areajSelect > ul > li:nth-child(1)').setAttribute('class','');
                document.querySelector('body > div.column-search > div > div.search-rect > div.search-wrap > div.search-panel > div.areajSelect > ul > li:nth-child(2)').setAttribute('class','current');
                document.querySelector('#txtSearch').value='{keyword}';
                document.querySelector('#btnSearch').click();
            '''
            driver.execute_script(script)
            time.sleep(5)
            script = '''
                document.querySelector('#rightContent > div.grid-right > div:nth-child(1) > div.list-tool-wrap > div.filtrater-box > div:nth-child(2)').classList.add('current');
                document.querySelector('#recordgroup > dl > dd:nth-child(3)').click();
            '''
            driver.execute_script(script)
            # time.sleep(0)
            # timeliness_dicport = WebDriverWait(driver, 10, 0.5).until(lambda x:x.find_elements(By.CSS_SELECTOR, '#leftContent > div > div:nth-child(9) > div > ul'))
            # for i,td in enumerate(timeliness_dicport):
            #     print(f'#TimelinessDicport_{i+1}_span')
            #     tld = td.find_element(By.CSS_SELECTOR, f'#TimelinessDicport_{i+1}_span')
            #     txt = str(tld.text).split(" ")[0]
            #     print(search_key)
            #     if txt in search_key:
            #         tld.click()
            #         del_search_key.append(txt)
            #         search_key.remove(txt)
            #         break
            
            # txtSearch = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.ID, 'txtSearch'))
            # txtSearch.send_keys(keyword)
            # btnSearch = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.ID, 'btnSearch'))
            # btnSearch.click()
        except Exception as e:
            print(e)
            # raise Exception('打开标题页面出错!')
            url_login = 'https://www.pkulaw.com/'
            driver.get(url_login)
            print(f"打开页面出错，稍后重新打开执行，请稍等...")
            time.sleep(5)
        else:
            # WebDriverWait(driver,60,0.5).until(lambda x: EC.presence_of_element_located((By.CSS_SELECTOR,"#menusResult > div > ul > li.current > a")))
            # # driver = uc.Chrome()
            # driver.execute_script('''

                

            # ''')
            time.sleep(3)
            break
            
    return driver

def parse_data(html):
    """
    数据解析，写入csv

    :param html: 网页源码
    """
    data = {}
    time.sleep(6)
    soup = BeautifulSoup(html, 'lxml')
    try:
        data['题目'] = soup.find('h2', class_='title').text.replace('\n', ' ').replace('English','').strip()
    except:
        data['题目'] = None
    try:
        items = soup.find('div', class_='fields').find('ul').find_all('li')
        for i in items:
            data[i.find('strong').text.split('：')[0]] = i.text.split('：')[1].replace('\n', ' ').strip()
    except:
        pass
    try:
        data['引用本法'] = ','.join([a.text for a in soup.find('div', id='div0').find_all('a')])
    except:
        data['引用本法'] = None
    try:
        data['正文'] = soup.find('div', id='divFullText').text.replace('\n', ' ').replace('\u3000', '').strip()
    except:
        data['正文'] = None
    try:
        lenovo = soup.find_all('div', class_='lenovo')
        for l in lenovo:
            jt = dict()
            blocks = l.find_all('div', class_='block')
            for b in blocks:
                jt[b.find('h5').text.replace('\n', '').strip()] = ','.join(
                    [i.text.replace('\n', '').strip() for i in b.find_all('li')])
            data[l.find('h4').text.replace('\n', '').strip()] = json.dumps(jt, ensure_ascii=False)
    except:
        pass
    try:
        data['本篇链接'] = driver.current_url if 'chl' in driver.current_url else None
    except:
        data['本篇链接'] = None
    data_t = dict()
    data_t['题目'] = data['题目'] if '题目' in data.keys() else None
    data_t['发布部门'] = data['发布部门'] if '发布部门' in data.keys() else None
    data_t['发文字号'] = data['发文字号'] if '发文字号' in data.keys() else None
    data_t['发布日期'] = data['发布日期'] if '发布日期' in data.keys() else None
    data_t['实施日期'] = data['实施日期'] if '实施日期' in data.keys() else None
    data_t['时效性'] = data['时效性'] if '时效性' in data.keys() else None
    data_t['效力级别'] = data['效力级别'] if '效力级别' in data.keys() else None
    data_t['法规类别'] = data['法规类别'] if '法规类别' in data.keys() else None
    data_t['专题分类'] = data['专题分类'] if '专题分类' in data.keys() else None
    data_t['引用本法'] = data['引用本法'] if '引用本法' in data.keys() else None
    data_t['正文'] = data['正文'] if '正文' in data.keys() else None
    data_t['背景资料'] = data['背景资料'] if '背景资料' in data.keys() else None
    data_t['本篇引用的法规'] = data['本篇引用的法规'] if '本篇引用的法规' in data.keys() else None
    data_t['引用本篇的法规 案例 论文'] = data['引用本篇的法规 案例 论文'] if '引用本篇的法规 案例 论文' in data.keys() else None
    data_t['本篇链接'] = data['本篇链接'] if '本篇链接' in data.keys() else None
    data_df = pd.DataFrame([data_t])
    print(data_df)
    # 判断是否需要加表头
    if not os.path.exists(f'./BDFBData.csv'):
        data_df.to_csv(f'./BDFBData.csv', mode='a', index=False)
    else:
        data_df.to_csv(f'./BDFBData.csv', mode='a', index=False, header=None)

def simulateDragX(driver, source, targetOffsetX):
    """
    模仿人的拖拽动作：快速沿着X轴拖动（存在误差），再暂停，然后修正误差
    防止被检测为机器人，出现“图片被怪物吃掉了”等验证失败的情况

    :param source:要拖拽的html元素
    :param targetOffsetX: 拖拽目标x轴距离
    :return: None
    """
    action_chains = ActionChains(driver)
    # 点击，准备拖拽
    action_chains.click_and_hold(source)
    # 拖动次数，二到三次
    dragCount = random.randint(2, 3)
    if dragCount == 2:
        # 总误差值
        sumOffsetx = random.randint(-10, 10)
        action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
        # 暂停一会
        action_chains.pause(0.5)
        # 修正误差，防止被检测为机器人，出现图片被怪物吃掉了等验证失败的情况
        action_chains.move_by_offset(-sumOffsetx, 0)
    elif dragCount == 3:
        # 总误差值
        sumOffsetx = random.randint(-10, 10)
        action_chains.move_by_offset(targetOffsetX + sumOffsetx, 0)
        # 暂停一会
        action_chains.pause(0.5)
        # 已修正误差的和
        fixedOffsetX = 0
        # 第一次修正误差
        if sumOffsetx < 0:
            offsetx = random.randint(sumOffsetx, 0)
        else:
            offsetx = random.randint(0, sumOffsetx)

        fixedOffsetX = fixedOffsetX + offsetx
        action_chains.move_by_offset(-offsetx, 0)
        action_chains.pause(0.5)

        # 最后一次修正误差
        action_chains.move_by_offset(-sumOffsetx + fixedOffsetX, 0)
        action_chains.pause(0.5)

    action_chains.release().perform()

def start_drag(driver, distance):
    """
    滑块验证码突破

    :param driver: 驱动
    :param distance: 缺口距离
    :return: None
    """
    time.sleep(3)
    slider = WebDriverWait(driver, 30, 0.5).until(lambda x: x.find_element(By.XPATH,'//*[@id="drag"]/div[3]'))
    simulateDragX(driver, slider, distance)

def mergy_Image(image_file, location_list):
    """
    将原始图片进行合成
    :param image_file: 图片文件
    :param location_list: 图片位置
    :return: 合成新的图片地址
    """
    # 存放上下部分的各个小块
    upper_half_list = []
    down_half_list = []
    location_list_upper = location_list[:10]
    location_list_down = location_list[10:]
    image = Image.open(image_file)
    # 通过 y 的位置来判断是上半部分还是下半部分,然后切割
    for location in location_list_upper:
        if location['y'] == -100:
            # 间距为10，y：
            if location['x'] <= -300:
                im = image.crop((abs(location['x']+300), 100, abs(location['x']+300)+30, 200))
            elif 300>= location['x']>0:
                im = image.crop((300-location['x'], 100, 300-location['x']+30, 200))
            else:
                im = image.crop((abs(location['x']), 100, abs(location['x'])+30, 200))
        elif location['y'] == 0:
            # 间距为10，y：0-50
            if location['x'] <= -300:
                im = image.crop((abs(location['x']+300), 0, abs(location['x']+300)+30 , 100))
            elif 300 >= location['x'] > 0:
                im = image.crop((300-location['x'], 0, 300-location['x']+30 , 100))
            else:
                im = image.crop((abs(location['x']), 0, abs(location['x'])+30 , 100))
        upper_half_list.append(im)

    for location in location_list_down:
        if location['y'] == -100:
            # 间距为10，y：
            if location['x'] <= -300:
                im = image.crop((abs(location['x']+300), 100, abs(location['x']+300)+30, 200))
            elif 300>= location['x']>0:
                im = image.crop((300-location['x'], 100, 300-location['x']+30, 200))
            else:
                im = image.crop((abs(location['x']), 100, abs(location['x'])+30, 200))
        elif location['y'] == 0:
            # 间距为10，y：0-50
            if location['x'] <= -300:
                im = image.crop((abs(location['x']+300), 0, abs(location['x']+300)+30 , 100))
            elif 300 >= location['x'] > 0:
                im = image.crop((300-location['x'], 0, 300-location['x']+30 , 100))
            else:
                im = image.crop((abs(location['x']), 0, abs(location['x'])+30 , 100))
        down_half_list.append(im)

    # 创建一张大小一样的图片
    new_image = Image.new('RGB', (300, 200))
    # 粘贴好上半部分 y坐标是从上到下（0-200）
    offset = 0
    for im in upper_half_list:
        #im.show()
        new_image.paste(im, (offset, 0))
        offset += 30
    # 粘贴好下半部分
    offset = 0
    for im in down_half_list:
        new_image.paste(im, (offset, 100))
        offset += 30
    new_image.save('./captcha.png')
    return './captcha.png'

def get_distance_b(bg_Image_path):
    """
    获取滑块验证码缺口距离
    :param bg_Image_path: 滑块背景图地址
    :return: 距离
    """
    # 读取文件
    img = cv2.imread(bg_Image_path)
    img1 = img.copy()
    # 将通道值小于150的转变为黑色
    for h in range(img.shape[0]):
        for w in range(img.shape[1]):
            if img[h, w, 0] < 120 and img[h, w, 1] < 120 and img[h, w, 2] < 120:
                for c in range(3):
                    img[h, w, c] = 0
            else:
                for c in range(3):
                    img[h, w, c] = 255
    canny_img = cv2.Canny(img, 0, 100)  # 边缘检测
    counts, _ = cv2.findContours(canny_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 轮廓检测
    dist_list = []
    for c in counts:
        x, y, w, h = cv2.boundingRect(c)
        #  去除较小先验框
        if w < 30:
            continue
        if h < 30:
            continue
        cv2.rectangle(img1, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # print(f"左上点的坐标为：{x, y}，右下点的坐标为{x + w, y + h}")
        dist_list.append(x)
    # cv2.imshow('123', img1)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    dist_dic = dict()
    for i in dist_list:
        dist_dic[i] = dist_list.count(i)
    sorted(dist_dic.items(), key=lambda x:x[1], reverse=False)
    dist = list(dist_dic.items())[0][0] if len(dist_list) != 0 else 0
    rate = list(dist_dic.items())[0][1]/len(dist_list) if len(dist_list) != 0 else 0
    print(f'滑块距离:{dist} 准确率:{rate}')
    return dist

def get_distance(bg_Image_path):
    """
    获取滑块验证码缺口距离

    :param bg_Image_path: 滑块背景图地址
    :return: 距离
    """

    # 读取文件
    bg_Image = Image.open(bg_Image_path)
    # 阈值
    threshold = 80
    high_min = 25
    for i in range(30, bg_Image.size[0]):
        count_y = []
        for j in range(bg_Image.size[1]):
            bg_pix = bg_Image.getpixel((i, j))
            bg_pix_pre = bg_Image.getpixel((i-1, j))
            if abs(sum(bg_pix)-sum(bg_pix_pre)) >=threshold:
                count_y.append(j)

        if len(count_y) >= high_min:
            print('滑块距离：',i)
            return i

def recognize_code(driver):
    """
    识别滑动验证码
    :param driver: selenium驱动
    :return:
    """
    while True:
        if 'drag_bg' in driver.page_source:
            bs = BeautifulSoup(driver.page_source, 'lxml')
            break
    # 找到背景图片和缺口图片的div
    bg_div = bs.find_all(class_='cut_bg')
    # 获取缺口背景图片url
    bg_url = re.findall('data:image/jpg;base64,(.*?)"', bg_div[-1].get('style'))[0]
    # 获取背景图片url
    img = base64.urlsafe_b64decode(bg_url + '=' * (4 - len(bg_url) % 4))
    with open("imageToSave.png", "wb") as fh:
        fh.write(img)
    # 存放每个合成缺口背景图片的位置
    bg_location_list = []
    # 存放每个合成背景图片的位置
    for bg in bg_div:
        location = {}
        location['x'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', bg.get('style'))[0][0])
        location['y'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', bg.get('style'))[0][1])
        bg_location_list.append(location)
    # 合成图片
    bg_Image_path = mergy_Image('./imageToSave.png', bg_location_list)
    # 计算缺口偏移距离
    distance = get_distance(bg_Image_path)
    distance = distance if distance is not None else 1
    # 移动滑块
    start_drag(driver, distance)
    time.sleep(2)
    if 'drag_bg' in driver.page_source:
        close = WebDriverWait(driver, 5, 0.5).until(lambda x:x.find_element(By.CLASS_NAME,'layui-layer-setwin')).find_element(By.TAG_NAME,'a')
        close.click()
        next_page = WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element(By.LINK_TEXT, '下一页'))
        next_page.click()
        time.sleep(2)
        recognize_code(driver)

def parse_data_content(html,title,icon):
    """
    数据解析，写入csv

    :param html: 网页源码
    """
    data = {}
    time.sleep(3)
    soup = BeautifulSoup(html, 'lxml')
    try:
        data['法律名称'] = title
    except:
        data['法律名称'] = None
    try:
        items = soup.find('div', class_='fields').find('ul').find_all('li')
        for i in items:
            data[i.find('strong').text.split('：')[0]] = i.text.split('：')[1].replace('\n', ' ').strip()
    except:
        pass
    try:
        data['全文内容'] = soup.find('div', id='divFullText').text.replace('\n', ' ').replace('\u3000', '').strip()
    except:
        data['全文内容'] = None
    try:
        data['本篇链接'] = driver.current_url if 'chl' in driver.current_url else None
    except:
        data['本篇链接'] = None
    data_t = dict()
    if data.get('时效性','') != "失效":
        fatiaos = []
        tiao_wrap = soup.find_all("div",attrs={"class":"tiao-wrap"})
        if icon and len(tiao_wrap)>0:
            # print(f"tiaowrap:{len(tiao_wrap)}")
            for tw in tiao_wrap:
                if "谣言" not in tw.text:
                    continue
                tiao_span = tw.find("div",attrs={"class","kuan-content"}).find("span")
                tiao = tiao_span.text
                tiao_span.decompose()
                item = tw.find_all("div",attrs={"class","xiang-wrap"})
                # print(f"tiao:{tiao}")
                # print(f"item{len(item)}")
                if len(item)<=0:
                    fatiao_name = f"{title.strip()}{tiao.strip()}"
                    # print(f"xw:--{fatiao_name}") 
                    fatiaos.append((fatiao_name,tw.text)) 
                for xw in item:
                    if "谣言" in xw.text:
                        fatiao_content = xw.text
                        match = re.findall("[（\(）\)一二三四五六七八九十0-9]+",xw.text)
                        fatiao_name = f"{title.strip()}{tiao.strip()}第{str(match[0]).strip()}项"
                        # print(f"xw:{match}--{fatiao_name}") 
                        fatiaos.append((fatiao_name,fatiao_content))
            dt = []
            # 2-15 16 18 20
            print(fatiaos)
            for f in fatiaos:
                data_t['法律名称'] = data['法律名称'] if '法律名称' in data.keys() else None
                data_t['制定机关'] = data['制定机关'] if '制定机关' in data.keys() else None
                data_t['发文字号'] = data['发文字号'] if '发文字号' in data.keys() else None
                data_t['发布日期'] = data['发布日期'] if '发布日期' in data.keys() else None
                data_t['实施日期'] = data['实施日期'] if '实施日期' in data.keys() else None
                data_t['时效性'] = data['时效性'] if '时效性' in data.keys() else None
                data_t['效力位阶'] = data['效力位阶'] if '效力位阶' in data.keys() else None
                data_t['法规类别'] = data['法规类别'] if '法规类别' in data.keys() else None
                data_t['法条名称'] = f[0]
                data_t['法条内容'] = f[1]
                data_t['全文内容'] = data['全文内容'] if '全文内容' in data.keys() else None
                print(f"------{data_t}")
                dt.append(data_t)
                # dt.append(data_t)
        else:
            data_t['法律名称'] = data['法律名称'] if '法律名称' in data.keys() else None
            data_t['制定机关'] = data['制定机关'] if '制定机关' in data.keys() else None
            data_t['发文字号'] = data['发文字号'] if '发文字号' in data.keys() else None
            data_t['公布日期'] = data['公布日期'] if '公布日期' in data.keys() else None
            data_t['施行日期'] = data['施行日期'] if '施行日期' in data.keys() else None
            data_t['时效性'] = data['时效性'] if '时效性' in data.keys() else None
            data_t['效力位阶'] = data['效力位阶'] if '效力位阶' in data.keys() else None
            data_t['法规类别'] = data['法规类别'] if '法规类别' in data.keys() else None
            data_t['法条名称'] = data['法律名称']
            data_t['法条内容'] = data['法条内容'] if '法条内容' in data.keys() else None
            data_t['全文内容'] = data['全文内容'] if '全文内容' in data.keys() else None
        if icon and len(tiao_wrap)>0:
            data_df = pd.DataFrame(dt)
            print(f"运行dt:--------------{len(dt)}")
        else:
            data_df = pd.DataFrame([data_t])
            print(f"运行data_t:---------------------{1}")
        # 判断是否需要加表头
        if not os.path.exists(f'./fabao_result1.csv'):
            data_df.to_csv(f'./fabao_result1.csv', mode='a', index=False)
        else:
            data_df.to_csv(f'./fabao_result.csv1', mode='a', index=False, header=None)


def to_sifaanli(driver,keyword):
    script = f"""
        document.querySelector('.nav-wrap > li:nth-child(2) > a:nth-child(1)').click();
        
        document.querySelector('.jSelectList > li:nth-child(1)').setAttribute('class','');
        document.querySelector('.jSelectList > li:nth-child(20)').setAttribute('class','current');
        
        document.querySelector('#txtSearch').value='{keyword}';
        document.querySelector('#btnSearch').click();
        
    """
    driver.execute_script(script)

if __name__ == '__main__':
        page_count = 1 # 统计采集页数
        skip_count = 41 # 跳过页数
        skip_tiao_count = 0 #当前页跳过条数
        keyword = "谣言" # 关键词
        entrance = 7 # 90图书馆 跳转接口元素selector 索引
        search_key = ["现行有效","已被修改","部分失效"]
        del_search_key = []
        url_login = 'http://www.90tsg.com/'  # 登录地址
        #url_login = 'https://www.pkulaw.com/'
        driver = init_driver()
        driver.get(url_login)
        driver = to_bdfb(driver,entrance)
        #to_sifaanli(driver,keyword)
        # result = captcha(url_login, driver.page_source)
        print("ok")
        # exit()
        # time.sleep(3)
       # driver = to_datalist_page(driver,search_key,del_search_key,keyword=keyword)
        time.sleep(1)
        # while True:
        #skip_page_count = WebDriverWait(driver, 10, 0.5).until(lambda x:x.find_element(By.CSS_SELECTOR,'.pagination > li:nth-child(14) > input:nth-child(1)'))
        #skip_page_count.send_keys(skip_count)
        #skc = WebDriverWait(driver, 10, 0.5).until(lambda x:x.find_element(By.CSS_SELECTOR,'.jumpBtn'))
        #skc.click()
        #page_count =skip_count
        #page_count = 
        time.sleep(1)
        while True:
            while True:
                try:
                    if 'drag_bg' in driver.page_source:
                        # recognize_code(driver)
                        time.sleep(1)
                    else:
                        break
                except:
                    pass
                else:
                    time.sleep(2)
            # 获取当前页标题元素列表
            title_list = WebDriverWait(driver, 10, 0.5).until(lambda x:x.find_elements(By.CSS_SELECTOR, '#rightContent > div.grid-right > div:nth-child(1) > div.accompanying-wrap >div.item'))
            # print(len(title_list))
            # time.sleep(100)
            for i ,t in enumerate(title_list):
                if (i + 1)< skip_tiao_count:
                    continue
                print(f"正在采集第{page_count}页第{i+1}条")
                icon = t.find_elements(By.CLASS_NAME,'icon') 
                if len(icon)>0:   
                    icon = True
                else:
                    icon = False
                # 点击标题链接
                while True:
                    try:
                        tt = t.find_element(By.TAG_NAME, 'a')
                    except StaleElementReferenceException as e :
                        time.sleep(0.5)
                    else:
                        break
                title_s = tt.get_attribute('logother')
                title = str(title_s).split('、',maxsplit=1)[1]
                print(icon,title)
                # time.sleep(1)
                driver.implicitly_wait(2)
                tt.click()
                while True:
                    # 跳转页面，解析数据，关闭页面
                    all_pages = driver.window_handles
                    if len(all_pages) >= 2:
                        time.sleep(2)
                        driver.switch_to.window(all_pages[-1])
                        parse_data_content(driver.page_source,title,icon)
                        driver.close()
                        driver.switch_to.window(all_pages[1])
                        print(f"{title}数据采集完成!")
                        break
                time.sleep(1)
            # 下一页
            time.sleep(1)
            # next_page = driver.execute_script("return document.querySelector('#rightContent > div.grid-right > div:nth-child(1) > div:nth-child(3) > ul > li:nth-child(12) > a').hasAttribute('pageindex');")
            # if next_page:
            next_page = WebDriverWait(driver, 10, 0.5).until(lambda x:x.find_element(By.LINK_TEXT,'下一页'))
            next_page.click()
            time.sleep(2)
            # else:
                # break
            page_count += 1