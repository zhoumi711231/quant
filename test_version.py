import akshare as ak
import pandas as pd
from datetime import datetime
import time

def get_stock_realtime_quote(stock_code):
    """
    获取单个股票的实时行情数据
    :param stock_code: 股票代码（如：'000001'）
    :return: DataFrame
    """
    try:
        # 获取实时行情数据
        stock_df = ak.stock_zh_a_spot()
        # 如果指定了股票代码，则筛选特定股票
        if stock_code:
            stock_df = stock_df[stock_df['代码'] == stock_code]
        return stock_df
    except Exception as e:
        print(f"获取股票行情数据时发生错误: {str(e)}")
        return None

def get_stock_history(stock_code, start_date, end_date=None):
    """
    获取股票的历史行情数据
    :param stock_code: 股票代码（如：'000001'）
    :param start_date: 开始日期（如：'20240101'）
    :param end_date: 结束日期（如：'20240331'），默认为当前日期
    :return: DataFrame
    """
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 获取历史行情数据
        hist_data = ak.stock_zh_a_hist(symbol=stock_code, 
                                      start_date=start_date,
                                      end_date=end_date,
                                      adjust="qfq")
        return hist_data
    except Exception as e:
        print(f"获取历史数据时发生错误: {str(e)}")
        return None

def get_stock_list():
    """
    获取A股所有股票列表
    :return: DataFrame
    """
    try:
        stock_list = ak.stock_zh_a_spot_em()
    
        return stock_list
    except Exception as e:
        print(f"获取股票列表时发生错误: {str(e)}")
        return None

def main():
    # 示例：获取所有A股实时行情
    print("获取实时行情数据...")
    realtime_data = get_stock_realtime_quote('')
    if realtime_data is not None:
        print("\n实时行情数据示例（前5条）：")
        print(realtime_data.head())
        print(realtime_data)
    
    # 示例：获取特定股票的历史数据
    stock_code = '000001'  # 平安银行
    print(f"\n获取 {stock_code} 的历史数据...")
    hist_data = get_stock_history(stock_code, '20240101')
    if hist_data is not None:
        print("\n历史数据示例（前5条）：")
        print(hist_data.head())
    
    # 示例：获取股票列表
    print("\n获取股票列表...")
    stocks = get_stock_list()
    if stocks is not None:
        print(stocks)
        print("\n股票列表示例（前5条）：")
        print(stocks.head())

if __name__ == "__main__":
    main()