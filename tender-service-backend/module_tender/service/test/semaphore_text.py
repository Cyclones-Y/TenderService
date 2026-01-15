import asyncio
import random

async def use_shared_resource(semaphore, task_id):
    # 等待获取信号量
    async with semaphore:
        print(f"任务 {task_id} 正在使用共享资源...")
        # 模拟占用资源一段时间
        await asyncio.sleep(random.uniform(1, 2))
        print(f"任务 {task_id} 已完成并释放资源")

async def main():
    # 限制最多允许2个协程同时使用共享资源
    semaphore = asyncio.Semaphore(3)

    tasks = [use_shared_resource(semaphore, i) for i in range(1, 6)]

    # 等待所有任务完成
    await asyncio.gather(*tasks)

# 运行主函数
asyncio.run(main())
