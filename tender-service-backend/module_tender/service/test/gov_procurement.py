import asyncio
import datetime
from module_tender.service.gov_procurement.tender_service import TenderService


async def test_get_ccgp_gov_project_list():
    """
    测试获取 CCGP 政府采购项目列表 (仅测试爬虫部分)
    """
    print("Testing get_ccgp_gov_project_list...")
    start_date = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # 直接调用基类的爬虫方法进行测试
    items = await TenderService.get_ccgp_gov_project_list(start_date, end_date)
    
    print(f"Fetched {len(items)} items.")
    if items:
        print("First item sample:")
        print(items[2])
        
        # 测试 parse_item_from_content
        print("\nTesting parse_item_from_content for the first item...")
        try:
            parsed = await TenderService.parse_item_from_content(items[2])
            print("Parsed result:")
            print(parsed)
        except Exception as e:
            print(f"Error parsing item: {e}")

    return items


if __name__ == '__main__':
    asyncio.run(test_get_ccgp_gov_project_list())
