from pydantic import BaseModel, Field


class TenderPlanEntity(BaseModel):
    """招标计划字段提取"""
    district: str = Field(title="所属区县",
                          description="从如下区县中提取项目所属区县，有：东城区、西城区、朝阳区、丰台区、石景山区、海淀区、顺义区、通州区、大兴区、房山区、门头沟区、昌平区、平谷区、密云区、怀柔区、延庆区")
    projectType: str = Field(title="项目类型",
                             description="该项目的类型，有如下类型如：工程、监理、诊疗、设计、养护、租摆、有害生物防治、劳务等")