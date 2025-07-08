# TikTok Scraper Project

This project is designed to scrape TikTok data using Selenium, extract video and channel details, save them into CSV files, and upload them to Google Sheets for reporting. This script uses cookies to automatically log into TikTok and bypass CAPTCHA verification. You can also use the exported data for Looker Studio reports.

## Workflow

![Workflow](https://github.com/kina2711/scrape_tiktok/blob/main/Workflow.png)

### Steps:
1. **Load Cookies**: The cookies from `tiktok_cookie.pkl` are used to log into TikTok automatically.
2. **Initialize Browser**: The Chrome browser is initialized with settings to prevent automation detection.
3. **Login to TikTok**: The cookies are set into the browser and the TikTok homepage is refreshed to log in.
4. **Scroll to Load Videos**: The page is scrolled to load all the videos (up to 20 times).
5. **Get Channel Information**: Extracts follower count, total likes, total videos, and video URLs from the TikTok channel.
6. **Extract Video Details**: Extracts author, description, likes, shares, comments, duration, hashtags, and ad status for each video.
7. **Collect Data**: Data is collected for each video across all specified channels.
8. **Export to CSV**: Data is exported into a CSV file named after the channels.
9. **Merge and Clean CSV**: Select and merge CSV files, handle missing values and cast data types.
10. **Export to Google Sheets**: After processing, data is uploaded to Google Sheets.
11. **Connect to Looker Studio**: Link the Google Sheets to Looker Studio for reporting.

---

## Requirements

You can install all necessary dependencies via `requirements.txt`:

```bash
pip install -r requirements.txt
````

---

## Files and Functions

1. **`save_cookie.py`**: Logs in to TikTok using provided credentials and saves cookies for later use.
2. **`crawl_tiktok.py`**: Scrapes TikTok channel data, including video and channel statistics.
3. **`csv_to_ggsheet.py`**: Converts CSV data to Google Sheets, allowing for easier access and reporting.

---

## How to Use

### Step 1: Setup

1. Clone the repository to your local machine.

   ```bash
   git clone https://github.com/kina2711/scrape_tiktok.git
   cd scrape_tiktok
   ```

2. Set up environment variables in the `.env` file for TikTok login (email and password).

   Create a file named `.env` in the root directory of your project and add your TikTok credentials:

   ```
   TIKTOK_EMAIL="your_tiktok_email@example.com"
   TIKTOK_PASSWORD="your_tiktok_password"
   ```

3. Run `save_cookie.py` to log in and save the cookies.

   ```bash
   python save_cookie.py
   ```

   This will log you in to TikTok and save the login cookies in `tiktok_cookie.pkl` so that you don't need to log in again.

---

### Step 2: Scrape TikTok Data

1. Run `crawl_tiktok.py` to scrape video data from your specified TikTok channels.

   ```bash
   python crawl_tiktok.py
   ```

   * When prompted, enter the TikTok channel names you want to scrape, separated by commas.

   ```
   Enter the TikTok channel names (separate by commas): channel1, channel2, channel3
   ```

2. The scraped data will be saved in a CSV file located in the `./data` directory.

---

### Step 3: Export to Google Sheets

1. Run `csv_to_ggsheet.py` to import the CSV files and upload them to Google Sheets.

   ```bash
   python csv_to_ggsheet.py
   ```

2. The exported data will be available for further reporting and analysis in your Google Sheet.

---

## Dashboard

### Live Dashboard Report
View comprehensive TikTok channel performance analytics:

**🔗 [TikTok Platform Analytics Dashboard](https://lookerstudio.google.com/reporting/bf18bd16-9ac8-4119-aa9a-d14269054b81)**

![Dashboard Preview](https://github.com/kina2711/scrape_tiktok/blob/main/Dashboard_preview.png)
*Real-time TikTok analytics dashboard showing key performance metrics*

### 📈 Dashboard Overview

**Key Metrics Tracked:**
- **📊 Total Views**: 44,507,044+ across all monitored channels
- **👥 Total Followers**: 27,397+ combined follower base
- **📺 Video Count**: 181 videos analyzed
- **📥 Downloads**: 8,332 data points collected
- **💬 Engagement**: 108,478 total interactions

### 📋 Dashboard Sections

#### 1. **Performance Overview**
- Real-time view counts and engagement metrics
- Top performing channels comparison
- Daily/weekly growth tracking

#### 2. **Channel Analysis Tables**
- Individual channel performance breakdown
- Follower growth rates
- Engagement ratios per channel
- Content frequency analysis

#### 3. **View Distribution Charts**
- **Views by Channel**: Horizontal bar chart showing view distribution
- **Follower Growth**: Time-series analysis of follower acquisition
- **Engagement Trends**: Like and interaction patterns over time

#### 4. **Interactive Filters**
- **Date Range**: Customizable time period selection
- **Channel Filter**: Focus on specific TikTok accounts
- **Metric Selection**: Toggle between views, likes, followers

### 🎯 Key Features

- **📊 Multi-Channel Tracking**: Monitor multiple TikTok accounts simultaneously
- **📈 Growth Visualization**: Clear charts showing performance trends
- **🔄 Auto-Refresh**: Data updates every 6 hours from crawling scripts
- **📱 Mobile Responsive**: Accessible on all devices
- **📤 Export Options**: Download reports in multiple formats

### 📅 Data Coverage
- **Reporting Period**: Jun 1, 2025 - Jun 30, 2025 (customizable)
- **Update Frequency**: Every 6 hours via automated crawling
- **Data Sources**: Direct TikTok channel scraping
- **Metrics Retention**: 90-day historical data

### 🚀 How to Use

1. **Access**: Click the dashboard link above
2. **Navigate**: Use the sidebar filters to customize your view
3. **Analyze**: Compare channel performance using the tables and charts
4. **Export**: Download specific reports or share insights with your team
5. **Monitor**: Track growth trends and identify top-performing content

### 📊 Current Statistics
- **Channels Monitored**: 10+ active TikTok accounts
- **Total Video Analysis**: 181 videos and counting
- **Data Points Collected**: 8,332+ individual metrics
- **Combined Reach**: 44.5M+ total views tracked
- **Last Updated**: Real-time sync with 15-minute delay

---

### 🔧 Technical Details
- **Platform**: Google Looker Studio
- **Data Source**: Automated Python crawling scripts
- **Refresh Rate**: Every 6 hours
- **Visualization**: Interactive charts and responsive tables
- **Access**: Public dashboard (no login required)

---

### Notes

  - This script's reliability depends on TikTok's website structure. If TikTok updates its site, the CSS selectors in the script may need to be updated.
  - Automating user accounts is against the terms of service of many platforms. Use this script responsibly and at your own risk.
  - If the script fails, ensure your `ChromeDriver` version exactly matches your Google Chrome browser version.
