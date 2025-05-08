from data_fetcher import DataFetcher
from strategy import Strategy
from realtime_data import RealtimeDataFetcher
from trade_interface import TradeInterface
from risk_manager import RiskManager
from money_manager import MoneyManager
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import time
import numpy as np

def plot_portfolio(portfolio, title):
    """
    绘制投资组合表现
    """
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio.index, portfolio['total'], label='投资组合价值')
    plt.title(title)
    plt.xlabel('日期')
    plt.ylabel('价值')
    plt.legend()
    plt.grid(True)
    plt.show()

def run_backtest():
    """
    运行回测
    """
    try:
        # 初始化数据获取器和策略
        data_fetcher = DataFetcher()
        strategy = Strategy()
        
        # 设置回测参数
        stock_code = "000001"  # 平安银行
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        print(f"回测参数:")
        print(f"股票代码: {stock_code}")
        print(f"开始日期: {start_date}")
        print(f"结束日期: {end_date}")
        
        # 获取股票数据
        print(f"\n正在获取 {stock_code} 的历史数据...")
        stock_data = data_fetcher.get_stock_data(stock_code, start_date, end_date)
        
        if stock_data is None:
            print("获取数据失败，请检查股票代码和日期是否正确")
            return
        
        print("\n数据获取成功，数据形状:", stock_data.shape)
        print("数据列名:", stock_data.columns.tolist())
        print("\n数据预览:")
        print(stock_data.head())
        
        # 运行均线交叉策略回测
        print("\n正在运行均线交叉策略回测...")
        portfolio_ma = strategy.backtest(stock_data, strategy_type='ma_cross')
        
        if portfolio_ma.empty:
            print("均线交叉策略回测失败")
            return
            
        print("\n均线交叉策略回测结果预览:")
        print(portfolio_ma.head())
        
        # 运行MACD策略回测
        print("\n正在运行MACD策略回测...")
        portfolio_macd = strategy.backtest(stock_data, strategy_type='macd')
        
        if portfolio_macd.empty:
            print("MACD策略回测失败")
            return
            
        print("\nMACD策略回测结果预览:")
        print(portfolio_macd.head())
        
        # 计算策略表现
        try:
            # 计算年化收益率
            ma_returns = portfolio_ma['total'].pct_change().mean() * 252
            macd_returns = portfolio_macd['total'].pct_change().mean() * 252
            
            # 计算最大回撤
            ma_drawdown = (portfolio_ma['total'] / portfolio_ma['total'].cummax() - 1).min()
            macd_drawdown = (portfolio_macd['total'] / portfolio_macd['total'].cummax() - 1).min()
            
            # 计算夏普比率
            ma_sharpe = portfolio_ma['total'].pct_change().mean() / portfolio_ma['total'].pct_change().std() * np.sqrt(252)
            macd_sharpe = portfolio_macd['total'].pct_change().mean() / portfolio_macd['total'].pct_change().std() * np.sqrt(252)
            
            print("\n策略表现总结：")
            print(f"均线交叉策略:")
            print(f"  年化收益率: {ma_returns:.2%}")
            print(f"  最大回撤: {ma_drawdown:.2%}")
            print(f"  夏普比率: {ma_sharpe:.2f}")
            
            print(f"\nMACD策略:")
            print(f"  年化收益率: {macd_returns:.2%}")
            print(f"  最大回撤: {macd_drawdown:.2%}")
            print(f"  夏普比率: {macd_sharpe:.2f}")
            
        except Exception as e:
            print(f"计算策略表现时出错: {e}")
            import traceback
            print("错误详情:")
            print(traceback.format_exc())
        
        # 绘制投资组合表现
        try:
            plot_portfolio(portfolio_ma, "均线交叉策略投资组合表现")
            plot_portfolio(portfolio_macd, "MACD策略投资组合表现")
        except Exception as e:
            print(f"绘制图表时出错: {e}")
        
    except Exception as e:
        print(f"回测过程中出现错误: {e}")
        import traceback
        print("错误详情:")
        print(traceback.format_exc())

def run_live_trading():
    """
    运行实盘交易
    """
    # 初始化各个模块
    realtime_data = RealtimeDataFetcher()
    trade_interface = TradeInterface(account_id="test_account")
    risk_manager = RiskManager()
    money_manager = MoneyManager(initial_capital=1000000.0)
    strategy = Strategy()
    
    # 设置交易参数
    stock_codes = ["000001"]  # 平安银行
    update_interval = 3  # 更新间隔（秒）
    
    try:
        # 开始获取实时数据
        print("开始获取实时数据...")
        realtime_data.start_fetching(stock_codes)
        
        while True:
            # 获取最新数据
            latest_data = realtime_data.get_latest_data()
            if latest_data:
                # 获取账户信息
                account_info = trade_interface.get_account_info()
                
                # 更新投资组合价值
                current_prices = {latest_data['code']: latest_data['price']}
                portfolio_value = money_manager.get_portfolio_value(current_prices)
                risk_manager.update_portfolio_value(portfolio_value)
                
                # 获取策略信号
                # 这里需要将实时数据转换为策略可用的格式
                data_df = pd.DataFrame([latest_data])
                signals = strategy.ma_cross_strategy(data_df)
                
                # 检查是否有交易信号
                if not signals.empty and signals['position'].iloc[-1] != 0:
                    direction = 'buy' if signals['position'].iloc[-1] > 0 else 'sell'
                    price = latest_data['price']
                    
                    # 计算交易数量
                    volume = money_manager.calculate_position_size(
                        latest_data['code'], price
                    )
                    
                    if volume > 0:
                        # 创建订单
                        order = {
                            'stock_code': latest_data['code'],
                            'direction': direction,
                            'price': price,
                            'volume': volume
                        }
                        
                        # 风险检查
                        allowed, reason = risk_manager.check_order(order, account_info)
                        if allowed:
                            # 执行交易
                            order_id = trade_interface.place_order(
                                order['stock_code'],
                                order['direction'],
                                order['price'],
                                order['volume']
                            )
                            
                            if order_id:
                                # 更新资金管理
                                money_manager.update_position(
                                    order['stock_code'],
                                    order['direction'],
                                    order['price'],
                                    order['volume']
                                )
                                
                                print(f"执行交易: {order}")
                
                # 打印当前状态
                performance = money_manager.get_performance_metrics(current_prices)
                risk_metrics = risk_manager.get_risk_metrics()
                
                print("\n当前状态:")
                print(f"投资组合价值: {portfolio_value:,.2f}")
                print(f"总收益率: {performance['total_return']:.2%}")
                print(f"波动率: {risk_metrics.get('volatility', 0):.2%}")
                print(f"夏普比率: {risk_metrics.get('sharpe_ratio', 0):.2f}")
            
            time.sleep(update_interval)
            
    except KeyboardInterrupt:
        print("\n停止交易...")
    finally:
        realtime_data.stop_fetching()
        
        # 打印最终统计信息
        trade_stats = money_manager.get_trade_statistics()
        print("\n交易统计:")
        print(f"总交易次数: {trade_stats.get('total_trades', 0)}")
        print(f"买入交易: {trade_stats.get('buy_trades', 0)}")
        print(f"卖出交易: {trade_stats.get('sell_trades', 0)}")
        print(f"总交易金额: {trade_stats.get('total_value', 0):,.2f}")

if __name__ == "__main__":
    print("请选择运行模式：")
    print("1. 回测模式")
    print("2. 实盘交易模式")
    
    choice = input("请输入选择（1或2）：")
    
    if choice == "1":
        run_backtest()
    elif choice == "2":
        run_live_trading()
    else:
        print("无效的选择") 