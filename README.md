# TikTok Channel Scraper & Google Sheets Exporter

This project contains a set of Python scripts designed to automate the process of scraping video data from public TikTok channels and exporting the results directly into a Google Sheet.

It uses Selenium to control a web browser, handles login persistence via cookies, and leverages the Google Sheets API for data output.

## Features

  - **Automated Login**: Performs an initial login to TikTok to capture session cookies.
  - **Cookie Persistence**: Saves login session to a `tiktok_cookie.pkl` file to avoid logging in on every run.
  - **Dynamic Channel Input**: Scrape data from one or more TikTok channels in a single session.
  - **Comprehensive Data Scraping**: Extracts key metrics for each video, including:
      - Views, Likes, Comments, Shares, Saves (Collects)
      - Video Description & Hashtags
      - Video Duration
      - Post Date
  - **Google Sheets Integration**: Automatically clears the target sheet and exports all scraped data in a clean, structured format.

## Prerequisites

  - Python 3.7+
  - Google Chrome browser
  - **ChromeDriver**: The version must match your installed Google Chrome version. You can download it [here](https://googlechromelabs.github.io/chrome-for-testing/).

## Setup & Installation

Follow these steps to set up the project environment.

### 1\. Clone the Repository

```sh
git clone https://github.com/kina2711/scrape_tiktok.git
cd scrape_tiktok
```

### 2\. Install Python Dependencies

It's recommended to use a virtual environment.

```sh
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required libraries
pip install selenium python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3\. Configure Google Sheets API

You need to create a service account and get its credentials to allow the script to write to your Google Sheet.

a. **Enable APIs**: Go to the [Google Cloud Console](https://console.cloud.google.com/).

  - Create a new project (e.g., "TikTok Scraper").
  - In your project, go to "APIs & Services" \> "Library".
  - Search for and enable the **Google Drive API** and the **Google Sheets API**.

b. **Create Service Account**:

  - Go to "APIs & Services" \> "Credentials".
  - Click "Create Credentials" \> "Service account".
  - Give it a name (e.g., "tiktok-sheets-writer") and click "Create and Continue".
  - Grant it the role of **Editor**, then click "Done".

c. **Get JSON Credentials**:

  - After creating the service account, find it in the credentials list and click on it.
  - Go to the "Keys" tab.
  - Click "Add Key" \> "Create new key".
  - Select **JSON** as the key type and click "Create".
  - A JSON file will be downloaded. **Rename this file to `credentials.json`** and place it in your project's root directory.

d. **Share Your Google Sheet**:

  - Open your `credentials.json` file and find the `client_email` address (it looks like `...gserviceaccount.com`).
  - Open your target Google Sheet.
  - Click the "Share" button in the top right.
  - Paste the `client_email` into the sharing dialog and give it **Editor** permissions.

### 4\. Configure TikTok Credentials

Create a file named `.env` in the project's root directory. This file will store your TikTok login details for the *first-time setup only*.

```
TIKTOK_EMAIL="your_tiktok_email@example.com"
TIKTOK_PASSWORD="your_tiktok_password"
```

### 5\. Configure the Main Script

Open the main script (e.g., `scraper.py`) and update the following variables inside the `main()` function if needed:

  - `SPREADSHEET_ID`: The ID of your Google Sheet. You can find it in the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`.
  - `SHEET_NAME`: The name of the specific sheet (tab) you want to write data to (e.g., `Sheet1`).

## Usage

The process involves two main steps.

### Step 1: Generate Cookies (First-Time Use Only)

To avoid logging in every time, you first need to run the login script to create a cookie file.

1.  Make sure your `.env` file is configured correctly.
2.  Run the login script from your terminal:
    ```sh
    python login_and_save_cookie.py
    ```
3.  The script will open Chrome, automatically fill in your credentials, and then pause.
4.  **You must manually solve the CAPTCHA** in the browser window to complete the login.
5.  Once you have logged in successfully, the script will save a `tiktok_cookie.pkl` file and close the browser.

### Step 2: Run the Scraper

Once the `tiktok_cookie.pkl` file exists, you can run the main scraper script as many times as you want.

1.  Run the main script from your terminal:

    ```sh
    python scraper.py
    ```

    *(Note: Rename your main script to `scraper.py` or use the correct filename).*

2.  When prompted, enter the TikTok channel names you want to scrape, separated by commas.

    ```
    Nhập tên các kênh TikTok (cách nhau bởi dấu phẩy): channel1,channel2,someotherchannel
    ```

3.  The script will now use the saved cookies to log in, scrape the data from the specified channels, and export it to your configured Google Sheet.

## Notes

  - This script's reliability depends on TikTok's website structure. If TikTok updates its site, the CSS selectors in the script may need to be updated.
  - Automating user accounts is against the terms of service of many platforms. Use this script responsibly and at your own risk.
  - If the script fails, ensure your `ChromeDriver` version exactly matches your Google Chrome browser version.
