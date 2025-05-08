import pandas as pd
import numpy as np

class Strategy:
    def __init__(self):
        self.position = 0
        self.cash = 0
        self.positions = []
        self.trades = []
    
    def calculate_ma(self, data, window):
        """
        计算移动平均线
        """
        return data['close'].rolling(window=window).mean()
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """
        计算MACD指标
        """
        exp1 = data['close'].ewm(span=fast, adjust=False).mean()
        exp2 = data['close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def ma_cross_strategy(self, data, short_window=5, long_window=20):
        """
        均线交叉策略
        """
        try:
            signals = pd.DataFrame(index=data.index)
            signals['price'] = data['close']
            signals['short_ma'] = self.calculate_ma(data, short_window)
            signals['long_ma'] = self.calculate_ma(data, long_window)
            
            # 生成交易信号
            signals['signal'] = 0.0
            signals.loc[signals['short_ma'] > signals['long_ma'], 'signal'] = 1.0
            
            # 生成仓位变化信号
            signals['position'] = signals['signal'].diff()
            signals['position'] = signals['position'].fillna(0)
            
            return signals
        except Exception as e:
            print(f"均线交叉策略计算错误: {e}")
            return pd.DataFrame()
    
    def macd_strategy(self, data):
        """
        MACD策略
        """
        try:
            signals = pd.DataFrame(index=data.index)
            signals['price'] = data['close']
            macd, signal_line, histogram = self.calculate_macd(data)
            
            signals['macd'] = macd
            signals['signal_line'] = signal_line
            signals['histogram'] = histogram
            
            # 生成交易信号
            signals['signal'] = 0.0
            signals.loc[signals['macd'] > signals['signal_line'], 'signal'] = 1.0
            
            # 生成仓位变化信号
            signals['position'] = signals['signal'].diff()
            signals['position'] = signals['position'].fillna(0)
            
            return signals
        except Exception as e:
            print(f"MACD策略计算错误: {e}")
            return pd.DataFrame()
    
    def backtest(self, data, strategy_type='ma_cross', initial_capital=100000.0):
        """
        回测策略
        """
        try:
            if strategy_type == 'ma_cross':
                signals = self.ma_cross_strategy(data)
            elif strategy_type == 'macd':
                signals = self.macd_strategy(data)
            else:
                raise ValueError("不支持的策略类型")
            
            if signals.empty:
                raise ValueError("策略信号生成失败")
            
            # 初始化投资组合
            portfolio = pd.DataFrame(index=signals.index)
            
            # 计算持仓
            portfolio['positions'] = signals['signal'] * initial_capital / signals['price']
            portfolio['positions'] = portfolio['positions'].fillna(0)
            
            # 计算现金
            position_changes = signals['position'] * signals['price'] * portfolio['positions']
            portfolio['cash'] = initial_capital - position_changes.cumsum()
            
            # 计算总资产
            portfolio['total'] = portfolio['positions'] * signals['price'] + portfolio['cash']
            
            # 计算收益率
            portfolio['returns'] = portfolio['total'].pct_change()
            portfolio['returns'] = portfolio['returns'].fillna(0)
            
            return portfolio
            
        except Exception as e:
            print(f"回测过程出错: {e}")
            import traceback
            print("错误详情:")
            print(traceback.format_exc())
            return pd.DataFrame() 