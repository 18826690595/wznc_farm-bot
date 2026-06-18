"""
账号管理模块
用于读取和管理账号信息CSV文件
"""
import csv
import os
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Account:
    """账号数据类"""
    account: str           # 账号
    password: str          # 密码
    executed_today: bool   # 今天是否已执行
    last_exec_time: str    # 最后执行时间
    remarks: str           # 备注
    
    @property
    def need_execute(self) -> bool:
        """是否需要执行"""
        return not self.executed_today
    
    def mark_executed(self):
        """标记为已执行"""
        self.executed_today = True
        self.last_exec_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class AccountManager:
    """账号管理器"""
    
    def __init__(self, csv_path: str = None):
        """
        初始化账号管理器
        
        Args:
            csv_path: CSV文件路径，默认为 config/accounts.csv
        """
        if csv_path is None:
            csv_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config", "accounts.csv"
            )
        self.csv_path = csv_path
        self.accounts: List[Account] = []
        self._load()
    
    def _load(self):
        """从CSV加载账号"""
        if not os.path.exists(self.csv_path):
            return
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                account = Account(
                    account=row.get('account', ''),
                    password=row.get('password', ''),
                    executed_today=row.get('executed_today', 'false').lower() == 'true',
                    last_exec_time=row.get('last_exec_time', ''),
                    remarks=row.get('remarks', '')
                )
                self.accounts.append(account)
    
    def _save(self):
        """保存账号到CSV"""
        with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['account', 'password', 'executed_today', 'last_exec_time', 'remarks']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for acc in self.accounts:
                writer.writerow({
                    'account': acc.account,
                    'password': acc.password,
                    'executed_today': 'true' if acc.executed_today else 'false',
                    'last_exec_time': acc.last_exec_time,
                    'remarks': acc.remarks
                })
    
    def get_all(self) -> List[Account]:
        """获取所有账号"""
        return self.accounts
    
    def get_need_execute(self) -> List[Account]:
        """获取需要执行的账号"""
        return [acc for acc in self.accounts if acc.need_execute]
    
    def get_by_account(self, account_name: str) -> Optional[Account]:
        """根据账号名获取账号"""
        for acc in self.accounts:
            if acc.account == account_name:
                return acc
        return None
    
    def mark_executed(self, account_name: str):
        """标记账号为已执行"""
        acc = self.get_by_account(account_name)
        if acc:
            acc.mark_executed()
            self._save()
    
    def reset_daily(self):
        """重置每日执行状态（每天0点调用）"""
        for acc in self.accounts:
            acc.executed_today = False
        self._save()
    
    def add_account(self, account: str, password: str, remarks: str = ""):
        """添加新账号"""
        new_acc = Account(
            account=account,
            password=password,
            executed_today=False,
            last_exec_time="",
            remarks=remarks
        )
        self.accounts.append(new_acc)
        self._save()
    
    def remove_account(self, account_name: str):
        """删除账号"""
        self.accounts = [acc for acc in self.accounts if acc.account != account_name]
        self._save()
    
    def count(self) -> int:
        """账号总数"""
        return len(self.accounts)
    
    def count_need_execute(self) -> int:
        """需要执行的账号数"""
        return len(self.get_need_execute())
    
    def __str__(self) -> str:
        return f"AccountManager(total={self.count()}, need_execute={self.count_need_execute()})"


# 全局实例
account_manager = AccountManager()