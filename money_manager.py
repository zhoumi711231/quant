import pandas as pd
import numpy as np
from datetime import datetime

class MoneyManager:
    def __init__(self, initial_capital=1000000.0):
        """
        初始化资金管理器
        :param initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # 当前持仓
        self.trade_history = []  # 交易历史
        self.cash_history = []  # 现金历史
        self.position_history = []  # 持仓历史
    
    def calculate_position_size(self, stock_code, price, risk_per_trade=0.02):
        """
        计算单个交易的仓位大小
        :param stock_code: 股票代码
        :param price: 当前价格
        :param risk_per_trade: 每笔交易的风险比例
        :return: int 可买入的股数
        """
        # 计算可用资金
        available_capital = self.current_capital * risk_per_trade
        
        # 计算可买入的股数（向下取整到100的倍数）
        shares = int(available_capital / price / 100) * 100
        
        return max(0, shares)
    
    def update_position(self, stock_code, direction, price, volume):
        """
        更新持仓信息
        :param stock_code: 股票代码
        :param direction: 交易方向 ('buy' 或 'sell')
        :param price: 价格
        :param volume: 数量
        """
        trade_value = price * volume
        
        if direction == 'buy':
            self.current_capital -= trade_value
            if stock_code not in self.positions:
                self.positions[stock_code] = 0
            self.positions[stock_code] += volume
        else:  # sell
            self.current_capital += trade_value
            if stock_code in self.positions:
                self.positions[stock_code] -= volume
                if self.positions[stock_code] == 0:
                    del self.positions[stock_code]
        
        # 记录交易
        trade = {
            'timestamp': datetime.now(),
            'stock_code': stock_code,
            'direction': direction,
            'price': price,
            'volume': volume,
            'value': trade_value
        }
        self.trade_history.append(trade)
        
        # 更新历史记录
        self._update_history()
    
    def _update_history(self):
        """
        更新历史记录
        """
        self.cash_history.append({
            'timestamp': datetime.now(),
            'cash': self.current_capital
        })
        
        self.position_history.append({
            'timestamp': datetime.now(),
            'positions': self.positions.copy()
        })
    
    def get_portfolio_value(self, current_prices):
        """
        计算当前投资组合价值
        :param current_prices: 当前价格字典 {stock_code: price}
        :return: float 投资组合总价值
        """
        position_value = sum(
            self.positions.get(code, 0) * price
            for code, price in current_prices.items()
        )
        return self.current_capital + position_value
    
    def get_performance_metrics(self, current_prices):
        """
        计算投资组合表现指标
        :param current_prices: 当前价格字典
        :return: dict 表现指标
        """
        portfolio_value = self.get_portfolio_value(current_prices)
        total_return = (portfolio_value - self.initial_capital) / self.initial_capital
        
        # 计算持仓分布
        position_distribution = {}
        for code, volume in self.positions.items():
            if code in current_prices:
                value = volume * current_prices[code]
                position_distribution[code] = value / portfolio_value
        
        return {
            'total_return': total_return,
            'current_capital': self.current_capital,
            'position_value': portfolio_value - self.current_capital,
            'position_distribution': position_distribution
        }
    
    def get_trade_statistics(self):
        """
        获取交易统计信息
        :return: dict 交易统计
        """
        if not self.trade_history:
            return {}
        
        df = pd.DataFrame(self.trade_history)
        
        stats = {
            'total_trades': len(df),
            'buy_trades': len(df[df['direction'] == 'buy']),
            'sell_trades': len(df[df['direction'] == 'sell']),
            'total_volume': df['volume'].sum(),
            'total_value': df['value'].sum(),
            'avg_trade_value': df['value'].mean()
        }
        
        return stats 