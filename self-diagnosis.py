import selenium
import json
import os
import datetime
import asyncio
import re
import webbrowser
import requests
import zipfile
import subprocess
import ctypes

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, NoAlertPresentException
from selenium.webdriver.common.keys import Keys

now = datetime.datetime.now()
__version__ = "0.0.2"


async def info_data_load():
    """ 
    my_info파일에서 데이터를 불러옵니다.
    """
    print("[ 자가진단 ] 정보파일을 읽겠습니다.")
    with open("./database/my_info.json", "r", encoding="utf-8") as r:
        info = json.load(r)
    for x in list(info.keys()):
        if info[str(x)] == None:
            await info_new(False)
            info = await data_setup()
    print("[ 자가진단 ] 성공적으로 읽었습니다.")
    return info


async def data_setup():
    """ 
    my_info.json에 데이터가 없으면 이 구문이 실행되어 데이터를 등록할 수 있도록 한다.
    """
    with open("./database/my_info.json", "r", encoding="utf-8") as r:
        info = json.load(r)
    yes_or_no = str(
        input("[ 자가진단 ] 당신의 신상데이터가 존재하지 않습니다.\n 등록하시겠습니까? (Y/N) : "))
    if yes_or_no.upper() == "N":
        print("[ 자가진단 ] 프로그램이 5초 뒤 종료됩니다.")
        await asyncio.sleep(5)
        exit()
    elif yes_or_no.upper() == "Y":
        try:
            dia_Time = input(
                "[ 자가진단 ] 자가진단을 실행할 시간을 입력하여주세요. ex) 오전 7시20분 -> 7:20, 오후 1시20분 -> 13:20 : ")
            time = datetime.datetime.strptime(dia_Time, "%H:%M")
            print(
                f"[ 자가진단 ] 시간이 등록되었습니다. : {time.strftime('%p %I:%M').replace('PM', '오후').replace('AM', '오전')}")
        except:
            raise SyntaxError("[ ERROR ] 지정해준 시간타입으로 입력하여주세요.")
        CityCode = str(
            input("[ 자가진단 ] 자신의 학교 관할 교육청의 지역을 입력하여주세요. ex) 서울특별시, 서울, 인천 : "))
        Citylist = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
                    "경기", "강원", "충청북", "충청남", "전라북", "전라남", "경상북", "경상남", "제주"]
        for i, x in enumerate(Citylist):
            if CityCode.startswith(x):
                CityCode = f"{i+1:02b}"
                break
            if (i + 1) == len(Citylist):
                CityCode = None
        if CityCode is None:
            raise SyntaxError(f"[ ERROR ] 인식할 수 없는 지역입니다.")
        print(f"[ 자가진단 ] 지역이 등록되었습니다. : {x}")
        SchLvlCode = str(
            input("[ 자가진단 ] 자신의 학교급을 입력하여주세요. ex) 특수학교, 고등학교, 중학교, 초등학교, 유치원 : "))
        SchLvllist = ["유치원", "초등학교", "중학교", "고등학교", "특수학교"]
        for i, x in enumerate(SchLvllist):
            if SchLvlCode.startswith(x):
                SchLvlCode = f"{i+1}"
                break
            if (i + 1) == len(SchLvllist):
                SchLvlCode = None
        if SchLvlCode is None:
            raise SyntaxError(f"[ ERROR ] 인식할 수 없는 학교급입니다.")
        print(f"[ 자가진단 ] 지역이 등록되었습니다. : 학교급이 등록되었습니다. : {x}")
        SchoolName = str(input("[ 자가진단 ] 자신의 학교명을 입력하여주세요. : "))
        if len(SchoolName) <= 1:
            raise SyntaxError(f"[ ERROR ] 학고명을 2자리 이상으로 입력하여주세요.")
        print(f"[ 자가진단 ] 학교가 등록되었습니다. : {SchoolName}")
        My_Name = str(input("[ 자가진단 ] 자신의 성명을 입력하여주세요. : "))
        print(f"[ 자가진단 ] 성명이 등록되었습니다. : {My_Name}")
        My_Bir = str(input("[ 자가진단 ] 자신의 생년월일 6자리를 입력하여주세요. : "))
        if len(My_Bir) != 6:
            raise SyntaxError("[ ERROR ] 6자리만 입력하여주세요.")
        print(f"[ 자가진단 ] 생년월일이 등록되었습니다. : {My_Bir}")
        My_Pass = str(input("[ 자가진단 ] 자가진단 비밀번호 4자리를 입력하여주세요. : "))
        if len(My_Pass) != 4:
            raise SyntaxError("[ ERROR ] 4자리만 입력하여주세요.")
        print(f"[ 자가진단 ] 성명이 등록되었습니다. : {My_Pass}")
        info["Dia_Time"] = dia_Time
        info["CityCode"] = CityCode
        info["SchLvlCode"] = SchLvlCode
        info["SchoolName"] = SchoolName
        info["My_Name"] = My_Name
        info["My_Bir"] = My_Bir
        info["My_Pass"] = My_Pass
        with open("./database/my_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
        return info


async def last_ver():
    r = requests.get(f"https://github.com/INIRU/Auto-Self-Diagnosis/releases")
    soup = BeautifulSoup(r.content, "html.parser")
    return soup.find_all(attrs={'class': 'css-truncate-target'}, style="max-width: 125px")[0].text


async def update():
    print("[ 자기진단 ] 새로운 버전이 있는지 확인중입니다.")
    last_version = await last_ver()
    if int(__version__.replace(".", "")) < int(last_version.replace(".", "")):
        r = requests.get(
            f"https://github.com/INIRU/Auto-Self-Diagnosis/releases/download/{last_version}/Auto-Self-Diagnosis.zip")
        with open("Auto-Self-Diagnosis.zip", "wb") as file:
            file.write(r.content)
        zipfile.ZipFile("./Auto-Self-Diagnosis.zip").extract("└┌░í┴°┤▄.exe")
        if os.path.isfile("./Auto-Self-Diagnosis.zip"):
            os.remove("./Auto-Self-Diagnosis.zip")
        if os.path.isfile("./자가진단_old.exe"):
            os.rename("./자가진단.exe", "./자가진단_old.exe")
        if os.path.isfile("./자가진단.exe"):
            os.rename("./자가진단.exe", "./자가진단_old.exe")
        await asyncio.sleep(1)
        if os.path.isfile("./└┌░í┴°┤▄.exe"):
            os.rename("./└┌░í┴°┤▄.exe", "./자가진단.exe")
        print("[ 자기진단 ] 업데이트가 완료되었습니다.\n\n자가진단_old.exe는 삭제를 해주세요.")
        exit()
    elif int(__version__.replace(".", "")) == int(last_version.replace(".", "")):
        print("[ 자기진단 ] 이미 최신버전 입니다.")


async def browser_setup():
    """
    크롬 드라이버의 함수이다. driver폴더에 있는 크롬 드라이버 버전 순서대로 내려가며 
    자신의 크롬 브라우저에 맞는 드라이버를 찾습니다.
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
            print(
                "[ 자가진단 ] 크롬 브라우저와 크롬 드라이버가 호환되지 않습니다.\n\n[ 자가진단 ] 다른 버전의 크롬드라이버로 다시 실행합니다.")
    yes_no = str(
        input("[ 자가진단 ] 크롬 브라우저가 없거나 호환되는 드라이버가 없습니다.\n\n구글 크롬 다운받기 (Y/N) : "))
    if yes_no.upper() == "N":
        exit()
    elif yes_no.upper() == "Y":
        webbrowser.open(
            "https://www.google.co.kr/chrome/?brand=IBEF&gclid=CjwKCAjwv_iEBhASEiwARoemvEvKcHLytJDw3JXmNJOBqSdeBoJt0K1NEtYWABIsyE5kMb22O4Z2JhoCVckQAvD_BwE&gclsrc=aw.ds")
        yes_no = str(input("[ 자가진단 ] 크롬 브라우저를 설치(업데이트)를 진행하셨나요? (Y/N) : "))
        if yes_no.upper() == "N":
            exit()
        elif yes_no.upper() == "Y":
            await dia_start()


async def lastday_set(dia_full: int, last_dia: str):
    """
    마지막으로 자가진단을 진행한 날을 등록합니다.
    """
    with open("./database/my_info.json", "r", encoding="utf-8") as r:
        info = json.load(r)
    info["last_dia"] = last_dia
    info["lastday"] = dia_full
    with open("./database/my_info.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)


async def info_new(reason: bool = True):
    """
    my_info를 초기화 시킵니다.
    """
    ctypes.windll.shell32.ShellExecuteA(0, "open", "자가진단.exe", None, None, 1)
    if reason == True:
        print("[ 자가진단 ] 정보가 잘 못 되었습니다.\n\n다시 작성을 시도합니다.")
    with open("./database/my_info.json", "r", encoding="utf-8") as r:
        info = json.load(r)
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


async def screnn_shot(driver):
    """
    자가진단을 완료후 스크린샷을 합니다.
    """
    now = datetime.datetime.now()
    nowtime = now.strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists("./screenshot"):
        print("[ 자가진단 ] 스크린샷 폴더가없는거같아요. 생성하겠습니다.")
        os.mkdir("./screenshot")
        print("[ 자가진단 ] 스크린샷을 찍겠습니다.")
        driver.save_screenshot(f"./screenshot/{nowtime}_screenshot.png")
        print("[ 자가진단 ] 자가진단이 완료되었습니다.")
    else:
        print("[ 자가진단 ] 스크린샷을 찍겠습니다.")
        driver.save_screenshot(f"./screenshot/{nowtime}_screenshot.png")
        print("[ 자가진단 ] 자가진단이 완료되었습니다.")


async def info_initialization_menu():
    """
    정보초기화 메뉴
    """
    os.system("cls")
    info = await info_data_load()
    dia_time = (datetime.datetime.strptime(info["Dia_Time"], "%H:%M")).strftime(
        "%p %I:%M").replace("PM", "오후").replace("AM", "오전")
    City = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
            "경기", "강원", "충청북", "충청남", "전라북", "전라남", "경상북", "경상남", "제주"]
    SchLvl = ["유치원", "초등학교", "중학교", "고등학교", "특수학교"]
    print(f"""
자동 자가진단 시간 | {dia_time}
교육청 지역 | {City[int(info["CityCode"])-1]}
학교급 | {SchLvl[int(info["SchLvlCode"])-1]}
학교명 | {info["SchoolName"]}

이름 | {info["My_Name"]}
생년월일 (6자리) | {info["My_Bir"]}
자가진단 비밀번호 | {info["My_Pass"][:2]+"**"}
""")
    print("")
    yes_no = input("[ 자가진단 ] 정보를 초기화 하시겠습니까? (Y/N) : ")
    if yes_no.upper() == "Y":
        await info_new()
        await start_menu()
    elif yes_no.upper() == "N":
        await start_menu()


async def dia_start():
    """
    자동자가진단 시작
    """
    while True:
        os.system("cls")
        info = await info_data_load()
        now = datetime.datetime.now()
        now_dia_full = int(now.strftime("%Y%m%d"))
        now_last_dia = str(now.strftime("%Y %m %d %H %M"))
        now_dia_time = int(now.strftime("%H%M"))
        if now_dia_time >= int(info["Dia_Time"].replace(":", "")) and now_dia_full != info["lastday"]:

            # 홈페이지 접속 준비
            driver = await browser_setup()
            waitingTime = info["waitingTime"]
            driver.get("https://hcs.eduro.go.kr/#/loginHome")
            print("[ 자가진단 ] 자가진단 웹페이지가 열었습니다.")

            # 학교 정보 입력

            print("[ 자가진단 ] 자가진단 참여버튼을 클릭하겠습니다.")
            driver.find_element_by_id("btnConfirm2").click()  # 자가진단 참여하기 GO 버튼
            driver.find_element_by_xpath(
                "//input[@class='input_text_common input_text_search']").click()
            print("[ 자가진단 ] 당신의 학교데이터를 검색합니다.")
            await asyncio.sleep(waitingTime)
            driver.find_element_by_xpath(
                "//select['data-v-f6ebec28 name id']/option[@value='" + info["CityCode"] + "']").click()  # 시/도 설정 메뉴
            driver.find_element_by_xpath(
                "//select['data-v-f6ebec28']/option[@value='" + info["SchLvlCode"] + "']").click()  # 학교급 설정 메뉴
            elem = driver.find_element_by_xpath(
                "//input[@class='searchArea']")  # 학교검색메뉴
            elem.click()
            elem.send_keys(info["SchoolName"])
            await asyncio.sleep(waitingTime)
            elem.send_keys(Keys.ENTER)
            try:
                alert = driver.switch_to.alert
                message = alert.text
                alert.accept()
                if message in ("최소 2자리 이상 학교명을 입력해주세요", "검색결과가 없습니다"):
                    driver.close()
                    await info_new()
                    await dia_start()
                elif message == "찾을 학교명을 입력해주세요":
                    driver.close()
                    os.system("cls")
                    print("[ 자가진단 ] 학교명을 입력하던도중 에러가 발생하여 다시시도 합니다.")
                    await dia_start()
            except NoAlertPresentException:
                pass
            await asyncio.sleep(waitingTime)
            driver.find_element_by_xpath(
                '//*[@id="softBoardListLayer"]/div[2]/div[1]/ul').click()
            driver.find_element_by_class_name(
                "layerFullBtn").click()  # 학교선택 버튼클릭
            print(f"[ 자가진단 ] {info['SchoolName']} 를/(을) 선택하였습니다.")
            await asyncio.sleep(waitingTime)

            # 신상정보 입력

            print("[ 자가진단 ] 신상 정보를 입력합니다.")
            await asyncio.sleep(waitingTime)
            elem = driver.find_element_by_xpath(
                "//input[@class='input_text_common']")
            elem.click()
            elem.send_keys(info["My_Name"])
            elem = driver.find_element_by_xpath(
                "//input[@inputmode='numeric']")
            elem.send_keys(info["My_Bir"])
            driver.find_element_by_xpath(
                "//input[@id='btnConfirm']").click()  # 신상정보제출
            print("[ 자가진단 ] 신상 정보 입력을 완료했습니다.")
            await asyncio.sleep(0.5)
            try:
                alert = driver.switch_to.alert
                message = alert.text
                alert.accept()
                if message.startswith("입력하신"):
                    driver.close()
                    await info_new()
                    await dia_start()
            except NoAlertPresentException:
                pass
            await asyncio.sleep(waitingTime)
            print("[ 자가진단 ] 비밀번호를 통해 사용자 인증을 시도합니다.")
            await asyncio.sleep(waitingTime)
            elem = driver.find_element_by_xpath(
                "//input[@class='input_text_common']")  # 비밀번호입력폼
            elem.send_keys(info["My_Pass"])
            driver.find_element_by_xpath(
                "//input[@id='btnConfirm']").click()  # 비밀번호제출
            print("[ 자가진단 ] 비밀번호를 통해 사용자 인증을 완료했습니다.")
            await asyncio.sleep(waitingTime)

            # 자가진단 실시

            print(
                f"[ 자가진단 ] {info['SchoolName']} 를/(을) 재학중이신 {info['My_Name']}님 자가진단 (무증상)을 시작합니다.")
            driver.find_elements_by_class_name("btn")[0].click()
            try:
                alert = driver.switch_to.alert
                message = alert.text
                time = int(re.findall(r"약(\d)분", message)[0])
                print(f"[ 자가진단 ] 알림이 감지되었습니다. {time}분 후에 다시 시도하겠습니다.")
                alert.accept()
                await asyncio.sleep((time * 60))
                print(f"[ 자가진단 ] {time}분이 지나 다시 시도하겠습니다.")
                driver.find_elements_by_class_name("btn")[0].click()
            except NoAlertPresentException:
                pass
            await asyncio.sleep(waitingTime)
            driver.find_element_by_xpath("//input[@id='survey_q1a1']").click()
            driver.find_element_by_xpath("//input[@id='survey_q2a1']").click()
            driver.find_element_by_xpath("//input[@id='survey_q3a1']").click()
            driver.find_element_by_xpath("//input[@id='btnConfirm']").click()
            print(
                f"[ 자가진단 ] {info['SchoolName']} 를/(을) 재학중이신 {info['My_Name']}님 자가진단 (무증상)으로 완료되었습니다.")
            await lastday_set(now_dia_full, now_last_dia)
            await asyncio.sleep(waitingTime)
            await screnn_shot(driver)
            driver.close()
            os.system("cls")
            await dia_start()
        else:
            time = datetime.datetime.strptime(
                info["last_dia"], "%Y %m %d %H %M")
            last_dia_Time = time.strftime("%Y. %m. %d %p %I:%M").replace(
                "PM", "오후").replace("AM", "오전")
            os.system("cls")
            print(
                f"[ 자가진단 ] 정해진 시간이 아니여서 실행이 중단되었습니다.\n\n[ 자가진단 ] 이미 {last_dia_Time}에 자가진단을 완료하였습니다.")
            await asyncio.sleep(5)


async def start_menu():
    """
    시작 메뉴
    """
    await update()
    last_version = await last_ver()
    if int(__version__.replace(".", "")) == int(last_version.replace(".", "")):
        if os.path.isfile("./자가진단_old.exe"):
            os.remove("./자가진단_old.exe")
        version_stats = "최신 버전"
    os.system("cls")
    print(f"""
┍──────────────────────────────
│
│   자동 자가진단 (Auto Self Diagnosis)
│
│
│   1. 자동 자가진단
│
│   2. 자신의 정보 초기화
│
│
│  * 제작자 : INIRU#0001
│  * 버전   : {__version__} | {version_stats}
│
┕──────────────────────────────
""")
    value = str(input("[ 자가진단 ] 원하는 항목의 숫자를 입력하고 엔터(Enter) : "))
    if value == "1":
        await dia_start()
    elif value == "2":
        await info_initialization_menu()
    else:
        await start_menu()


asyncio.run(start_menu())  # 비동기 함수 실행
