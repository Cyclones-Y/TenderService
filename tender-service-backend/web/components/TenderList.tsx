import React, { useEffect, useState } from 'react';
import { DISTRICTS, STAGES } from '../constants';
import { FilterParams, TenderStage } from '../types';
import { Card, CardContent } from './ui/Card';
import { Input, Select } from './ui/Input';
import { Button } from './ui/Button';
import { Search, RotateCcw, Download, Eye, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react';
import { getApiUrl } from '../utils/api';

interface TenderListProps {
  onViewDetail: (id: string) => void;
}

type TenderListRow = {
  tenderId: number;
  projectCode?: string;
  projectName?: string;
  district?: string;
  constructionUnit?: string;
  projectStage?: string;
  releaseTime?: string;
};

type PageResponse<T> = {
  code: number;
  msg: string;
  success: boolean;
  time: string;
  rows: T[];
  pageNum: number;
  pageSize: number;
  total: number;
  hasNext: boolean;
};

const TenderList: React.FC<TenderListProps> = ({ onViewDetail }) => {
  const [filters, setFilters] = useState<FilterParams>({
    keyword: '',
    projectCode: '',
    district: '',
    stage: '',
    startDate: '',
    endDate: ''
  });

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10
  });

  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [rows, setRows] = useState<TenderListRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [errorText, setErrorText] = useState<string | null>(null);

  const totalPages = Math.ceil(total / pagination.pageSize);
  const currentData = rows;

  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return;
    setPagination(prev => ({ ...prev, current: page }));
    void fetchTenderList({ nextPage: page, nextPageSize: pagination.pageSize });
  };

  const handleReset = () => {
    setFilters({
      keyword: '',
      projectCode: '',
      district: '',
      stage: '',
      startDate: '',
      endDate: ''
    });
    setPagination({ current: 1, pageSize: pagination.pageSize });
    setSelectedIds(new Set());
    void fetchTenderList({ nextPage: 1, nextPageSize: pagination.pageSize, nextFilters: {
      keyword: '',
      projectCode: '',
      district: '',
      stage: '',
      startDate: '',
      endDate: ''
    }});
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(new Set(currentData.map(d => d.tenderId)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectRow = (id: number) => {
    const newSet = new Set(selectedIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedIds(newSet);
  };

  const buildQueryParams = (p: { pageNum: number; pageSize: number; f: FilterParams }) => {
    const params = new URLSearchParams();
    params.set('page_num', String(p.pageNum));
    params.set('page_size', String(p.pageSize));
    if (p.f.keyword) params.set('project_name', p.f.keyword);
    if (p.f.projectCode) params.set('project_code', p.f.projectCode);
    if (p.f.district) params.set('district', p.f.district);
    if (p.f.stage) params.set('project_stage', p.f.stage);
    if (p.f.startDate) params.set('begin_time', p.f.startDate);
    if (p.f.endDate) params.set('end_time', p.f.endDate);
    return params;
  };

  const fetchTenderList = async (opts?: { nextPage?: number; nextPageSize?: number; nextFilters?: FilterParams }) => {
    const pageNum = opts?.nextPage ?? pagination.current;
    const pageSize = opts?.nextPageSize ?? pagination.pageSize;
    const f = opts?.nextFilters ?? filters;
    const params = buildQueryParams({ pageNum, pageSize, f });

    setLoading(true);
    setErrorText(null);
    try {
      const res = await fetch(getApiUrl(`/tenders?${params.toString()}`));
      const json = (await res.json()) as PageResponse<TenderListRow>;
      if (!res.ok || !json.success) {
        setErrorText(json?.msg || '查询失败');
        setRows([]);
        setTotal(0);
        return;
      }
      setRows(json.rows || []);
      setTotal(json.total || 0);
      setSelectedIds(new Set());
    } catch {
      setErrorText('查询失败');
      setRows([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchTenderList();
  }, []);

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleExportAll = async () => {
    const params = buildQueryParams({ pageNum: pagination.current, pageSize: pagination.pageSize, f: filters });
    const loadingBtn = document.getElementById('export-btn-all') as HTMLButtonElement | null;
    if (loadingBtn) loadingBtn.disabled = true;
    try {
      const res = await fetch(getApiUrl('/tenders/export'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
        body: params.toString(),
      });
      if (!res.ok) {
        alert('导出失败');
        return;
      }
      const blob = await res.blob();
      const filename = `招标信息_${new Date().toISOString().slice(0, 10)}.xlsx`;
      downloadBlob(blob, filename);
    } catch {
      alert('导出失败');
    } finally {
      if (loadingBtn) loadingBtn.disabled = false;
    }
  };

  const handleExportSelected = async () => {
    if (selectedIds.size === 0) return;
    
    const params = new URLSearchParams();
    params.set('tender_ids', Array.from(selectedIds).join(','));
    
    const loadingBtn = document.getElementById('export-btn-selected') as HTMLButtonElement | null;
    if (loadingBtn) loadingBtn.disabled = true;
    
    try {
      const res = await fetch(getApiUrl('/tenders/export'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
        body: params.toString(),
      });
      if (!res.ok) {
        alert('导出失败');
        return;
      }
      const blob = await res.blob();
      const filename = `招标信息_选中_${new Date().toISOString().slice(0, 10)}.xlsx`;
      downloadBlob(blob, filename);
    } catch {
      alert('导出失败');
    } finally {
      if (loadingBtn) loadingBtn.disabled = false;
    }
  };

  const getStageBadgeColor = (stage: string) => {
    switch (stage) {
      case TenderStage.ANNOUNCEMENT: return 'bg-blue-100 text-blue-700 border-blue-200';
      case TenderStage.CANDIDATE: return 'bg-purple-100 text-purple-700 border-purple-200';
      case TenderStage.RESULT: return 'bg-green-100 text-green-700 border-green-200';
      case TenderStage.FAILURE: return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Filter Bar */}
      <Card>
        <CardContent className="pt-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <Input 
              label="项目名称" 
              placeholder="输入关键词模糊搜索" 
              value={filters.keyword}
              onChange={e => setFilters(prev => ({ ...prev, keyword: e.target.value }))}
            />
            <Input 
              label="项目编号" 
              placeholder="输入完整编号" 
              value={filters.projectCode}
              onChange={e => setFilters(prev => ({ ...prev, projectCode: e.target.value }))}
            />
            <Select 
              label="所在区县" 
              options={DISTRICTS} 
              value={filters.district}
              onChange={e => setFilters(prev => ({ ...prev, district: e.target.value }))}
            />
            <Select 
              label="项目阶段" 
              options={STAGES} 
              value={filters.stage}
              onChange={e => setFilters(prev => ({ ...prev, stage: e.target.value }))}
            />
            <div className="lg:col-span-2 flex gap-4 items-end">
              <Input 
                type="date" 
                label="发布开始时间" 
                value={filters.startDate}
                onChange={e => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
              />
              <span className="pb-3 text-slate-400 font-medium">-</span>
              <Input 
                type="date" 
                label="发布结束时间" 
                value={filters.endDate}
                onChange={e => setFilters(prev => ({ ...prev, endDate: e.target.value }))}
              />
            </div>
            <div className="lg:col-span-2 flex items-end justify-end gap-3">
              <Button variant="secondary" onClick={handleReset} size="md">
                <RotateCcw className="mr-2 h-4 w-4" /> 重置
              </Button>
              <Button onClick={() => {
                setPagination(p => ({...p, current: 1}));
                void fetchTenderList({ nextPage: 1 });
              }} size="md" disabled={loading}>
                <Search className="mr-2 h-4 w-4" /> 查询
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Bar */}
      <div className="flex flex-wrap justify-between items-center gap-4">
        <h2 className="text-xl font-bold text-slate-800">查询结果 ({total})</h2>
        <div className="flex gap-3">
          <Button 
            id="export-btn-selected"
            variant="outline" 
            size="md" 
            onClick={handleExportSelected}
            disabled={selectedIds.size === 0 || loading}
          >
            <Download className="mr-2 h-4 w-4" /> 导出选中 ({selectedIds.size})
          </Button>
          <Button 
            id="export-btn-all"
            variant="outline" 
            size="md" 
            onClick={handleExportAll}
            disabled={loading}
          >
            <Download className="mr-2 h-4 w-4" /> 导出全部
          </Button>
        </div>
      </div>

      {/* Data Table */}
      <Card className="overflow-hidden border border-slate-200 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="text-sm font-semibold text-slate-600 uppercase bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="p-4 w-12">
                  <input 
                    type="checkbox" 
                    className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                    onChange={handleSelectAll}
                    checked={currentData.length > 0 && selectedIds.size >= currentData.length}
                  />
                </th>
                <th className="px-6 py-4">序号</th>
                <th className="px-6 py-4">项目名称</th>
                <th className="px-6 py-4">所在区县</th>
                <th className="px-6 py-4">建设单位</th>
                <th className="px-6 py-4">项目阶段</th>
                <th className="px-6 py-4">发布时间</th>
                <th className="px-6 py-4 text-right">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-base">
              {currentData.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-16 text-center text-slate-500">
                    <div className="flex flex-col items-center gap-3">
                      <AlertCircle className="h-10 w-10 text-slate-300" />
                      <p className="text-base">{loading ? '加载中...' : (errorText || '暂无数据，请尝试调整筛选条件')}</p>
                    </div>
                  </td>
                </tr>
              ) : (
                currentData.map((item, index) => (
                  <tr key={item.tenderId} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="p-4">
                      <input 
                        type="checkbox" 
                        className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                        checked={selectedIds.has(item.tenderId)}
                        onChange={() => handleSelectRow(item.tenderId)}
                      />
                    </td>
                    <td className="px-6 py-5 text-slate-500">
                      {(pagination.current - 1) * pagination.pageSize + index + 1}
                    </td>
                    <td className="px-6 py-5 font-medium text-slate-900">
                      <div className="flex flex-col gap-1">
                        <span 
                          className="hover:text-indigo-600 cursor-pointer transition-colors truncate max-w-[320px] text-base"
                          onClick={() => onViewDetail(String(item.tenderId))}
                          title={item.projectName}
                        >
                          {item.projectName || '-'}
                        </span>
                        <span className="text-sm text-slate-400">{item.projectCode || '-'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-5">{item.district || '-'}</td>
                    <td className="px-6 py-5 truncate max-w-[200px] text-slate-600" title={item.constructionUnit}>{item.constructionUnit || '-'}</td>
                    <td className="px-6 py-5">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getStageBadgeColor(item.projectStage || '')}`}>
                        {item.projectStage || '-'}
                      </span>
                    </td>
                    <td className="px-6 py-5 text-slate-500">{item.releaseTime || '-'}</td>
                    <td className="px-6 py-5 text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm" onClick={() => onViewDetail(String(item.tenderId))}>
                          <Eye className="h-4 w-4 mr-1.5" /> 详情
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="flex items-center justify-between p-4 border-t border-slate-200 bg-slate-50/50">
          <div className="text-base text-slate-500">
            显示 {(pagination.current - 1) * pagination.pageSize + 1} 到 {Math.min(pagination.current * pagination.pageSize, total)} 条，共 {total} 条
          </div>
          <div className="flex items-center gap-3">
            <select 
              className="h-9 rounded-md border-slate-200 text-sm focus:ring-indigo-500 focus:border-indigo-500 px-2"
              value={pagination.pageSize}
              onChange={(e) => {
                const nextPageSize = Number(e.target.value);
                setPagination({ current: 1, pageSize: nextPageSize });
                void fetchTenderList({ nextPage: 1, nextPageSize });
              }}
            >
              <option value={10}>10条/页</option>
              <option value={20}>20条/页</option>
              <option value={50}>50条/页</option>
            </select>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                className="px-3 h-9"
                disabled={pagination.current === 1}
                onClick={() => handlePageChange(pagination.current - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-base font-medium px-3 text-slate-700">
                {pagination.current} / {totalPages || 1}
              </span>
              <Button 
                variant="outline" 
                size="sm" 
                className="px-3 h-9"
                disabled={pagination.current === totalPages || totalPages === 0}
                onClick={() => handlePageChange(pagination.current + 1)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default TenderList;
