from pydantic import BaseModel, Field

class GovTenderNoticeEntity(BaseModel):
    """政府采购网站招标公告字段提取"""

    projectType: str = Field(title="项目类型",
                             description="该项目的类型，有如下类型如：工程、监理、诊疗、设计、养护、租摆、有害生物防治、劳务等")
    district: str = Field(title="所属区县",
                          description="从如下区县中提取项目所属区县，东城区、西城区、朝阳区、丰台区、石景山区、海淀区、顺义区、通州区、大兴区、房山区、门头沟区、昌平区、平谷区、密云区、怀柔区、延庆区")
    bidControlPrice: float = Field(title="招标控制价",
                                   description="招标控制价,最高的投标限价或计划的投资总额。如价格单位不是万元，请你将其价格该为万元为单位，例如：1661300元，输出 166.13")
    constructionScale: str = Field(title="建设规模", description="建设规模")
    tenderScope: str = Field(title="招标范围", description="招标范围")
    constructionName: str = Field(title="招标人/采购人名称", description="招标人/采购人名称")
    agentName:str = Field(title="代理机构名称", description="代理机构名称")
    constructionContent: str = Field(title="施工内容", description="施工内容")
    duration: str = Field(title="工期", description="工期，以日历天为单位")
    registrationDeadline: str = Field(title="报名截止时间",
                                      description="该截止时间为获取文件的截止时间，如：时间：2026-01-06 至 2026-01-12 ，每天上午09:00至12:00，下午12:00至16:00（北京时间，法定节假日除外），截止时间则为：2026年01月12日16时00分")
