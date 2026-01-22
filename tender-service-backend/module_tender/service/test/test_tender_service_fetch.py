import asyncio
from unittest.mock import MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession
from module_tender.service.gov_procurement.tender_service import TenderService
from module_tender.entity.structured_entity.ccgp_gov_entity import CCGPGovEntity

async def test_fetch():
    print("Starting test_fetch...")
    
    # Mock DB session
    mock_db = MagicMock(spec=AsyncSession)
    f = asyncio.Future()
    f.set_result(None)
    mock_db.commit.return_value = f
    mock_db.rollback.return_value = f
    
    # Sample items
    sample_items = [
        {
            'project_url': 'http://example.com/1',
            'project_title': 'Test Project 1',
            'project_type': 'Test Type'
        }
    ]
    
    # Mock return for _extract_ai_data
    mock_ai_entity = CCGPGovEntity(
        projectCode="TC12345",
        district="Test District",
        projectType="Test Type",
        bidControlPrice=100.0,
        bidPrice=0.0,
        constructionScale="Scale",
        constructionContent="Content",
        tenderScope="Scope",
        constructionName="Construction Unit",
        agentName="Agency",
        duration="Duration",
        registrationDeadline="2023-01-01",
        winner_rank_1="",
        winner_rank_2="",
        winner_rank_3="",
        discountRate="",
        unitPrice=0.0
    )

    # Mock TenderService methods and TenderDao
    with patch('module_tender.service.gov_procurement.tender_service.TenderService.get_ccgp_gov_project_list', return_value=sample_items) as mock_get_list, \
         patch('module_tender.service.gov_procurement.tender_service.TenderService.get_html_detail_content', return_value="项目编号：TC12345\n项目名称：测试项目\n绿化工程") as mock_get_content, \
         patch('module_tender.service.gov_procurement.tender_service.TenderService._extract_ai_data', return_value=(mock_ai_entity, False)) as mock_ai, \
         patch('module_tender.dao.tender_dao.TenderDao.get_by_code_and_stage', return_value=None) as mock_dao_get, \
         patch('module_tender.dao.tender_dao.TenderDao.add_tender_dao') as mock_dao_add:
         
        mock_dao_add.side_effect = lambda db, tender: f

        print("Calling TenderService.fetch...")
        try:
            result = await TenderService.fetch(mock_db)
            print(f"Fetch completed. Result: {result}")
            
            print(f"get_ccgp_gov_project_list called: {mock_get_list.called}")
            print(f"get_html_detail_content called: {mock_get_content.called}")
            print(f"_extract_ai_data called: {mock_ai.called}")
            print(f"TenderDao.add_tender_dao called {mock_dao_add.call_count} times.")
            
        except Exception as e:
            print(f"Error during fetch: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_fetch())
