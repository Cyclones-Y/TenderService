import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, LineChart, Line, Legend
} from 'recharts';
import { PieChart as PieIcon, BarChart3, TrendingUp, Activity } from 'lucide-react';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#0ea5e9', '#22c55e', '#eab308', '#f97316'];

type DistrictStat = { name: string; value: number };
type StageStat = { name: string; value: number };
type TrendStat = { date: string; count: number };

type DashboardData = {
  totalProjects: number;
  monthNew: number;
  totalAmountBillion: number;
  topDistrict: string;
  lastSyncMinutesAgo: number;
  districtStats: DistrictStat[];
  stageStats: StageStat[];
  trendStats: TrendStat[];
};

type DataResponse<T> = {
  code: number;
  msg: string;
  success: boolean;
  time: string;
  data?: T;
};

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [errorText, setErrorText] = useState<string | null>(null);
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      setErrorText(null);
      try {
        const res = await fetch('/dev-api/tenders/dashboard');
        const json = (await res.json()) as DataResponse<DashboardData>;
        if (!res.ok || !json.success || !json.data) {
          setErrorText(json?.msg || '加载失败');
          setData(null);
          return;
        }
        setData(json.data);
      } catch {
        setErrorText('加载失败');
        setData(null);
      } finally {
        setLoading(false);
      }
    };
    void fetchDashboard();
  }, []);

  const districtStats = data?.districtStats || [];
  const stageStats = data?.stageStats || [];
  const trendStats = data?.trendStats || [];

  return (
    <div className="space-y-8 animate-fade-in">
      {errorText ? (
        <div className="text-base text-slate-500">{errorText}</div>
      ) : null}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium text-slate-600">总招标项目</CardTitle>
            <Activity className="h-5 w-5 text-slate-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-900">{data ? data.totalProjects.toLocaleString('zh-CN') : (loading ? '...' : '-')}</div>
            <p className="text-sm text-slate-500 mt-1">统计口径：项目编号去重</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium text-slate-600">本月新增</CardTitle>
            <TrendingUp className="h-5 w-5 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-900">{data ? data.monthNew.toLocaleString('zh-CN') : (loading ? '...' : '-')}</div>
            <p className="text-sm text-slate-500 mt-1">按采集时间统计</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium text-slate-600">涉及金额 (亿元)</CardTitle>
            <div className="h-5 w-5 text-slate-500 font-serif">¥</div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-900">{data ? data.totalAmountBillion.toLocaleString('zh-CN') : (loading ? '...' : '-')}</div>
            <p className="text-sm text-slate-500 mt-1">按招标控制价汇总</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-base font-medium text-slate-600">活跃区县</CardTitle>
            <PieIcon className="h-5 w-5 text-slate-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-900">{data ? (data.topDistrict || '-') : (loading ? '...' : '-')}</div>
            <p className="text-sm text-slate-500 mt-1">项目数量Top 1</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
               <TrendingUp className="h-5 w-5 text-indigo-600" />
               近30天发布趋势
            </CardTitle>
          </CardHeader>
          <CardContent className="pl-0">
            <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendStats} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: '#64748b' }} minTickGap={30} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: '#64748b' }} />
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', padding: '12px' }}
                    itemStyle={{ fontSize: '14px', fontWeight: 500 }}
                  />
                  <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        
        <Card className="col-span-3">
          <CardHeader>
             <CardTitle className="flex items-center gap-2 text-lg">
               <PieIcon className="h-5 w-5 text-indigo-600" />
               区域分布
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={districtStats}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {districtStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip contentStyle={{ borderRadius: '8px', padding: '10px' }} itemStyle={{ fontSize: '14px' }}/>
                  <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '14px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
               <BarChart3 className="h-5 w-5 text-indigo-600" />
               项目阶段分布
            </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stageStats}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: '#64748b' }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: '#64748b' }} />
                <RechartsTooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', padding: '10px' }} itemStyle={{ fontSize: '14px' }} />
                <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={50} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
