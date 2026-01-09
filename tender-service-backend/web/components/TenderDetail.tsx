import React from 'react';
import { MOCK_TENDERS } from '../constants';
import { TenderStage } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { ArrowLeft, ExternalLink, FileText, Building2, Coins, Calendar, Trophy, AlertTriangle, Globe } from 'lucide-react';

interface TenderDetailProps {
  id: string;
  onBack: () => void;
}

const DetailItem: React.FC<{ label: string; value?: string | number; full?: boolean }> = ({ label, value, full }) => (
  <div className={`flex flex-col gap-2 ${full ? 'col-span-full' : ''}`}>
    <span className="text-sm font-semibold text-slate-500 uppercase tracking-wide">{label}</span>
    <span className="text-base font-medium text-slate-900 break-words leading-relaxed">{value || '-'}</span>
  </div>
);

const TenderDetail: React.FC<TenderDetailProps> = ({ id, onBack }) => {
  const tender = MOCK_TENDERS.find(t => t.id === id);

  if (!tender) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <p className="text-lg text-slate-500">未找到相关项目信息</p>
        <Button onClick={onBack}>返回列表</Button>
      </div>
    );
  }

  const formatMoney = (amount?: number) => {
    if (amount === undefined) return '-';
    return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY' }).format(amount);
  };

  const isFinished = tender.stage === TenderStage.RESULT || tender.stage === TenderStage.CANDIDATE;

  return (
    <div className="space-y-8 max-w-[1600px] mx-auto animate-fade-in">
      <div className="flex items-start gap-6 border-b border-slate-200 pb-6">
        <Button variant="outline" size="icon" className="mt-1" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1 space-y-3">
          <h1 className="text-3xl font-bold text-slate-900 leading-tight">{tender.projectName}</h1>
          <div className="flex flex-wrap items-center gap-4 text-base text-slate-500">
            <span className="bg-slate-100 px-3 py-1 rounded-md text-slate-700 font-medium">{tender.projectCode}</span>
            <span>•</span>
            <span className="font-medium">{tender.district}</span>
            <span>•</span>
            <span>{tender.publishTime} 发布</span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <Globe className="h-4 w-4" />
              {tender.sourcePlatform || '来源未知'}
            </span>
          </div>
        </div>
        <div className="flex gap-3">
           <a href={tender.sourceUrl} target="_blank" rel="noopener noreferrer">
            <Button variant="outline" size="lg">
              <ExternalLink className="mr-2 h-5 w-5" /> 查看原始公告
            </Button>
           </a>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left Column: Main Info */}
        <div className="xl:col-span-2 space-y-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-xl">
                <Building2 className="h-6 w-6 text-indigo-600" />
                业务信息
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <DetailItem label="建设单位 (招标人)" value={tender.builder} full />
                <DetailItem label="招标代理机构" value={tender.agency} full />
                <DetailItem label="项目类型" value={tender.projectType} />
                <DetailItem label="工期要求" value={tender.duration} />
                <DetailItem label="当前阶段" value={tender.stage} />
                <DetailItem label="信息来源" value={tender.sourcePlatform} />
              </div>
            </CardContent>
          </Card>

          {isFinished && (
            <Card className="border-indigo-100 bg-indigo-50/40">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl text-indigo-900">
                  <Trophy className="h-6 w-6 text-indigo-600" />
                  中标/成交信息
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <DetailItem label="中标单位" value={tender.winner} full />
                  <DetailItem label="中标金额" value={formatMoney(tender.winningAmount)} />
                  <DetailItem label="下浮率 / 优惠率" value={tender.winRate ? `${tender.winRate}%` : '-'} />
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
             <CardHeader>
              <CardTitle className="flex items-center gap-3 text-xl">
                <FileText className="h-6 w-6 text-slate-500" />
                备注 / 原始摘要
              </CardTitle>
            </CardHeader>
            <CardContent>
              {tender.remarks ? (
                 <div className="flex items-start gap-3 p-4 bg-amber-50 text-amber-900 rounded-lg border border-amber-100 text-base">
                   <AlertTriangle className="h-5 w-5 mt-0.5 shrink-0 text-amber-600" />
                   {tender.remarks}
                 </div>
              ) : (
                <p className="text-base text-slate-500">无特殊备注信息。</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Key Metrics */}
        <div className="space-y-8">
          <Card className="bg-slate-900 text-white border-slate-800 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-xl text-slate-100">
                <Coins className="h-6 w-6 text-emerald-400" />
                资金概览
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-8">
                <div>
                  <p className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">招标控制价 (预算)</p>
                  <p className="text-3xl font-bold tracking-tight text-white">{formatMoney(tender.budget)}</p>
                </div>
                {tender.winningAmount && (
                  <div>
                    <p className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">最终中标价</p>
                    <p className="text-3xl font-bold tracking-tight text-emerald-400">{formatMoney(tender.winningAmount)}</p>
                  </div>
                )}
                {tender.budget && tender.winningAmount && (
                   <div className="pt-6 border-t border-slate-700/50">
                     <p className="text-sm text-slate-400 mb-1">资金节约率</p>
                     <p className="text-xl font-medium text-emerald-400">
                       {((tender.budget - tender.winningAmount) / tender.budget * 100).toFixed(2)}%
                     </p>
                   </div>
                )}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-xl">
                <Calendar className="h-5 w-5 text-slate-500" />
                重要时间节点
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative border-l-2 border-slate-100 ml-3 space-y-8 pb-2">
                <div className="ml-6">
                  <div className="absolute -left-[9px] mt-1.5 h-4 w-4 rounded-full border-2 border-white bg-indigo-500 shadow-sm ring-2 ring-indigo-50"></div>
                  <p className="text-base font-bold text-slate-900">发布公告</p>
                  <p className="text-sm text-slate-500 mt-0.5">{tender.publishTime}</p>
                </div>
                <div className="ml-6">
                  <div className="absolute -left-[9px] mt-1.5 h-4 w-4 rounded-full border-2 border-white bg-slate-300 shadow-sm"></div>
                  <p className="text-base font-bold text-slate-900">开标时间</p>
                  <p className="text-sm text-slate-500 mt-0.5">待定 / 详见文件</p>
                </div>
                {isFinished && (
                  <div className="ml-6">
                    <div className="absolute -left-[9px] mt-1.5 h-4 w-4 rounded-full border-2 border-white bg-emerald-500 shadow-sm ring-2 ring-emerald-50"></div>
                    <p className="text-base font-bold text-slate-900">中标结果公示</p>
                    <p className="text-sm text-slate-500 mt-0.5">已完成</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TenderDetail;