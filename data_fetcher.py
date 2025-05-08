import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self):
        self.cache = {}
    
    def get_stock_data(self, stock_code, start_date, end_date):
        """
        获取股票历史数据
        :param stock_code: 股票代码（如：000001）
        :param start_date: 开始日期（如：20230101）
        :param end_date: 结束日期（如：20240101）
        :return: DataFrame包含OHLCV数据
        """
        try:
            print(f"正在获取股票 {stock_code} 的历史数据...")
            print(f"开始日期: {start_date}")
            print(f"结束日期: {end_date}")
            
            # 获取日线数据
            df = ak.stock_zh_a_hist(symbol=stock_code, 
                                  start_date=start_date, 
                                  end_date=end_date, 
                                  adjust="qfq")
            
            if df is None or df.empty:
                print("获取数据失败：返回数据为空")
                return None
            
            # 打印原始列名，用于调试
            print("原始数据列名:", df.columns.tolist())
            
            # 检查数据是否包含必要的列
            required_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量']
            if not all(col in df.columns for col in required_columns):
                print("警告：数据缺少必要的列")
                print("可用的列:", df.columns.tolist())
                return None
            
            # 重命名为标准格式
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover_rate'
            }
            
            # 只重命名存在的列
            existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=existing_columns)
            
            # 确保数值列为数值类型
            numeric_columns = ['open', 'close', 'high', 'low', 'volume', 'amount']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 设置日期为索引
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 删除包含NaN的行
            df = df.dropna(subset=['open', 'close', 'high', 'low', 'volume'])
            
            if df.empty:
                print("警告：清理后的数据为空")
                return None
            
            print(f"成功获取数据，形状: {df.shape}")
            print("数据预览:")
            print(df.head())
            
            return df
            
        except Exception as e:
            print(f"获取股票数据时出错: {e}")
            import traceback
            print("错误详情:")
            print(traceback.format_exc())
            return None
    
    def get_index_data(self, index_code, start_date, end_date):
        """
        获取指数数据
        :param index_code: 指数代码（如：000001）
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: DataFrame包含指数数据
        """
        try:
            df = ak.stock_zh_index_daily(symbol=index_code)
            if df is None or df.empty:
                print("获取指数数据失败：返回数据为空")
                return None
                
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            return df
        except Exception as e:
            print(f"获取指数数据时出错: {e}")
            return None
    
    def get_stock_list(self):
        """
        获取A股股票列表
        :return: DataFrame包含股票列表
        """
        try:
            stock_list = ak.stock_zh_a_spot_em()
            if stock_list is None or stock_list.empty:
                print("获取股票列表失败：返回数据为空")
                return None
            return stock_list
        except Exception as e:
            print(f"获取股票列表时出错: {e}")
            return None 