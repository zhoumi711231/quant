import akshare as ak
import pandas as pd
from datetime import datetime

def get_real_time_quotes(stock_codes):
    """
    获取实时行情数据
    :param stock_codes: 股票代码列表，例如 ['600519', '000858']
    :return: DataFrame 包含实时行情数据
    """
    try:
        # 获取实时行情数据
       
        
        stock_data = ak.stock_zh_a_spot_em()
        
        # 如果指定了股票代码，则只返回这些股票的数据
        if stock_codes:
            stock_data = stock_data[stock_data['代码'].isin(stock_codes)]
        
        return stock_data
    except Exception as e:
        print(f"获取数据时出错: {str(e)}")
        return None

def save_to_csv(data, filename=None):
    """
    将数据保存为CSV文件
    :param data: DataFrame 数据
    :param filename: 文件名，如果为None则使用当前时间戳
    """
    if filename is None:
        filename = f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    data.to_csv(filename, encoding='utf-8-sig', index=False)
    print(f"数据已保存到: {filename}")

def main():
    # 示例股票代码列表（可以根据需要修改）
    stock_codes = ['600519', '000858', '601318']  # 贵州茅台、五粮液、中国平安
    
    print("正在获取A股实时行情数据...")
    stock_data = get_real_time_quotes(stock_codes)
    
    if stock_data is not None:
        print("\n获取到的数据示例：")
        print(stock_data.head())
        
        # 保存数据到CSV文件
        save_to_csv(stock_data)

if __name__ == "__main__":
    main() 