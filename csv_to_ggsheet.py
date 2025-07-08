import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Optional

class ColumnConfig:
    """Cấu hình cột và kiểu dữ liệu."""
    COLUMNS = [
        'Kênh', 'Author', 'Followers', 'Text', 'Likes', 'Shares', 'Comments',
        'Collects', 'Duration(s)', 'Ngày tạo kênh', 'Ngày đăng', 'Hashtags',
        'URL Video', 'Views', 'followerCount', 'isAd'
    ]
    DTYPES = {
        'Kênh': str,
        'Author': str,
        'Followers': int,
        'Text': str,
        'Likes': int,
        'Shares': int,
        'Comments': int,
        'Collects': int,
        'Duration(s)': int,
        'Ngày tạo kênh': str,
        'Ngày đăng': str,
        'Hashtags': str,
        'URL Video': str,
        'Views': int,
        'followerCount': str,
        'isAd': str
    }

class CsvToGoogleSheetsApp:
    def __init__(
        self,
        credentials_file: str = './credentials.json',
        spreadsheet_id: Optional[str] = None,
        sheet_name: Optional[str] = None
    ):
        self._credentials_file = credentials_file
        self._spreadsheet_id = spreadsheet_id or os.getenv(
            'SPREADSHEET_ID', '17cnmrpZLq5f5nAzg_L9zC6ivpaG2CohavSDwC-PBLX8'
        )
        self._sheet_name = sheet_name or os.getenv('SHEET_NAME', 'tiktok_tháng7')
        self._scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self._service = None

    @property
    def service(self):
        """Khởi tạo và trả về Google Sheets service."""
        if self._service is None:
            self._init_service()
        return self._service

    def _init_service(self) -> None:
        """Khởi tạo Google Sheets API service."""
        try:
            creds = Credentials.from_service_account_file(
                self._credentials_file, scopes=self._scopes
            )
            self._service = build('sheets', 'v4', credentials=creds)
        except FileNotFoundError:
            raise FileNotFoundError(f"Không tìm thấy file credentials: {self._credentials_file}")
        except Exception as e:
            raise RuntimeError(f"Lỗi khi khởi tạo Sheets service: {e}")

    def _select_csv_files(self) -> List[str]:
        """Mở hộp thoại chọn file CSV."""
        try:
            root = tk.Tk()
            root.withdraw()
            file_paths = filedialog.askopenfilenames(
                title='Chọn các file CSV để gộp',
                filetypes=[('CSV files', '*.csv')]
            )
            return list(file_paths)
        except Exception as e:
            print(f"Lỗi khi chọn file: {e}")
            return []

    def _clean_value(self, value: str) -> str:
        """Làm sạch giá trị chuỗi để tránh lỗi JSON."""
        if isinstance(value, str):
            return value.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
        return value

    def _read_and_merge_csv(self, file_paths: List[str]) -> pd.DataFrame:
        """Đọc và gộp các file CSV."""
        dfs = []
        for fp in file_paths:
            try:
                df = pd.read_csv(fp)
                dfs.append(df)
            except Exception as e:
                print(f"Lỗi khi đọc '{fp}': {e}")
        
        if not dfs:
            print("Không có file CSV nào được đọc.")
            return pd.DataFrame()
        
        # Gộp DataFrame
        merged = pd.concat(dfs, ignore_index=True)
        
        # Thêm các cột thiếu
        for col in ColumnConfig.COLUMNS:
            if col not in merged.columns:
                merged[col] = None
        
        return merged

    def _cast_and_handle_null(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ép kiểu dữ liệu và thay giá trị trống bằng 'NULL'."""
        # Thay NaN/None bằng "NULL"
        df = df.fillna("NULL")
        
        # Ép kiểu dữ liệu
        for col, dtype in ColumnConfig.DTYPES.items():
            try:
                if dtype == str:
                    df[col] = df[col].astype(str).replace("nan", "NULL")
                    df[col] = df[col].apply(self._clean_value)
                elif dtype == int:
                    df[col] = df[col].apply(lambda x: int(x) if x != "NULL" else "NULL")
            except Exception as e:
                print(f"Lỗi khi ép kiểu cột {col}: {e}")
                df[col] = "NULL"
        
        return df

    def _create_sheet_if_not_exists(self) -> None:
        """Tạo sheet mới nếu chưa tồn tại."""
        try:
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self._spreadsheet_id).execute()
            sheets = [sheet['properties']['title'] for sheet in sheet_metadata.get('sheets', [])]
            if self._sheet_name not in sheets:
                body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': self._sheet_name
                            }
                        }
                    }]
                }
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self._spreadsheet_id,
                    body=body
                ).execute()
                print(f"Tạo sheet mới: {self._sheet_name}")
        except HttpError as err:
            print(f"Lỗi khi kiểm tra/tạo sheet: {err}")

    def _export_to_google_sheets(self, df: pd.DataFrame) -> None:
        """Xuất dữ liệu lên Google Sheets."""
        if df.empty:
            print("Không có dữ liệu để xuất lên Google Sheets.")
            return
        
        self._create_sheet_if_not_exists()
        sheet = self.service.spreadsheets()
        values = [df.columns.tolist()] + df.values.tolist()
        body = {'values': values}
        
        try:
            sheet.values().clear(
                spreadsheetId=self._spreadsheet_id,
                range=self._sheet_name
            ).execute()
            sheet.values().update(
                spreadsheetId=self._spreadsheet_id,
                range=f"{self._sheet_name}!A1",
                valueInputOption='RAW',
                body=body
            ).execute()
            print(f"Thành công: dữ liệu đã được lưu vào https://docs.google.com/spreadsheets/d/{self._spreadsheet_id}")
        except HttpError as err:
            print(f"Lỗi API Google Sheets: {err}")
            print("Dữ liệu gửi đi (5 dòng đầu):", values[:5])
        except Exception as e:
            print(f"Lỗi không xác định khi xuất dữ liệu: {e}")

    def run(self) -> None:
        """Chạy ứng dụng."""
        csv_paths = self._select_csv_files()
        if not csv_paths:
            print("Bạn chưa chọn file CSV nào.")
            return
        
        df = self._read_and_merge_csv(csv_paths)
        if df.empty:
            return
        
        df = self._cast_and_handle_null(df)
        print(f"Gộp {len(csv_paths)} file thành DataFrame với {len(df)} dòng.")
        print("Các kiểu dữ liệu:\n", df.dtypes)
        print("Mẫu dữ liệu đầu tiên:\n", df.head())
        
        self._export_to_google_sheets(df)

if __name__ == '__main__':
    try:
        app = CsvToGoogleSheetsApp()
        app.run()
    except Exception as e:
        print(f"Lỗi khi chạy ứng dụng: {e}")
