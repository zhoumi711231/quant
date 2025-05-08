import akshare as ak
import pandas as pd
import time
from datetime import datetime
import threading
import queue

class RealtimeDataFetcher:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.running = False
        self.stock_list = []
        self.update_interval = 3  # 更新间隔（秒）
    
    def start_fetching(self, stock_codes):
        """
        开始获取实时数据
        :param stock_codes: 股票代码列表
        """
        self.stock_list = stock_codes
        self.running = True
        self.fetch_thread = threading.Thread(target=self._fetch_loop)
        self.fetch_thread.start()
    
    def stop_fetching(self):
        """
        停止获取实时数据
        """
        self.running = False
        if hasattr(self, 'fetch_thread'):
            self.fetch_thread.join()
    
    def _fetch_loop(self):
        """
        实时数据获取循环
        """
        while self.running:
            try:
                # 获取实时行情
                realtime_data = ak.stock_zh_a_spot_em()
                
                # 打印列名，用于调试
                print("实时数据列名:", realtime_data.columns.tolist())
                
                # 检查必要的列是否存在
                required_columns = ['代码', '最新价', '成交量', '成交额', '买一价', '卖一价', '买一量', '卖一量']
                if not all(col in realtime_data.columns for col in required_columns):
                    print("警告：实时数据缺少必要的列")
                    print("可用的列:", realtime_data.columns.tolist())
                    time.sleep(self.update_interval)
                    continue
                
                for stock_code in self.stock_list:
                    try:
                        stock_data = realtime_data[realtime_data['代码'] == stock_code]
                        
                        if not stock_data.empty:
                            # 确保所有数值都是有效的
                            data = {
                                'timestamp': datetime.now(),
                                'code': stock_code,
                                'price': float(stock_data['最新价'].values[0]),
                                'volume': float(stock_data['成交量'].values[0]),
                                'amount': float(stock_data['成交额'].values[0]),
                                'bid_price': float(stock_data['买一价'].values[0]),
                                'ask_price': float(stock_data['卖一价'].values[0]),
                                'bid_volume': float(stock_data['买一量'].values[0]),
                                'ask_volume': float(stock_data['卖一量'].values[0])
                            }
                            
                            # 验证数据有效性
                            if all(isinstance(v, (int, float)) for v in data.values() if isinstance(v, (int, float))):
                                self.data_queue.put(data)
                            else:
                                print(f"警告：股票 {stock_code} 的数据无效")
                    except Exception as e:
                        print(f"处理股票 {stock_code} 数据时出错: {e}")
                        continue
                
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"获取实时数据时出错: {e}")
                import traceback
                print("错误详情:")
                print(traceback.format_exc())
                time.sleep(self.update_interval)
    
    def get_latest_data(self):
        """
        获取最新的实时数据
        :return: 最新的数据字典
        """
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_all_data(self):
        """
        获取所有待处理的数据
        :return: 数据列表
        """
        data_list = []
        while not self.data_queue.empty():
            try:
                data_list.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
        return data_list 