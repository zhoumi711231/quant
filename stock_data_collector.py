import akshare as ak
import pandas as pd
from sqlalchemy import create_engine
import datetime
import time

def get_stock_data():
    """
    获取A股市场所有股票的行情数据
    """
    try:
        # 获取A股所有股票的实时行情数据
        stock_df = ak.stock_zh_a_spot_em()

        stock_data = ak.stock_zh_a_spot_em()
        # 添加获取时间列
        stock_df['fetch_time'] = datetime.datetime.now()
        return stock_df
    except Exception as e:
        print(f"获取股票数据时出错: {str(e)}")
        return None

def create_mysql_engine(user, password, host, port, database):
    """
    创建MySQL数据库连接
    """
    try:
        engine = create_engine(
            f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'
        )
        return engine
    except Exception as e:
        print(f"创建数据库连接时出错: {str(e)}")
        return None

def save_to_mysql(df, engine, table_name):
    """
    将数据保存到MySQL数据库
    """
    try:
        # 处理可能的空值
        df = df.where(pd.notnull(df), None)
        # 确保数值类型列的类型正确
        numeric_columns = ['最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', 
                         '最高', '最低', '今开', '昨收', '量比', '换手率', 
                         '市盈率-动态', '市净率', '总市值', '流通市值', 
                         '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 保存到数据库
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"成功保存 {len(df)} 条记录到数据库")
    except Exception as e:
        print(f"保存数据到MySQL时出错: {str(e)}")

def main():
    # 数据库配置
    DB_CONFIG = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'port': 3306,
        'database': 'stock_market'
    }
    
    # 创建数据库连接
    engine = create_mysql_engine(**DB_CONFIG)
    if not engine:
        return
    
    while True:
        try:
            # 获取股票数据
            stock_df = get_stock_data()
            
            if stock_df is not None:
                # 保存到MySQL
                save_to_mysql(stock_df, engine, 'stock_realtime_data')
            
            # 等待5分钟后再次获取数据
            print(f"数据更新完成，等待5分钟后继续...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("程序已停止")
            break
        except Exception as e:
            print(f"运行出错: {str(e)}")
            time.sleep(60)  # 发生错误时等待1分钟后重试

if __name__ == "__main__":
    main()