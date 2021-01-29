import asyncio
from datetime import date, datetime, timedelta
from typing import Callable, Iterable, TypeVar, Union

from playwright.async_api import Browser, ElementHandle, Page, BrowserType

_T = TypeVar("_T")


class Driver:
    def __init__(self, driver: Page):
        self.driver = driver

    async def click(self, xpath: str):
        await self.driver.wait_for_selector(f"xpath={xpath}", state="attached")
        btn = await self.driver.query_selector(f"xpath={xpath}")
        await btn.click()

    async def wait_and_select(self, xpath: str):
        await self.driver.wait_for_selector(f"xpath={xpath}")
        return await self.driver.query_selector(f"xpath={xpath}")

    async def wait_and_select_all(self, xpath: str):
        await self.driver.wait_for_selector(f"xpath={xpath}")
        return await self.driver.query_selector_all(f"xpath={xpath}")

    async def close(self):
        await self.driver.close()


class Date:
    def __init__(self, driver: Driver, date: date, text: str):
        self.driver = driver
        self.date = date
        self.text = text

    async def _get_courts(self):
        elem = await self.driver.wait_and_select(
            '//*[@id="skin-app"]/section/div[3]/div[2]/table/thead/tr[1]'
        )
        divs = await elem.query_selector_all("div")
        return [
            Court(self.driver, await div.inner_text(), self.date, i + 1)
            for i, div in enumerate(divs)
        ]

    async def get_court(self, court_num_or_name: Union[int, str]):
        if isinstance(court_num_or_name, int):
            return find(
                await self._get_courts(), lambda x: x.index == court_num_or_name
            )
        return find(await self._get_courts(), lambda x: x.name == court_num_or_name)

    def __str__(self) -> str:
        return str(self.date)


class Court:
    def __init__(self, driver: Driver, text: str, date: date, index: int):
        assert index > 0
        self.driver = driver
        self.index = index
        self.name = text
        self.date = date

    async def _get_time_sections(self):
        tbody = await self.driver.wait_and_select(
            '//*[@id="skin-app"]/section/div[3]/div[3]/table/tbody'
        )
        # :(
        await asyncio.sleep(0.5)
        elems = await tbody.query_selector_all(f".schedule-table_column_{self.index}")
        return [TimeSection(elem, self.date) for elem in elems]

    async def schedual(self, start: datetime, end: datetime):
        for ts in await self._get_time_sections():
            ts_start, ts_end = await ts.range()
            if start <= ts_start and ts_end <= end:
                print("schedual", ts_start, "-", ts_end)
                await ts.schedual()

    def __str__(self) -> str:
        return self.name


class TimeSection:
    def __init__(self, elem: ElementHandle, date: date):
        self.elem = elem
        self.date = date

    async def range(self):
        div = await self.elem.query_selector("div")
        timestr, msg = (await div.inner_text()).split("\n", 1)
        self.msg = msg
        bound = [datetime.strptime(t, "%H:%M") for t in timestr.split("-")]
        return datetime.combine(self.date, bound[0].time()), datetime.combine(
            self.date, bound[1].time()
        )

    async def schedual(self):
        klass = await self.elem.get_attribute("class") or ""
        if "selected" in klass:
            return

        await self.elem.click()


def date_to_datetime(d: date):
    return datetime.combine(d, datetime.min.time())


async def schedule(
    page: Page,
    court_num_or_name: Union[int, str],
    date: date,
    start: timedelta,
    end: timedelta,
):
    await page.goto("https://ftty.ydmap.cn/venue/101333")
    driver = Driver(page)
    await driver.click('//*[@id="skin-app"]/section/div[5]/div/div/a/button')
    d = await select_date(driver, date)
    court = await d.get_court(court_num_or_name)
    await court.schedual(date_to_datetime(date) + start, date_to_datetime(date) + end)
    await driver.click('//*[@id="skin-app"]/section/div[4]/div[2]/button')
    await driver.driver.set_viewport_size({"height": 10000, "width": 1920})
    await driver.click("/html/body/div[2]/div/div[3]/button[2]")
    await driver.driver.set_viewport_size({"height": 1280, "width": 1920})
    await driver.click('//*[@id="skin-app"]/div/section/div[2]/div[2]/button')
    await driver.wait_and_select(
        '//*[@id="skin-app"]/section/div/div[2]/div[1]/div[1]/div/div/button'
    )


async def login(page: Page, name: str, password: str):
    await page.goto("https://ftty.ydmap.cn/user/login")
    driver = Driver(page)
    elem = await driver.wait_and_select(
        '//*[@id="skin-app"]/div/section/form/div[1]/div/div[1]/input'
    )
    await elem.type(name)
    elem = await driver.wait_and_select(
        '//*[@id="skin-app"]/div/section/form/div[2]/div/div/input'
    )
    await elem.type(password)
    await driver.click('//*[@id="skin-app"]/div/section/section/button')
    slider = await driver.wait_and_select('//*[@id="nc_1_n1z"]')

    rect = await slider.bounding_box()
    await page.mouse.move(rect["x"], rect["y"])
    await page.mouse.down()
    await page.mouse.move(rect["x"] + 500, rect["y"])
    await driver.wait_and_select(
        '//*[@id="skin-app"]/section/section/div[3]/div/div/div[1]/img'
    )


async def new_browser(debug: bool, browser_type: BrowserType):
    browser = await browser_type.launch(
        executable_path="/usr/bin/google-chrome",
        args=[
            "--disable-blink-features",
            "--disable-blink-features=AutomationControlled",
        ],
        headless=not debug,
    )
    ctx = await browser.new_context(no_viewport=True)
    await ctx.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', {
            value: undefined,
            configurable: true
        })
    """
    )
    return ctx.browser


async def new_driver(browser: Browser):
    page = await browser.new_page()
    await page.set_viewport_size({"width": 1920, "height": 1280})
    await page.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', {
            value: undefined,
            configurable: true
        })
    """
    )
    return page


async def select_date(driver: Driver, d: date):
    elems = await driver.wait_and_select_all(
        '//*[@id="skin-app"]/section/div[2]/div[2]/div/ul/li'
    )
    for elem in elems:
        divs = await elem.query_selector_all("div")
        schedulable_date = datetime.strptime(await divs[0].inner_text(), "%Y-%m-%d")
        if datetime.combine(d, datetime.min.time()) == schedulable_date:
            await elem.click()
            return Date(driver, d, await divs[1].inner_text())

    raise KeyError(f"date {d} not found")


def find(iter: Iterable[_T], func: Callable[[_T], bool]) -> _T:
    for item in iter:
        if func(item):
            return item
    raise ValueError("not found valid item in iterable")
