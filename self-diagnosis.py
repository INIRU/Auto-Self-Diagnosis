"""
 _____        _   __         ______  _                                   _
/  ___|      | | / _|        |  _  \(_)                                 (_)
\ `--.   ___ | || |_  ______ | | | | _   __ _   __ _  _ __    ___   ___  _  ___
 `--. \ / _ \| ||  _||______|| | | || | / _` | / _` || '_ \  / _ \ / __|| |/ __|
/\__/ /|  __/| || |          | |/ / | || (_| || (_| || | | || (_) |\__ \| |\__ \
\____/  \___||_||_|          |___/  |_| \__,_| \__, ||_| |_| \___/ |___/|_||___/
                                                __/ |
                                               |___/
"""

import json
import os
import datetime
import asyncio
import webbrowser
import requests
import re
import zipfile
import pyautogui

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import SessionNotCreatedException, NoAlertPresentException
from selenium import webdriver
from bs4 import BeautifulSoup


class Self_Diagnosis():
    __version__ = "0.0.8"

    def __init__(self):
        asyncio.run(self.start_menu())

    def dia_input(self, text):
        return input("[ 자가진단 ] " + text)

    def dia_printf(self, text):
        print("[ 자가진단 ] " + text)

    async def last_ver(self):
        """
        github에 있는 마지막 버전을 가져옵니다.
        """
        r = requests.get(
            "https://github.com/INIRU/Auto-Self-Diagnosis/releases")
        soup = BeautifulSoup(r.content, "html.parser")
        return soup.find_all(attrs={'class': 'css-truncate-target'}, style="max-width: 125px")[0].text

    async def info_new(self, reason: bool = True):
        """
        database 폴더 안에 있는 my_info.json의 잘 못된 데이터가 있을 경우
        이 함수를 호출하여 초기화 시킵니다.
        """
        os.system("cls")
        if reason == True:
            self.dia_printf("데이터 파일에 등록된 데이터 중 잘못된 값이 있습니다.")
        with open("./database/my_info.json", "r", encoding="utf-8") as r:
            info = json.load(r)
        for key in list(info.keys()):
            info[key] = None
        info["waitingTime"] = 1.7
        info["lastday"] = 1
        info["last_dia"] = 1
        with open("./database/my_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)

    async def info_data_load(self):
        """
        database 폴더 안에 있는 my_info.json을 불러옵니다.
        불러오던 더 중 my_info.json에 값이 누락되어 있는 경우 데이터를 초기화 시킵니다.
        """
        os.system("cls")
        self.dia_printf("데이터 파일을 불러오는중입니다.")
        if not os.path.exists("./database"):
            self.dia_printf("database 폴더가 없습니다. 생성하겠습니다.")
            os.mkdir("./database")
        if not os.path.isfile("./database/my_info.json"):
            self.dia_printf("my_info.json이 없습니다. 생성하겠습니다.")
            open("./database/my_info.json", 'w')
            info = {
                "last_dia": 1,
                "lastday": 1,
                "Dia_Time": None,
                "waitingTime": 1.7,
                "CityCode": None,
                "SchLvlCode": None,
                "SchoolName": None,
                "My_Name": None,
                "My_Bir": None,
                "My_Pass": None
            }
            with open("./database/my_info.json", "w", encoding="utf-8") as f:
                json.dump(info, f, indent=4, ensure_ascii=False)
        with open("./database/my_info.json", "r", encoding="utf-8") as r:
            info = json.load(r)
        self.dia_printf("누락된 값이 있는지 확인중입니다.")
        for key in list(info.keys()):
            if info[key] is None:
                await self.info_new()
                info = await self.data_setup()
            elif info[key] is not None:
                self.dia_printf(f"{key} | ✔")
        self.dia_printf("데이터 파일을 성공적으로 불러왔습니다.")
        return info

    async def data_setup(self):
        """
        database 폴더 안에 있는 my_info.json에 데이터가 None인 경우
        데이터 등록을 위해 이 함수가 호출됩니다.
        """
        os.system("cls")
        with open("./database/my_info.json", "r", encoding="utf-8") as r:
            info = json.load(r)
        while True:
            os.system("cls")
            yes_or_no = self.dia_input(
                "데이터파일에 데이터가 존재하지 않습니다.\n등록하시겠습니까? (Y/N) : ")
            os.system("cls")
            if yes_or_no.upper() == "N":
                self.dia_printf("데이터를 등록하지 않아 프로그램이 5초후 종료됩니다.")
                await asyncio.sleep(5)
                exit()
            elif yes_or_no.upper() == "Y":
                async def dia_time():
                    while True:
                        os.system("cls")
                        diatime = self.dia_input(
                            "자동으로 자가 진단을 실행할 시간을 입력하여 주세요.\n\nex) 오전 7시20분 -> 7:20 오후 1시:20분 -> 13:20 | (시:분) : ")
                        try:
                            time = datetime.datetime.strptime(diatime, "%H:%M")
                            self.dia_printf(
                                f"시간이 등록되었습니다. : " + time.strftime('%p %I:%M').replace('PM', '오후').replace('AM', '오전'))
                            await asyncio.sleep(0.7)
                            return diatime
                        except ValueError:
                            pyautogui.alert(
                                text="지정된 시간타입으로 입력하여주세요. | (시|분)", title="[ ERROR ]", button="OK")

                async def City_Code():
                    Citylist = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
                                "경기", "강원", "충청북", "충청남", "전라북", "전라남", "경상북", "경상남", "제주"]
                    while True:
                        os.system("cls")
                        City = self.dia_input(
                            "자신의 학교 관할 교육청의 지역을 입력하여 주세요. ex) 서울특별시, 서울, 인천 : ")
                        CityCode = None
                        for i, city in enumerate(Citylist):
                            if City.startswith(city):
                                CityCode = f"{i+1:02b}"
                                self.dia_printf(f"정상적으로 등록되었습니다. | {City}")
                                await asyncio.sleep(0.7)
                                return str(CityCode)
                        if CityCode is None:
                            pyautogui.alert(text="인식할 수 없는 지역입니다.",
                                            title="[ ERROR ]", button="OK")

                async def SchLvl():
                    SchLvllist = ["유", "초", "중", "고", "특"]
                    while True:
                        os.system("cls")
                        SchLvl = self.dia_input(
                            "자신의 학교급을 입력하여 주세요. ex) 유치원, 초등학교, 중학교, 고등학교, 특수학교 : ")
                        SchLvlCode = None
                        for i, SchLvlName in enumerate(SchLvllist):
                            if SchLvl.startswith(SchLvlName):
                                SchLvlCode = i + 1
                                self.dia_printf(f"정상적으로 등록되었습니다. | {SchLvl}")
                                await asyncio.sleep(0.7)
                                return str(SchLvlCode)
                        if SchLvlCode is None:
                            pyautogui.alert(text="인식할 수 없는 학교급입니다.",
                                            title="[ ERROR ]", button="OK")

                async def Sch_Name():
                    while True:
                        os.system("cls")
                        SchName = self.dia_input(
                            "다니고 있는 학교(유치원) 명을 입력하여 주세요. ex) 자진중, 자진고등학교 : ")
                        if len(SchName) <= 1:
                            pyautogui.alert(text="2글자 이상으로 입력하여주세요.",
                                            title="[ ERROR ]", button="OK")
                        elif len(SchName) >= 2:
                            self.dia_printf(f"정상적으로 등록되었습니다. | {SchName}")
                            await asyncio.sleep(0.7)
                            return SchName

                async def MyName():
                    while True:
                        os.system("cls")
                        My_Name = self.dia_input("자신의 본명을 입력하여주세요. : ")
                        self.dia_printf(f"정상적으로 등록되었습니다. : {My_Name}")
                        await asyncio.sleep(0.7)
                        return My_Name

                async def MyBir():
                    while True:
                        os.system("cls")
                        My_Bir = self.dia_input(
                            "자신의 생년월일 6자리를 입력하여 주세요. ex) 050819 : ")
                        if len(My_Bir) != 6:
                            pyautogui.alert(text="6자리를 입력하여 주세요.",
                                            title="[ ERROR ]", button="OK")
                        elif len(My_Bir) == 6:
                            self.dia_printf(f"정상적으로 등록되었습니다. | {My_Bir}")
                            await asyncio.sleep(0.7)
                            return My_Bir

                async def MyPass():
                    while True:
                        os.system("cls")
                        My_Pass = self.dia_input(
                            "자신의 자가진단 비밀번호 4자리를 입력하여 주세요. : ")
                        if len(My_Pass) != 4:
                            pyautogui.alert(text="4자리를 입력하여 주세요.",
                                            title="[ ERROR ]", button="OK")
                        elif len(My_Pass) == 4:
                            self.dia_printf("비밀번호가 정상적으로 등록되었습니다.")
                            await asyncio.sleep(0.7)
                            return My_Pass

                info["Dia_Time"] = await dia_time()
                info["CityCode"] = await City_Code()
                info["SchLvlCode"] = await SchLvl()
                info["SchoolName"] = await Sch_Name()
                info["My_Name"] = await MyName()
                info["My_Bir"] = await MyBir()
                info["My_Pass"] = await MyPass()
                with open("./database/my_info.json", "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=4, ensure_ascii=False)
                return info

    async def update(self):
        """
        github에서 맨 마지막 릴리스 버전을 확인하고 마지막 릴리스 버전이 현재 릴리스 버전보다 높으면
        웹사이트로 이동합니다.
        """
        os.system("cls")
        self.dia_printf("새로운 버전이 있는지 확인 중입니다.")
        last_version = await self.last_ver()
        if int(self.__version__.replace(".", "")) < int(last_version.replace(".", "")):
            self.dia_printf(
                f"새로운 업데이트가 있습니다.\n현재 버전: {self.__version__}\n최신 버전: {last_version}\n\n파일을 다운받는중...")
            r = requests.get(
                f"https://github.com/INIRU/Auto-Self-Diagnosis/releases/download/{last_version}/Auto-Self-Diagnosis.zip")
            with open("Auto-Self-Diagnosis.zip", "wb") as file:
                file.write(r.content)
            dia_zip = zipfile.ZipFile("./Auto-Self-Diagnosis.zip", "r")
            for file in dia_zip.namelist():
                if "driver/" in str(file):
                    dia_zip.extract(file)
            dia_zip.extract("└┌░í┴°┤▄.exe")
            if os.path.isfile("./읽어주세요.txt"):
                os.remove("./읽어주세요.txt")
            dia_zip.extract("└╨╛ε┴╓╝╝┐Σ.txt")
            dia_zip.close()
            if os.path.isfile("./Auto-Self-Diagnosis.zip"):
                os.remove("./Auto-Self-Diagnosis.zip")
            if os.path.isfile("./자가진단.exe"):
                os.rename("./자가진단.exe", "./자가진단_old.exe")
            await asyncio.sleep(0.5)
            if os.path.isfile("./└┌░í┴°┤▄.exe"):
                os.rename("./└┌░í┴°┤▄.exe", "./자가진단.exe")
            if os.path.isfile("./└╨╛ε┴╓╝╝┐Σ.txt"):
                os.rename("./└╨╛ε┴╓╝╝┐Σ.txt", "./읽어주세요.txt")
            while True:
                os.system("cls")
                yes_no = self.dia_input(
                    "업데이트가 완료되었습니다.\n\n자가진단_old.exe는 제거 해주세요.\n프로그램을 종료하시겠습니까? (Y/N) : ")
                if yes_no.upper() == "Y":
                    exit()
                elif yes_no.upper() == "N":
                    await self.start_menu()
                    break
        elif int(self.__version__.replace(".", "")) == int(last_version.replace(".", "")):
            self.dia_printf("이미 최신 버전 입니다.")

    async def driver_setup(self):
        """
        크롬 드라이버를 준비하고 셋팅하는 함수 입니다. driver 폴더에 있는 크롬 드라이버들을
        버전 순서대로 내려가며 자신의 크롬 브라우저에 맞는 드라이버를 찾습니다.
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("disable-gpu")
        chrome_options.add_argument('headless')
        chrome_options.add_argument('window-size=1920x1080')
        for bw in os.listdir("./driver"):
            print(f"[ CHROME DRIVER ] Select : {bw}")
            try:
                browser = webdriver.Chrome(
                    f"./driver/{bw}", chrome_options=chrome_options)
                return browser
            except SessionNotCreatedException:
                self.dia_printf(
                    "크롬 브라우저와 크롬 드라이버가 호환되지 않습니다.\n\n[ 자가진단 ] 다른 버전의 크롬 드라이버로 다시 진행합니다.")
        while True:
            os.system("cls")
            yes_no = self.dia_input(
                "크롬 브라우저가 없거나 호환되는 드라이버가 없습니다.\n\n 크롬 브라우저 업데이트(다운로드) 받기 (Y/N) : ")
            if yes_no.upper() == "N":
                exit()
            elif yes_no.upper() == "Y":
                webbrowser.open(
                    "https://www.google.co.kr/chrome/?brand=IBEF&gclid=CjwKCAjwv_iEBhASEiwARoemvEvKcHLytJDw3JXmNJOBqSdeBoJt0K1NEtYWABIsyE5kMb22O4Z2JhoCVckQAvD_BwE&gclsrc=aw.ds")
                break
        while True:
            os.system("cls")
            yes_no = self.dia_input(
                "크롬 브라우저를 다운로드(업데이트)를/(을) 하셨나요? (Y/N) : ")
            if yes_no.upper() == "N":
                exit()
            elif yes_no.upper() == "Y":
                await self.dia_start()
                break

    async def lastday_set(self):
        """
        마지막으로 자가진단을 한 날짜를 데이터에 등록합니다.
        """
        now = datetime.datetime.now()
        with open("./database/my_info.json", "r", encoding="utf-8") as r:
            info = json.load(r)
        info["last_dia"] = str(now.strftime("%Y %m %d %H %M"))
        info["lastday"] = int(now.strftime("%Y%m%d"))
        with open("./database/my_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)

    async def screenshot(self, driver):
        """
        자가진단을 완료 후 완료한 웹페이지에서 화면을 캡처합니다.
        """
        now = datetime.datetime.now()
        nowtime = now.strftime("%Y-%m-%d_%H-%M-%S")
        if not os.path.exists("./screenshot"):
            self.dia_printf("screenshot 폴더가 없습니다. 생성하겠습니다.")
            os.mkdir("./screenshot")
        self.dia_printf("화면을 캡쳐합니다.")
        driver.save_screenshot(f"./screenshot/{nowtime}_screenshot.png")
        self.dia_printf(f"캡쳐한 사진을 정삭적으로 저장하였습니다. | {nowtime}_screenshot.png")

    async def start_menu(self):
        """
        프로그램을 실행 시켰을때 처음 나오는 메뉴이다.
        """
        await self.update()
        last_version = await self.last_ver()
        if int(self.__version__.replace(".", "")) == int(last_version.replace(".", "")):
            version_stats = "최신버전"
        elif int(self.__version__.replace(".", "")) != int(last_version.replace(".", "")):
            version_stats = "구버전"
        if os.path.isfile("./자가진단_old.exe"):
            os.remove("./자가진단_old.exe")
        while True:
            os.system("cls")
            print(
                "┍──────────────────────────────"
                "\n│"
                "\n│   자동 자가진단 (Auto Self Diagnosis)"
                "\n│"
                "\n│"
                "\n│   1. 자동 자가진단"
                "\n│"
                "\n│   2. 자신의 정보 초기화"
                "\n│"
                "\n│"
                "\n│  * 제작자 : INIRU#0001"
                f"\n│  * 버전   : {self.__version__} | {version_stats}"
                "\n│"
                "\n┕──────────────────────────────\n"
            )
            menu_sec = self.dia_input("원하는 항목의 숫자를 입력하고 엔터(Enter) : ")
            if str(menu_sec) == "1":
                await self.dia_start()
                break
            elif str(menu_sec) == "2":
                await self.info_initialization_menu()
                break

    async def info_initialization_menu(self):
        """
        정보초기화 메뉴
        """
        info = await self.info_data_load()
        os.system("cls")
        dia_time = (datetime.datetime.strptime(info["Dia_Time"], "%H:%M")).strftime(
            "%p %I:%M").replace("PM", "오후").replace("AM", "오전")
        City = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시",
                "경기도", "강원도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주도"]
        SchLvl = ["유치원", "초등학교", "중학교", "고등학교", "특수학교"]
        while True:
            os.system("cls")
            print(
                f"자동 자가진단 시간 | {dia_time}"
                f"\n교육청 지역 | {City[int(info['CityCode'])-1]}"
                f"\n학교급 | {SchLvl[int(info['SchLvlCode'])-1]}"
                f"\n학교명 | {info['SchoolName']}\n"
                f"\n이름 | {info['My_Name']}"
                f"\n생년월일 (6자리) | {info['My_Bir']}"
                f"\n자가진단 비밀번호 | {info['My_Pass'][:2]+'**'}\n"
            )
            yes_no = self.dia_input("데이터를 초기화 하실건가요? (Y/N) : ")
            if yes_no.upper() == "Y":
                await self.info_new(False)
                await self.start_menu()
                break
            elif yes_no.upper() == "N":
                await self.start_menu()
                break

    async def dia_start(self):
        """
        자동자가진단 시작
        """
        while True:
            info = await self.info_data_load()
            now = datetime.datetime.now()
            os.system("cls")
            if int(now.strftime("%H%M")) >= int(info["Dia_Time"].replace(":", "")) and int(now.strftime("%Y%m%d")) != info["lastday"]:

                # 홈페이지 접속 준비 드라이버 셋업

                driver = await self.driver_setup()
                waitingTime = info["waitingTime"]
                driver.get("https://hcs.eduro.go.kr/#/loginHome")
                self.dia_printf("자가진단 웹페이지에 접속하였습니다.")

                # 학교 정보 입력

                driver.find_element_by_id(
                    "btnConfirm2").click()  # 자가진단 참여하기 GO 버튼
                self.dia_printf("자가진단 참여하기 버튼을 클릭하였습니다.")
                driver.find_element_by_xpath(
                    "//input[@class='input_text_common input_text_search']").click()
                self.dia_printf("학교를 검색합니다.")
                await asyncio.sleep(waitingTime)
                driver.find_element_by_xpath(
                    "//select['data-v-f6ebec28 name id']/option[@value='" + info["CityCode"] + "']").click()  # 시/도 설정 메뉴
                driver.find_element_by_xpath(
                    "//select['data-v-f6ebec28']/option[@value='" + info["SchLvlCode"] + "']").click()  # 학교급 설정 메뉴
                elem = driver.find_element_by_xpath(
                    "//input[@class='searchArea']")  # 학교검색메뉴
                elem.click()
                elem.send_keys(info["SchoolName"])
                elem.send_keys(Keys.ENTER)
                await asyncio.sleep(waitingTime)
                try:
                    alert = driver.switch_to.alert
                    message = alert.text
                    alert.accept()
                    if message in ("최소 2자리 이상 학교명을 입력해주세요", "검색결과가 없습니다"):
                        driver.close()
                        await self.info_new()
                        await self.start_menu()
                    elif message == "찾을 학교명을 입력해주세요":
                        driver.close()
                        os.system("cls")
                        self.dia_printf("학교명을 입력하던도중 에러가 발생하여 다시시도 합니다.")
                        await self.dia_start()
                except NoAlertPresentException:
                    pass
                driver.find_element_by_xpath(
                    "//*[@id='softBoardListLayer']/div[2]/div[1]/ul").click()
                driver.find_element_by_class_name("layerFullBtn").click()
                self.dia_printf(f"{info['SchoolName']} 를/(을) 선택하였습니다.")
                await asyncio.sleep(waitingTime)
                self.dia_printf(f"신상 정보를 입력합니다.")
                elem = driver.find_element_by_xpath(
                    "//input[@class='input_text_common']")
                elem.click()
                elem.send_keys(info["My_Name"])
                elem = driver.find_element_by_xpath(
                    "//input[@inputmode='numeric']")
                elem.send_keys(info["My_Bir"])
                driver.find_element_by_xpath(
                    "//input[@id='btnConfirm']").click()
                await asyncio.sleep(0.5)
                try:
                    alert = driver.switch_to.alert
                    message = alert.text
                    alert.accept()
                    if message.startswith("입력하신"):
                        driver.close()
                        await self.info_new()
                        await self.dia_start()
                except NoAlertPresentException:
                    pass
                self.dia_printf("신상 정보 입력을 완료하였습니다.")
                await asyncio.sleep(waitingTime)
                self.dia_printf("비밀번호를 통해 사용자 인증을 시도합니다.")
                elem = driver.find_element_by_xpath(
                    "//input[@class='input_text_common']")  # 비밀번호입력폼
                elem.send_keys(info["My_Pass"])
                driver.find_element_by_xpath(
                    "//input[@id='btnConfirm']").click()  # 비밀번호제출
                self.dia_printf("비밀번호를 통해 사용자 인증을 완료했습니다.")
                await asyncio.sleep(waitingTime)
                self.dia_printf(
                    f"{info['SchoolName']} 를/(을) 재학중이신 {info['My_Name']}님 자가진단 (무증상)을 시작합니다.")
                driver.find_elements_by_class_name("btn")[0].click()
                await asyncio.sleep(0.5)
                try:
                    alert = driver.switch_to.alert
                    message = alert.text
                    alert.accept()
                    time = int(re.findall(r"약(\d)분", message)[0])
                    self.dia_printf(f"알림이 감지되었습니다. {time}분 후에 다시 시도하겠습니다.")
                    await asyncio.sleep((time * 60))
                    self.dia_printf(f"{time}분이 지나 다시 시도하겠습니다.")
                    driver.find_elements_by_class_name("btn")[0].click()
                except NoAlertPresentException:
                    pass
                await asyncio.sleep(waitingTime)
                driver.find_element_by_xpath(
                    "//input[@id='survey_q1a1']").click()
                driver.find_element_by_xpath(
                    "//input[@id='survey_q2a1']").click()
                driver.find_element_by_xpath(
                    "//input[@id='survey_q3a1']").click()
                driver.find_element_by_xpath(
                    "//input[@id='btnConfirm']").click()
                self.dia_printf(
                    f"{info['SchoolName']} 를/(을) 재학중이신 {info['My_Name']}님 자가진단 (무증상)으로 완료되었습니다.")
                await self.lastday_set()
                await asyncio.sleep(0.3)
                await self.screenshot(driver)
                driver.close()
            else:
                time = datetime.datetime.strptime(
                    info["last_dia"], "%Y %m %d %H %M")
                last_dia_Time = time.strftime("%Y. %m. %d %p %I:%M").replace(
                    "PM", "오후").replace("AM", "오전")
                os.system("cls")
                self.dia_printf(
                    f"정해진 시간이 아니여서 실행이 중단되었습니다.\n\n이미 {last_dia_Time}에 자가진단을 완료하였습니다.")
                await asyncio.sleep(5)


Self_Diagnosis()
