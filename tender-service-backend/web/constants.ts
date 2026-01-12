import { Tender, TenderStage, DistrictStat, StageStat, TrendStat } from './types';

export const DISTRICTS = [
  '朝阳区', '海淀区', '通州区', '丰台区', '大兴区', '西城区', '东城区', '昌平区'
];

export const STAGES = Object.values(TenderStage);

export const PROJECT_TYPES = [
  '工程', '监理', '诊疗', '设计', '养护', '租摆', '有害生物防治', '劳务'
];

// Helper to generate random date within last 30 days
const getRandomDate = () => {
  const date = new Date();
  date.setDate(date.getDate() - Math.floor(Math.random() * 30));
  return date.toISOString().split('T')[0];
};

export const MOCK_TENDERS: Tender[] = Array.from({ length: 50 }).map((_, i) => {
  const stage = STAGES[Math.floor(Math.random() * STAGES.length)];
  const isFinished = stage === TenderStage.RESULT || stage === TenderStage.CANDIDATE;
  
  return {
    id: `T${10000 + i}`,
    projectCode: `ZB-2024-${String(i + 1).padStart(3, '0')}`,
    projectName: `2024年${DISTRICTS[Math.floor(Math.random() * DISTRICTS.length)]}某${['老旧小区改造', '智慧城市建设', '绿化养护服务', '办公设备采购', '道路维修工程'][Math.floor(Math.random() * 5)]}项目`,
    district: DISTRICTS[Math.floor(Math.random() * DISTRICTS.length)],
    builder: '某某城市建设投资有限公司',
    agency: '某某招标代理有限公司',
    stage: stage,
    publishTime: getRandomDate(),
    projectType: PROJECT_TYPES[Math.floor(Math.random() * PROJECT_TYPES.length)],
    budget: Math.floor(Math.random() * 10000000) + 500000,
    winningAmount: isFinished ? Math.floor(Math.random() * 9000000) + 400000 : undefined,
    winner: isFinished ? '某某建筑工程有限公司' : undefined,
    winRate: isFinished ? Number((Math.random() * 5).toFixed(2)) : undefined,
    duration: '180日历天',
    sourceUrl: 'https://example.com/tender/detail',
    sourcePlatform: ['北京市公共资源交易服务平台', '中国招标投标公共服务平台', '北京市政府采购网'][Math.floor(Math.random() * 3)],
    remarks: Math.random() > 0.8 ? '该数据字段部分缺失，请核对原始网页' : undefined
  };
});

// Mock Stats Data
export const DISTRICT_STATS: DistrictStat[] = DISTRICTS.map(d => ({
  name: d,
  value: Math.floor(Math.random() * 100) + 10
}));

export const STAGE_STATS: StageStat[] = STAGES.map(s => ({
  name: s,
  value: Math.floor(Math.random() * 200) + 20
}));

export const TREND_STATS: TrendStat[] = Array.from({ length: 30 }).map((_, i) => {
  const d = new Date();
  d.setDate(d.getDate() - (29 - i));
  return {
    date: `${d.getMonth() + 1}/${d.getDate()}`,
    count: Math.floor(Math.random() * 20) + 5
  };
});
