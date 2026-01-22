from pydantic import BaseModel, Field

class CCGPGovEntity(BaseModel):
    """政府采购网站字段提取"""
    district: str = Field(title="所属区县",
                          description="从如下区县中提取项目所属区县，东城区、西城区、朝阳区、丰台区、石景山区、海淀区、顺义区、通州区、大兴区、房山区、门头沟区、昌平区、平谷区、密云区、怀柔区、延庆区")
    projectType: str = Field(title="项目类型",
                             description="该项目的类型，有如下类型如：工程、监理、诊疗、设计、养护、租摆、有害生物防治、劳务等")
    bidControlPrice: float = Field(title="招标控制价",
                                   description="招标控制价,最高的投标限价或计划的投资总额。如价格单位不是万元，请你将其价格该为万元为单位，例如：1661300元，输出 166.13")
    bidPrice: float = Field(title="中标价格",
                            description="中标价格。如价格单位不是万元，请你将其价格该为万元为单位，例如：10699900.81元，输出 1069.990081")
    constructionScale: str = Field(title="建设规模", description="建设规模")
    constructionContent: str = Field(title="施工内容", description="施工内容")
    tenderScope: str = Field(title="招标范围", description="招标范围")

    agentName: str = Field(title="代理机构名称", description="代理机构名称")
    duration: str = Field(title="工期", description="工期")
    registrationDeadline: str = Field(title="获取文件的最后时间",
                                      description="最后获取采购文件/招标文件的时间。如：时间：2026-01-06 至 2026-01-12 ，每天上午09:00至12:00，下午12:00至16:00（北京时间，法定节假日除外），时间则为：2026年01月12日16时00分, 注意：该项只对招标公告生效，其他公告则输出null")

    winner_rank_1: str = Field(title="中标排名第一名", description="中标候选人第一名的单位名称")
    winner_rank_2: str = Field(title="中标排名第二名", description="中标候选人第二名的单位名称")
    winner_rank_3: str = Field(title="中标排名第三名", description="中标候选人第三名的单位名称")
    discountRate: str = Field(title="中标下浮率",
                              description="中标下浮率，即中标价与招标控制价的差值除以招标控制价，如：0.05，输出 5.0%")
    unitPrice: float = Field(title="单方造价",
                             description="单方造价，指建设面积的单方造价（单位：万元/㎡或万元/项）")