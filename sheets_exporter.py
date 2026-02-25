import os
from typing import Tuple


def append_to_sheets(video: dict, credentials_path: str, spreadsheet_id: str) -> Tuple[bool, str]:
    """Append a single video as a new row. Adds headers automatically if the sheet is empty.
    Returns: (success, message)
    """
    try:
        import gspread
    except ImportError:
        return False, "Missing dependency: pip install gspread google-auth"

    if not os.path.exists(credentials_path):
        return False, f"Credentials file not found at: {credentials_path}"

    try:
        gc = gspread.service_account(filename=credentials_path)
        ws = gc.open_by_key(spreadsheet_id).sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        return False, "Spreadsheet not found. Check the ID and make sure the sheet is shared with the service account."
    except Exception as e:
        return False, f"Failed to connect to Google Sheets: {str(e)}"

    try:
        headers = ["Title", "Channel", "URL", "Date Added", "Summary", "Keywords"]
        if ws.cell(1, 1).value != headers[0]:
            ws.insert_row(headers, index=1)

        ws.append_row([
            video.get("title", ""),
            video.get("channel", ""),
            video.get("video_url", ""),
            video.get("date_added", "")[:10],
            video.get("summary", ""),
            video.get("keywords", ""),
        ], value_input_option="USER_ENTERED")
        return True, "Video appended to Google Sheets."
    except Exception as e:
        return False, f"Failed to write data: {str(e)}"


def export_to_sheets(videos: list, credentials_path: str, spreadsheet_id: str) -> Tuple[bool, str]:
    """Export all videos to the first sheet of a Google Spreadsheet.
    Clears the sheet and rewrites everything on each call (full sync).
    Returns: (success, message)
    """
    try:
        import gspread
    except ImportError:
        return False, "Missing dependency: pip install gspread google-auth"

    if not os.path.exists(credentials_path):
        return False, f"Credentials file not found at: {credentials_path}"

    try:
        gc = gspread.service_account(filename=credentials_path)
        sh = gc.open_by_key(spreadsheet_id)
        ws = sh.sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        return False, "Spreadsheet not found. Check the ID and make sure the sheet is shared with the service account."
    except Exception as e:
        return False, f"Failed to connect to Google Sheets: {str(e)}"

    try:
        headers = ["Title", "Channel", "URL", "Date Added", "Summary", "Keywords"]
        rows = [
            [
                video.get("title", ""),
                video.get("channel", ""),
                video.get("video_url", ""),
                video.get("date_added", "")[:10],
                video.get("summary", ""),
                video.get("keywords", ""),
            ]
            for video in videos
        ]

        ws.clear()
        ws.append_rows([headers] + rows, value_input_option="USER_ENTERED")

        return True, f"Exported {len(videos)} video(s) to Google Sheets."
    except Exception as e:
        return False, f"Failed to write data: {str(e)}"
