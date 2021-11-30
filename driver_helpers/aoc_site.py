"""Helpers related to interacting with the AOC website."""
import os
import sqlite3
from pathlib import Path
from typing import BinaryIO

import requests

INPUT_URL = "https://adventofcode.com/{year}/day/{day}/input"
COOKIE_HOST = ".adventofcode.com"
COOKIE_NAME = "session"


def get_firefox_session() -> str:
    """Steal a session cookie from the firefox sqlite database."""
    cookie_file = find_firefox_cookie_db_path()
    session = get_session_cookie_from_db(cookie_file)
    return session


def find_firefox_cookie_db_path() -> Path:
    """Find the path to the firefox cookie database."""
    app_data_path = Path(os.environ["APPDATA"])
    firefox_profiles = app_data_path / "Mozilla" / "Firefox" / "Profiles"

    cookie_candidates = [
        subfolder / "cookies.sqlite"
        for subfolder in firefox_profiles.iterdir()
        if (subfolder / "cookies.sqlite").is_file()
    ]

    match cookie_candidates:
        case [path]:
            return path
        case []:
            raise Exception("Failed to find Firefox profile")
        case _:
            raise Exception("Found multiple Firefox profiles")


def get_session_cookie_from_db(sqlite_file: Path) -> str:
    """Retrieve the session cookie from the firefox cookie database."""
    conn = sqlite3.connect(sqlite_file)
    try:
        cur = conn.cursor()
        for row in cur.execute(
            "SELECT value FROM moz_cookies WHERE name=? AND host=?",
            (COOKIE_NAME, COOKIE_HOST),
        ):
            return str(row[0])
        raise Exception("No session cookie found")
    finally:
        conn.close()


def download_problem_input(filelike: BinaryIO, year: int, day: int) -> str:
    """Download the input file for a problem."""
    session = get_firefox_session()
    resp = requests.get(INPUT_URL.format(year=year, day=day), cookies={"session": session})
    resp.raise_for_status()
    filelike.write(resp.content)
