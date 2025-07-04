import time
import re
import os
import pickle
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def load_cookies_from_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            cookies = pickle.load(f)
        print(f"Đã tải cookie thành công từ '{filepath}'.")
        return cookies
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file cookie '{filepath}'.")
        print("Vui lòng chạy lại script đăng nhập để tạo file cookie trước.")
        return None
    except Exception as e:
        print(f"Lỗi khi đọc file cookie: {e}")
        return None

class TikTokScraper:
    def __init__(self, cookies):
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--start-maximized")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_argument('--log-level=3')

        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(300)
        self.cookies = cookies

    def set_cookies(self):
        print("Đang thiết lập cookies...")
        self.driver.get("https://www.tiktok.com/")
        self.driver.delete_all_cookies()
        for cookie in self.cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        time.sleep(2)

    @staticmethod
    def _parse_number(text):
        text = text.upper().strip()
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1_000)
        if 'M' in text:
            return int(float(text.replace('M', '')) * 1_000_000)
        if 'T' in text:
            return int(float(text.replace('T', '')) * 1_000_000_000)
        return int(text.replace(',', '').strip())

    @staticmethod
    def _parse_duration(duration_str):
        parts = duration_str.split(':')
        return int(parts[-1]) + int(parts[-2]) * 60 if len(parts) == 2 else int(parts[-1])

    @staticmethod
    def _convert_timestamp_to_date(timestamp):
        if not timestamp or timestamp == 0:
            return ""
        try:
            return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            return ""

    def _scroll_page(self):
        print("Đang cuộn trang để tải tất cả video...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        attempts = 0
        max_attempts = 20
        while attempts < max_attempts:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                attempts += 1
            else:
                attempts = 0
            last_height = new_height

    def _get_video_urls(self, channel_url):
        self.driver.get(channel_url)
        time.sleep(3)

        # Extract profile stats: followers, hearts, total videos
        try:
            followers_text = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="followers-count"]').text.strip()
            follower_count = self._parse_number(followers_text)
        except:
            follower_count = 0
        try:
            heart_text = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="heart-count"]').text.strip()
            heart_count = self._parse_number(heart_text)
        except:
            heart_count = 0
        try:
            video_text = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="video-count"]').text.strip()
            video_count = self._parse_number(video_text)
        except:
            video_count = 0

        # Scroll to load all videos
        self._scroll_page()
        elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"]')
        video_data = []
        for elem in elements:
            try:
                link = elem.find_element(By.TAG_NAME, 'a').get_attribute('href')
                views_text = elem.find_element(By.CSS_SELECTOR, '[data-e2e="video-views"]').text.strip()
                views = self._parse_number(views_text)
                video_data.append({
                    "url": link,
                    "playCount": views,
                    "followers": follower_count,
                    "heartCount": heart_count,
                    "videoCount": video_count
                })
            except:
                continue
        return video_data

    def _extract_video_details(self, video_info):
        self.driver.get(video_info['url'])
        time.sleep(3)
        html_source = self.driver.page_source

        data = {
            "webVideoUrl": video_info.get('url', ''),
            "playCount": video_info.get('playCount', 0),
            "followers": video_info.get('followers', 0),
            "heartCount": video_info.get('heartCount', 0),
            "videoCount": video_info.get('videoCount', 0)
        }

        def get_count(selector):
            try:
                txt = self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                return self._parse_number(txt)
            except:
                return 0

        data["author"] = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="browse-username"]').text.strip()
        data["text"] = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="browse-video-desc"]').text.strip()
        data["diggCount"] = get_count('[data-e2e="like-count"]')
        data["shareCount"] = get_count('[data-e2e="share-count"]')
        data["commentCount"] = get_count('[data-e2e="comment-count"]')
        try:
            col = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="undefined-count"]')
            data["collectCount"] = self._parse_number(col[0].text.strip()) if col else 0
        except:
            data["collectCount"] = 0

        try:
            dur = self.driver.find_element(By.CSS_SELECTOR, '.css-1cuqcrm-DivSeekBarTimeContainer')\
                          .text.split('/')[-1].strip()
            data["duration"] = self._parse_duration(dur)
        except:
            data["duration"] = 0

        ts_list = sorted(int(x) for x in re.findall(r'"createTime":\s*"(\d+)"', html_source) if int(x)!=0)
        data["Ngày tạo kênh"] = self._convert_timestamp_to_date(ts_list[0]) if ts_list else ""
        data["Ngày đăng"] = self._convert_timestamp_to_date(ts_list[-1]) if ts_list else ""

        data["hashtags"] = [
            a.text.strip('# ')
            for a in self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="browse-video-desc"] a strong')
        ]

        m1 = re.search(r'"isAd":(true|false)', html_source)
        m2 = re.search(r'"isADVirtual":(true|false)', html_source)
        data["isAd"] = m1.group(1) if m1 else ""
        data["isADVirtual"] = m2.group(1) if m2 else ""

        return data

    def scrape_channels(self, channel_names):
        all_data = []
        for name in channel_names:
            print(f"\n--- Đang xử lý kênh: {name} ---")
            url = f"https://www.tiktok.com/@{name}"
            try:
                vids = self._get_video_urls(url)
                if not vids:
                    print(f"No videos for {name}.")
                    continue
                for idx, info in enumerate(vids, 1):
                    print(f"Video {idx}/{len(vids)}: {info['url']}")
                    try:
                        detail = self._extract_video_details(info)
                        detail["channel"] = name
                        all_data.append(detail)
                    except Exception as e:
                        print(f"  Lỗi chi tiết: {e}")
            except Exception as e:
                print(f"  Lỗi khi xử lý kênh {name}: {e}")
        return all_data

    def quit(self):
        self.driver.quit()


