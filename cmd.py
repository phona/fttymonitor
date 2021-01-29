import asyncio
from argparse import ArgumentParser
from datetime import date, datetime, timedelta

from playwright.async_api import async_playwright
from monitor.operation import login, new_browser, new_driver, schedule


def timestr_to_timedelta(timestr: str):
    dt = datetime.strptime(timestr, "%H:%M")
    return timedelta(hours=dt.hour, minutes=dt.minute)


def main():
    parser = ArgumentParser(description="Process some integers.")
    parser.add_argument("--username", "-u", required=True, type=str)
    parser.add_argument("--password", "-p", required=True, type=str)

    mxg = parser.add_mutually_exclusive_group(required=True)
    mxg.add_argument("--court-num", "-n", type=int)
    mxg.add_argument("--court-name", "-N", type=str)

    parser.add_argument(
        "--date",
        "-d",
        default=date.today(),
        type=lambda datestring: datetime.strptime(datestring, "%Y-%m-%d").date(),
    )
    parser.add_argument(
        "--start-time",
        "-s",
        required=True,
        type=timestr_to_timedelta,
    )
    parser.add_argument(
        "--end-time",
        "-e",
        required=True,
        type=timestr_to_timedelta,
    )
    args = parser.parse_args()

    async def _():
        async with async_playwright() as p:
            browser = await new_browser(False, p.chromium)
            driver = await new_driver(browser)
            try:
                await login(driver, args.username, args.password)
                court_num_or_name = args.court_name or args.court_num
                tss = await schedule(
                    driver,
                    court_num_or_name,
                    args.date,
                    args.start_time,
                    args.end_time,
                )

            finally:
                await driver.screenshot(path="test.png", type="png")
                await driver.close()

    asyncio.get_event_loop().run_until_complete(_())


if __name__ == "__main__":
    main()
