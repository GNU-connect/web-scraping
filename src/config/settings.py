ACADEMIC_CALENDAR_URL = 'https://www.gnu.ac.kr/main/ps/schdul/selectSchdulMainList.do?mi='

_chrome_driver_path = None


def get_chrome_driver_path() -> str:
    global _chrome_driver_path
    if _chrome_driver_path is None:
        from webdriver_manager.chrome import ChromeDriverManager
        _chrome_driver_path = ChromeDriverManager().install()
    return _chrome_driver_path
