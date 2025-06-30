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
        self._scroll_page()
        elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"]')
        video_data = []
        for elem in elements:
            try:
                link = elem.find_element(By.TAG_NAME, 'a').get_attribute('href')
                views_text = elem.find_element(By.CSS_SELECTOR, '[data-e2e="video-views"]').text.strip()
                views = self._parse_number(views_text)
                video_data.append({"url": link, "playCount": views})
            except Exception:
                continue
        return video_data

    def _extract_video_details(self, video_info):
        self.driver.get(video_info['url'])
        time.sleep(3)
        html_source = self.driver.page_source
        data = {"webVideoUrl": video_info.get('url', ''), "playCount": video_info.get('playCount', 0)}

        def get_count(selector):
            try:
                count_text = self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                return self._parse_number(count_text)
            except:
                return 0

        data["author"] = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="browse-username"]').text.strip()
        data["text"] = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="browse-video-desc"]').text.strip()
        data["diggCount"] = get_count('[data-e2e="like-count"]')
        data["shareCount"] = get_count('[data-e2e="share-count"]')
        data["commentCount"] = get_count('[data-e2e="comment-count"]')
        
        try:
            collect_elems = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="undefined-count"]')
            data["collectCount"] = self._parse_number(collect_elems[0].text.strip()) if collect_elems else 0
        except:
            data["collectCount"] = 0
            
        try:
            duration_text = self.driver.find_element(By.CSS_SELECTOR, '.css-1cuqcrm-DivSeekBarTimeContainer').text.split('/')[-1].strip()
            data["duration"] = self._parse_duration(duration_text)
        except:
            data["duration"] = 0
        
        timestamps_str = re.findall(r'"createTime":\s*"(\d+)"', html_source)
        timestamps = sorted([int(ts) for ts in timestamps_str if int(ts) != 0])
        data["Ngày tạo kênh"] = self._convert_timestamp_to_date(timestamps[0]) if timestamps else ""
        data["Ngày đăng"] = self._convert_timestamp_to_date(timestamps[-1]) if timestamps else ""
        
        data["hashtags"] = [tag.text.strip('# ') for tag in self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="browse-video-desc"] a strong')]
        match_is_ad = re.search(r'"isAd":(true|false)', html_source)
        data["isAd"] = match_is_ad.group(1) == 'true' if match_is_ad else False
        
        return data

    def scrape_channels(self, channel_names):
        all_data = []
        for channel_name in channel_names:
            print(f"\n--- Đang xử lý kênh: {channel_name} ---")
            channel_url = f"https://www.tiktok.com/@{channel_name}"
            try:
                videos = self._get_video_urls(channel_url)
                if not videos:
                    print(f"Không tìm thấy video nào cho kênh '{channel_name}' hoặc kênh không tồn tại.")
                    continue
                
                print(f"Tìm thấy {len(videos)} video. Bắt đầu trích xuất chi tiết...")
                for idx, video_info in enumerate(videos, 1):
                    print(f"  Video {idx}/{len(videos)}: {video_info['url']}")
                    try:
                        details = self._extract_video_details(video_info)
                        details["channel"] = channel_name
                        all_data.append(details)
                    except Exception as e:
                        print(f"  Lỗi khi trích xuất chi tiết video: {e}")
            except Exception as e:
                print(f"Lỗi nghiêm trọng khi xử lý kênh {channel_name}: {e}")
        return all_data

    def quit(self):
        self.driver.quit()


class GoogleSheetExporter:
    def __init__(self, credentials_file, spreadsheet_id, sheet_name):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        self.service = build('sheets', 'v4', credentials=creds)

    def export(self, data):
        if not data:
            print("Không có dữ liệu để xuất.")
            return

        print(f"Đang chuẩn bị xuất {len(data)} hàng dữ liệu ra Google Sheets...")
        
        header = [
            "Kênh", "Author", "Text", "Likes", "Shares", "Comments", "Collects",
            "Duration(s)", "Ngày tạo kênh", "Ngày đăng", "Hashtags", "URL Video", "Views", "isAd"
        ]
        
        values = [header]
        for item in data:
            values.append([
                item.get("channel", ""), item.get("author", ""), item.get("text", ""),
                item.get("diggCount", 0), item.get("shareCount", 0), item.get("commentCount", 0),
                item.get("collectCount", 0), item.get("duration", 0),
                item.get("Ngày tạo kênh", ""), item.get("Ngày đăng", ""),
                ', '.join(item.get("hashtags", [])), item.get("webVideoUrl", ""),
                item.get("playCount", 0), item.get("isAd", False)
            ])

        body = {"values": values}
        
        try:
            print(f"Đang xóa dữ liệu cũ trong sheet '{self.sheet_name}'...")
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id, range=self.sheet_name
            ).execute()

            print(f"Đang ghi dữ liệu mới vào sheet '{self.sheet_name}'...")
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=f"{self.sheet_name}!A1",
                valueInputOption="RAW", body=body
            ).execute()
            
            print(f"Thành công! Dữ liệu đã được lưu vào Google Sheets: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")

        except HttpError as e:
            print(f"\nLỗi khi tương tác với Google Sheets API: {e}")
            print("Vui lòng kiểm tra lại: \n1. Spreadsheet ID có đúng không? \n2. Bạn đã chia sẻ Sheet cho email trong file credentials.json chưa (với quyền Editor)?")


def main():
    SPREADSHEET_ID = '17cnmrpZLq5f5nAzg_L9zC6ivpaG2CohavSDwC-PBLX8' 
    SHEET_NAME = 'testtt'
    CREDENTIALS_FILE = './credentials.json'
    COOKIE_FILE = 'tiktok_cookie.pkl'
    
    cookies = load_cookies_from_file(COOKIE_FILE)
    if not cookies:
        return

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Lỗi: Không tìm thấy file '{CREDENTIALS_FILE}'. Vui lòng đặt file credentials vào cùng thư mục.")
        return

    channels_input = input("Nhập tên các kênh TikTok (cách nhau bởi dấu phẩy): ")
    if not channels_input:
        print("Không có kênh nào được nhập. Kết thúc chương trình.")
        return
        
    channels = [ch.strip() for ch in channels_input.split(",")]
    
    scraper = TikTokScraper(cookies=cookies)
    
    try:
        scraper.set_cookies()
        scraped_data = scraper.scrape_channels(channels)
        
        if scraped_data:
            exporter = GoogleSheetExporter(CREDENTIALS_FILE, SPREADSHEET_ID, SHEET_NAME)
            exporter.export(scraped_data)
        else:
            print("\nQuá trình cào dữ liệu không thu được kết quả nào.")

    except Exception as e:
        print(f"\nĐã xảy ra lỗi không mong muốn trong quá trình chạy: {e}")
    finally:
        scraper.quit()
        print("\nChương trình đã kết thúc.")

if __name__ == "__main__":
    main()