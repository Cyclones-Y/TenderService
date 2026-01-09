import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Select } from './ui/Input';
import { Monitor, Save, Hash, Bell } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <div className="space-y-8 animate-fade-in max-w-5xl mx-auto">
       {/* UI Preference */}
       <Card>
         <CardHeader>
           <CardTitle className="flex items-center gap-3 text-xl"><Monitor className="h-6 w-6 text-indigo-600"/> 界面与显示</CardTitle>
         </CardHeader>
         <CardContent className="space-y-8">
            <div className="flex items-center justify-between">
               <div>
                  <label className="text-base font-medium text-slate-900">主题模式</label>
                  <p className="text-sm text-slate-500 mt-1">选择您喜欢的系统外观风格</p>
               </div>
               <div className="flex bg-slate-100 p-1.5 rounded-lg">
                  <button className="px-4 py-1.5 bg-white shadow-sm rounded-md text-sm font-medium text-slate-900 transition-all">浅色</button>
                  <button className="px-4 py-1.5 text-sm font-medium text-slate-500 hover:text-slate-900 transition-all">深色</button>
                  <button className="px-4 py-1.5 text-sm font-medium text-slate-500 hover:text-slate-900 transition-all">跟随系统</button>
               </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4 border-t border-slate-100">
               <Select label="默认列表每页条数" options={["10条/页", "20条/页", "50条/页", "100条/页"]} defaultValue="10条/页" />
               <Select label="列表密度" options={["标准 (默认)", "紧凑", "宽敞"]} defaultValue="标准 (默认)" />
            </div>
         </CardContent>
       </Card>

       {/* System Rules (Numbering) */}
       <Card>
         <CardHeader>
           <CardTitle className="flex items-center gap-3 text-xl"><Hash className="h-6 w-6 text-indigo-600"/> 编号与数据规则</CardTitle>
         </CardHeader>
         <CardContent className="space-y-8">
            <div className="flex items-center justify-between">
               <div>
                  <label className="text-base font-medium text-slate-900">自动补全项目编号</label>
                  <p className="text-sm text-slate-500 mt-1">当原始数据缺失编号时，根据规则生成临时编号</p>
               </div>
               <label className="relative inline-flex items-center cursor-pointer">
                 <input type="checkbox" className="sr-only peer" defaultChecked />
                 <div className="w-12 h-7 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-indigo-600"></div>
               </label>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
               <Select label="编号前缀规则" options={["ZB-YYYY-SEQ (标准)", "YYYY-MM-SEQ", "无前缀"]} />
               <Select label="数据刷新频率" options={["实时", "每10分钟", "每小时", "每天"]} defaultValue="每10分钟" />
            </div>
         </CardContent>
       </Card>

       <div className="flex justify-end gap-4 pt-6">
         <Button variant="secondary" size="lg">恢复默认设置</Button>
         <Button size="lg" onClick={() => alert('设置已保存')}><Save className="h-5 w-5 mr-2"/> 保存更改</Button>
       </div>
    </div>
  )
}

export default Settings;