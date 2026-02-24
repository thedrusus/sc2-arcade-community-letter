import json
import os
import re

import gspread
from google.oauth2.service_account import Credentials

README_PATH = "README.md"

DEV_CELL = "B2"
PLAY_CELL = "B3"
PLAYER_CELL = "B4"
SUMMARY_TAB = "Summary"

def replace_between_markers(text: str, marker: str, new_value: str) -> str:
    # Replaces content between <!--MARKER--> ... <!--/MARKER-->
    pattern = rf"(<!--{marker}-->)(.*?)(<!--/{marker}-->)"
    if not re.search(pattern, text, flags=re.DOTALL):
        raise RuntimeError(f"Marker {marker} not found in README.")
    return re.sub(pattern, rf"\1{new_value}\3", text, flags=re.DOTALL)

def main():
    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    sa_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]

    creds_info = json.loads(sa_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)

    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(SUMMARY_TAB)

    dev_count = str(ws.acell(DEV_CELL).value).strip()
    play_count = str(ws.acell(PLAY_CELL).value).strip()
    player_count = str(ws.acell(PLAYER_CELL).value).strip()

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    updated = readme
    updated = replace_between_markers(updated, "DEV_COUNT", dev_count)
    updated = replace_between_markers(updated, "PLAY_COUNT", play_count)
    updated = replace_between_markers(updated, "PLAYER_COUNT", player_count)

    if updated != readme:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated)
        print("README updated.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    main()