class GoogleSheetExporter:
    def __init__(self, credentials_file, spreadsheet_id, sheet_name):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        self.service = build('sheets', 'v4', credentials=creds)

    def export(self, data):
        if not data:
            print("Không có dữ liệu để xuất.")
            return
        header = [
            "Kênh","Author","Followers","Text","Likes","Shares","Comments","Collects",
            "Duration(s)","Ngày tạo kênh","Ngày đăng","Hashtags","URL Video","Views",
            "followerCount","heartCount","videoCount","isAd","isADVirtual"
        ]
        values = [header]
        for it in data:
            values.append([
                it.get("channel",""), it.get("author",""), it.get("followers",0), it.get("text",""),
                it.get("diggCount",0), it.get("shareCount",0), it.get("commentCount",0),
                it.get("collectCount",0), it.get("duration",0),
                it.get("Ngày tạo kênh",""), it.get("Ngày đăng",""),
                ', '.join(it.get("hashtags",[])), it.get("webVideoUrl",""),
                it.get("playCount",0),
                it.get("followerCount",0), it.get("heartCount",0), it.get("videoCount",0),
                it.get("isAd",""), it.get("isADVirtual","")
            ])
        body = {"values": values}
        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id, range=self.sheet_name
            ).execute()
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=f"{self.sheet_name}!A1",
                valueInputOption="RAW", body=body
            ).execute()
            print(f"Thành công! Dữ liệu đã được lưu vào Google Sheets: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
        except HttpError as e:
            print(f"Lỗi khi tương tác với Google Sheets API: {e}")

def main():
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID','17cnmrpZLq5f5nAzg_L9zC6ivpaG2CohavSDwC-PBLX8')
    SHEET_NAME = os.getenv('SHEET_NAME','testtt1')
    CREDENTIALS_FILE = './credentials.json'
    COOKIE_FILE = 'tiktok_cookie.pkl'

    cookies = load_cookies_from_file(COOKIE_FILE)
    if not cookies:
        return
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Lỗi: Không tìm thấy file '{CREDENTIALS_FILE}'.")
        return

    channels_input = input("Nhập tên các kênh TikTok (cách nhau bởi dấu phẩy): ")
    if not channels_input:
        print("Không có kênh nào được nhập.")
        return
    channels = [c.strip() for c in channels_input.split(',')]

    scraper = TikTokScraper(cookies)
    try:
        scraper.set_cookies()
        scraped_data = scraper.scrape_channels(channels)
        if scraped_data:
            GoogleSheetExporter(CREDENTIALS_FILE, SPREADSHEET_ID, SHEET_NAME).export(scraped_data)
        else:
            print("Không thu thập được dữ liệu video nào.")
    except Exception as e:
        print(f"Lỗi khi chạy script: {e}")
    finally:
        scraper.quit()
        print("Kết thúc chương trình.")

if __name__ == "__main__":
    main()
