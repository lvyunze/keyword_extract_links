class Tool:
    def __init__(self, url_address, browser_obj):
        self.url_address = url_address
        self.browser_obj = browser_obj

    async def create_page(self):
        page = await self.browser_obj.newPage()
        # 是否启用JS，enabled设为False，则无渲染效果
        await page.setJavaScriptEnabled(enabled=True)
        await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                         '{ webdriver:{ get: () => false } }) }')
        await page.goto(self.url_address)
        return page
