import asyncio
import random
import pandas as pd
from playwright.async_api import async_playwright

SEARCH_URL = (
    "https://www.104.com.tw/jobs/search/?"
    "area=6001002021,6001002024,6001002025,6001002022,6001001001,6001001006,6001001002"
    "&jobexp=1"
    "&keyword=前端工程師%20UI%20Flutter"
    "&mode=s&order=15"
)

TARGET_PAGES = 3  # 點進內頁耗時較長，建議先跑 2~3 頁測試

EXCLUDE_KEYWORDS = [
    "設備", "製程", "機構", "廠務", "半導體", "模具", "CNC",
    "自動控制", "電路", "硬體", "地質", "環境工程", "專利師"
]

async def random_sleep(min_sec=1.5, max_sec=3.0):
    """擬人隨機停頓"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def run_crawler():
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            no_viewport=True
        )
        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        for page_idx in range(1, TARGET_PAGES + 1):
            url = f"{SEARCH_URL}&page={page_idx}"
            print(f"\n======================================")
            print(f"[進度] 正在抓取第 {page_idx} / {TARGET_PAGES} 頁列表...")
            print(f"======================================")

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)

                # 偵測 Cloudflare 驗證畫面
                if "安全驗證" in await page.title() or await page.query_selector("iframe[src*='cloudflare']"):
                    print("⚠️ 偵測到安全驗證，請在瀏覽器畫面上手動勾選通過...")
                    for _ in range(30):
                        await asyncio.sleep(1)
                        if "安全驗證" not in await page.title():
                            break

                await random_sleep(2.5, 4.0)

                # 滾動畫面載入職缺
                for _ in range(3):
                    await page.mouse.wheel(0, random.randint(500, 700))
                    await random_sleep(0.7, 1.2)

                await page.wait_for_selector("div.job-summary, article.b-block--top-bord", timeout=15000)
                cards = await page.query_selector_all("div.job-summary, article.b-block--top-bord")
                print(f"-> 第 {page_idx} 頁取得 {len(cards)} 筆候選職缺")

                # 先從列表擷取基本連結與標題
                page_jobs = []
                for card in cards:
                    title_elem = await card.query_selector("h2 a, a.js-job-link")
                    if not title_elem:
                        continue
                    
                    title = (await title_elem.inner_text()).strip()
                    if any(bad in title for bad in EXCLUDE_KEYWORDS):
                        continue

                    raw_link = await title_elem.get_attribute("href") or ""
                    link = f"https:{raw_link}" if raw_link.startswith("//") else raw_link
                    link = link.split("?")[0]

                    comp_elem = await card.query_selector("a.info-company__text, a.b-link--muted")
                    company = (await comp_elem.inner_text()).strip() if comp_elem else "未知公司"

                    page_jobs.append({"職缺名稱": title, "公司名稱": company, "職缺連結": link})

                # 開新分頁逐筆進入內頁抓取完整內容
                detail_page = await context.new_page()
                for idx, job in enumerate(page_jobs, start=1):
                    print(f"  [{idx}/{len(page_jobs)}] 深入抓取內頁: {job['公司名稱']} - {job['職缺名稱']}")
                    try:
                        await detail_page.goto(job["職缺連結"], wait_until="domcontentloaded", timeout=30000)
                        await random_sleep(1.8, 3.2)

                        # 1. 工作內容完整全文
                        desc_elem = await detail_page.query_selector("p.job-description__content, div.job-description-table")
                        full_desc = (await desc_elem.inner_text()).strip() if desc_elem else ""

                        # 2. 條件要求（經歷、學歷、科系、語文）
                        req_elem = await detail_page.query_selector("div.job-requirement")
                        requirements = (await req_elem.inner_text()).strip() if req_elem else ""

                        # 3. 擅長工具與技能
                        tool_elem = await detail_page.query_selector("div.job-requirement-content")
                        tools = (await tool_elem.inner_text()).strip() if tool_elem else ""

                        # 4. 工作待遇
                        salary_elem = await detail_page.query_selector("p.text-primary, span.job-header__salary")
                        salary = (await salary_elem.inner_text()).strip() if salary_elem else "待遇面議"

                        # 5. 上班地點
                        loc_elem = await detail_page.query_selector("a[data-gtm-joblist*='地區'], div.job-address")
                        location = (await loc_elem.inner_text()).strip() if loc_elem else ""

                        results.append({
                            "公司名稱": job["公司名稱"],
                            "職缺名稱": job["職缺名稱"],
                            "工作地點": location,
                            "薪資待遇": salary,
                            "完整工作內容": full_desc,
                            "條件要求(學歷/科系/經歷)": requirements,
                            "擅長工具與技能": tools,
                            "職缺連結": job["職缺連結"]
                        })

                        # 內頁之間停頓 2 ~ 3.5 秒，避免觸發高頻防爬阻擋
                        await random_sleep(2.0, 3.5)

                    except Exception as e:
                        print(f"    -> 內頁解析失敗: {e}")
                        continue

                await detail_page.close()

                # 換頁等待 4 ~ 6 秒
                await random_sleep(4.0, 6.0)

            except Exception as err:
                print(f"第 {page_idx} 頁抓取遇到狀況: {err}")
                continue

        await browser.close()

    if results:
        df = pd.DataFrame(results)
        df.drop_duplicates(subset=["職缺連結"], inplace=True)
        csv_file = "104_完整條件職缺清單.csv"
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        print(f"\n全部爬取完成！共收集 {len(df)} 筆「含完整條件」職缺，已輸出至 {csv_file}")
    else:
        print("\n未能取得職缺資料。")

if __name__ == "__main__":
    asyncio.run(run_crawler())