"""
任务调度器 - 定时执行农场任务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from typing import Callable, Optional, Dict, Any
from datetime import datetime


class TaskScheduler:
    """
    任务调度器
    基于APScheduler实现定时任务
    """
    
    def __init__(self):
        """初始化调度器"""
        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[str, Any] = {}
        self._is_running = False
        
        logger.info("任务调度器已初始化")
    
    def start(self):
        """启动调度器"""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            logger.success("任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if self._is_running:
            self.scheduler.shutdown()
            self._is_running = False
            logger.info("任务调度器已停止")
    
    @property
    def is_running(self) -> bool:
        """调度器是否运行中"""
        return self._is_running
    
    def add_interval_job(
        self,
        job_id: str,
        func: Callable,
        interval: int,
        unit: str = 'seconds',
        start_date: Optional[datetime] = None,
        **kwargs
    ) -> bool:
        """
        添加间隔任务
        
        Args:
            job_id: 任务ID
            func: 任务函数
            interval: 间隔时间
            unit: 时间单位 (seconds, minutes, hours)
            start_date: 开始时间
            **kwargs: 传递给任务函数的参数
            
        Returns:
            是否添加成功
        """
        try:
            # 构建触发器参数
            trigger_args = {unit: interval}
            trigger = IntervalTrigger(**trigger_args, start_date=start_date)
            
            job = self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                kwargs=kwargs,
                replace_existing=True
            )
            
            self.jobs[job_id] = job
            logger.info(f"添加间隔任务: {job_id}, 间隔 {interval} {unit}")
            return True
            
        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            return False
    
    def add_cron_job(
        self,
        job_id: str,
        func: Callable,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        **kwargs
    ) -> bool:
        """
        添加定时任务（Cron表达式）
        
        Args:
            job_id: 任务ID
            func: 任务函数
            hour: 小时
            minute: 分钟
            **kwargs: 传递给任务函数的参数
            
        Returns:
            是否添加成功
        """
        try:
            trigger = CronTrigger(hour=hour, minute=minute)
            
            job = self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                kwargs=kwargs,
                replace_existing=True
            )
            
            self.jobs[job_id] = job
            logger.info(f"添加定时任务: {job_id}, 时间 {hour}:{minute}")
            return True
            
        except Exception as e:
            logger.error(f"添加定时任务失败: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """
        移除任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否移除成功
        """
        try:
            self.scheduler.remove_job(job_id)
            self.jobs.pop(job_id, None)
            logger.info(f"移除任务: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"移除任务失败: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """
        暂停任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否暂停成功
        """
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"暂停任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"暂停任务失败: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """
        恢复任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否恢复成功
        """
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"恢复任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"恢复任务失败: {e}")
            return False
    
    def get_jobs(self) -> Dict[str, Any]:
        """
        获取所有任务
        
        Returns:
            任务字典
        """
        jobs_info = {}
        
        for job_id, job in self.jobs.items():
            next_run = job.next_run_time
            jobs_info[job_id] = {
                'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S') if next_run else '未调度',
                'trigger': str(job.trigger)
            }
        
        return jobs_info
    
    def print_jobs(self):
        """打印所有任务信息"""
        jobs = self.get_jobs()
        
        if not jobs:
            logger.info("当前无任务")
            return
        
        logger.info("当前任务列表:")
        for job_id, info in jobs.items():
            logger.info(f"  - {job_id}: 下次运行 {info['next_run']}")
    
    def setup_default_tasks(
        self,
        harvest_func: Callable,
        plant_func: Callable,
        steal_func: Callable,
        bless_func: Callable,
        config: dict
    ):
        """
        设置默认任务
        
        Args:
            harvest_func: 收菜函数
            plant_func: 种菜函数
            steal_func: 偷菜函数
            bless_func: 祝福函数
            config: 配置字典
        """
        # 收菜任务
        if config.get('harvest_interval'):
            self.add_interval_job(
                job_id='harvest',
                func=harvest_func,
                interval=config['harvest_interval'],
                unit='seconds'
            )
        
        # 偷菜任务
        if config.get('steal_interval'):
            self.add_interval_job(
                job_id='steal',
                func=steal_func,
                interval=config['steal_interval'],
                unit='seconds'
            )
        
        # 祝福任务
        if config.get('bless_interval'):
            self.add_interval_job(
                job_id='bless',
                func=bless_func,
                interval=config['bless_interval'],
                unit='seconds'
            )
        
        # 定时种菜（每天固定时间）
        if config.get('plant_cron'):
            hour = config['plant_cron'].get('hour')
            minute = config['plant_cron'].get('minute', 0)
            self.add_cron_job(
                job_id='plant',
                func=plant_func,
                hour=hour,
                minute=minute
            )
        
        logger.info("默认任务已设置")
