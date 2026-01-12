export type ViewState = 'dashboard' | 'list' | 'detail' | 'settings' | 'subscription';

export enum TenderStage {
  ANNOUNCEMENT = '招标公告',
  CANDIDATE = '中标候选人',
  RESULT = '中标结果',
  FAILURE = '流标/废标',
  CHANGE = '变更公告'
}

export interface Tender {
  id: string;
  projectCode: string;
  projectName: string;
  district: string;
  builder: string; // 建设单位
  agency: string; // 代理机构
  stage: TenderStage;
  publishTime: string; // ISO Date string
  projectType: string; // 工程、服务、货物
  budget: number; // 招标控制价
  winningAmount?: number; // 中标价
  winner?: string; // 中标人
  winRate?: number; // 下浮率
  duration?: string; // 工期
  sourceUrl?: string; // 原始链接
  sourcePlatform?: string; // 信息来源平台
  remarks?: string;
}

export interface FilterParams {
  keyword: string;
  projectCode: string;
  district: string;
  stage: string;
  projectType: string;
  startDate: string;
  endDate: string;
}

// Stats Types
export interface DistrictStat {
  name: string;
  value: number;
  [key: string]: any;
}

export interface StageStat {
  name: string;
  value: number;
  [key: string]: any;
}

export interface TrendStat {
  date: string;
  count: number;
  [key: string]: any;
}