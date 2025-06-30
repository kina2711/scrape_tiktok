import os
import pickle
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys

# Tải các biến môi trường từ file .env
dotenv_path = os.path.join(os.path.dirname(__file__), "information.env")
load_dotenv(dotenv_path)

# Lấy thông tin email và mật khẩu
EMAIL = os.getenv("TIKTOK_EMAIL")
PASSWORD = os.getenv("TIKTOK_PASSWORD")

# Khởi tạo trình duyệt
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 15) # Đặt thời gian chờ tối đa là 15 giây

try:
    # 1. Load vào TikTok
    print("1. Đang mở trang chủ TikTok...")
    browser.get("https://www.tiktok.com/vi-VN")

    # 2. Nhấn vào nút "Đăng nhập" chính
    print("2. Tìm và nhấn nút 'Đăng nhập'...")
    login_main_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='TUXButton-label'][text()='Đăng nhập']")))
    login_main_button.click()

    # 3. Nhấn vào nút "Sử dụng số điện thoại / email / tên người dùng"
    print("3. Chọn phương thức đăng nhập...")
    use_phone_email_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Sử dụng số điện thoại/email/tên người dùng')]")))
    use_phone_email_button.click()

    # 4. Nhấn vào tab "Đăng nhập bằng email hoặc tên người dùng"
    print("4. Chuyển sang tab email/tên người dùng...")
    login_with_email_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Đăng nhập bằng email hoặc tên người dùng')]")))
    login_with_email_tab.click()

    # 5. Nhập email
    print("5. Nhập email...")
    email_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="username"]')))
    email_input.send_keys(EMAIL)
    sleep(10)

    # 6. Nhập mật khẩu
    print("6. Nhập mật khẩu...")
    password_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
    password_input.send_keys(PASSWORD)
    sleep(10)
    
    # 7. Nhấn nút "Đăng nhập" cuối cùng
    print("7. Nhấn nút 'Đăng nhập' để gửi thông tin...")
    final_login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="login-button"]')))
    final_login_button.click()

    # Dừng lại để giải CAPTCHA
    print("\n!!! CÓ 120 GIÂY ĐỂ TỰ GIẢI CAPTCHA TRÊN TRÌNH DUYỆT !!!")
    sleep(120)

    # Sau khi đăng nhập thành công, lưu lại cookie
    print("Đang lưu cookie vào file 'tiktok_cookie.pkl'...")
    pickle.dump(browser.get_cookies(), open("tiktok_cookie.pkl", "wb"))
    print("=> Đã lưu cookie thành công!")

except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")

finally:
    # Đóng trình duyệt
    print("Đóng trình duyệt.")
    browser.quit()


