import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self, max_position_size=0.1, max_drawdown=0.2, stop_loss_pct=0.05):
        """
        初始化风险管理器
        :param max_position_size: 单个股票最大仓位比例
        :param max_drawdown: 最大回撤限制
        :param stop_loss_pct: 止损比例
        """
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.stop_loss_pct = stop_loss_pct
        self.positions = {}
        self.trade_history = []
        self.portfolio_value_history = []
    
    def check_order(self, order, account_info):
        """
        检查订单是否符合风险控制要求
        :param order: 订单信息
        :param account_info: 账户信息
        :return: (bool, str) 是否允许下单，原因
        """
        # 检查单个股票仓位限制
        if order['direction'] == 'buy':
            current_position = self.positions.get(order['stock_code'], 0)
            new_position = current_position + order['volume']
            position_value = new_position * order['price']
            total_assets = account_info['total_assets']
            
            if position_value / total_assets > self.max_position_size:
                return False, "超过单个股票最大仓位限制"
        
        # 检查止损
        if order['direction'] == 'sell':
            if self._check_stop_loss(order['stock_code'], order['price']):
                return True, "触发止损"
        
        return True, "通过风险检查"
    
    def _check_stop_loss(self, stock_code, current_price):
        """
        检查是否触发止损
        :param stock_code: 股票代码
        :param current_price: 当前价格
        :return: bool 是否触发止损
        """
        if stock_code in self.positions:
            position = self.positions[stock_code]
            if position > 0:
                # 获取持仓成本
                cost = self._get_position_cost(stock_code)
                if cost > 0:
                    loss_pct = (current_price - cost) / cost
                    return loss_pct < -self.stop_loss_pct
        return False
    
    def _get_position_cost(self, stock_code):
        """
        获取持仓成本
        :param stock_code: 股票代码
        :return: float 持仓成本
        """
        # 这里应该实现实际的持仓成本计算
        return 0.0
    
    def update_portfolio_value(self, portfolio_value):
        """
        更新投资组合价值历史
        :param portfolio_value: 当前投资组合价值
        """
        self.portfolio_value_history.append({
            'timestamp': datetime.now(),
            'value': portfolio_value
        })
        
        # 检查最大回撤
        self._check_max_drawdown()
    
    def _check_max_drawdown(self):
        """
        检查最大回撤
        :return: bool 是否超过最大回撤限制
        """
        if len(self.portfolio_value_history) < 2:
            return False
        
        values = [record['value'] for record in self.portfolio_value_history]
        peak = np.maximum.accumulate(values)
        drawdown = (peak - values) / peak
        
        return np.max(drawdown) > self.max_drawdown
    
    def get_risk_metrics(self):
        """
        获取风险指标
        :return: dict 风险指标
        """
        if len(self.portfolio_value_history) < 2:
            return {}
        
        values = [record['value'] for record in self.portfolio_value_history]
        returns = np.diff(values) / values[:-1]
        
        metrics = {
            'volatility': np.std(returns) * np.sqrt(252),  # 年化波动率
            'max_drawdown': self._calculate_max_drawdown(values),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'var_95': self._calculate_var(returns, 0.95)  # 95% VaR
        }
        
        return metrics
    
    def _calculate_max_drawdown(self, values):
        """
        计算最大回撤
        """
        peak = np.maximum.accumulate(values)
        drawdown = (peak - values) / peak
        return np.max(drawdown)
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.03):
        """
        计算夏普比率
        """
        excess_returns = returns - risk_free_rate/252
        if len(excess_returns) == 0:
            return 0
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    def _calculate_var(self, returns, confidence_level):
        """
        计算VaR
        """
        return np.percentile(returns, (1 - confidence_level) * 100) 