#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
"""
import pymysql
from config import DB_CONFIG

def test_connection():
    """测试数据库连接并显示详细信息"""
    print("正在测试数据库连接...")
    print(f"主机: {DB_CONFIG['host']}")
    print(f"端口: {DB_CONFIG['port']}")
    print(f"用户名: {DB_CONFIG['username']}")
    print(f"数据库列表: {', '.join(DB_CONFIG['database_names'])}")
    print("-" * 40)
    
    try:
        # 先尝试连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['username'],
            password=DB_CONFIG['password'],
            connect_timeout=10
        )
        
        print("✅ 成功连接到MySQL服务器！")
        
        with connection.cursor() as cursor:
            # 显示MySQL版本
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"MySQL版本: {version}")
            
            # 显示所有数据库
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("\n可用的数据库:")
            for db in databases:
                print(f"  - {db[0]}")
        
        connection.close()
        
        # 尝试连接到每个指定数据库
        print(f"\n正在测试各个数据库连接:")
        
        for db_name in DB_CONFIG['database_names']:
            try:
                print(f"\n  测试数据库: {db_name}")
                
                connection = pymysql.connect(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    user=DB_CONFIG['username'],
                    password=DB_CONFIG['password'],
                    database=db_name,
                    connect_timeout=10
                )
                
                print(f"    ✅ 成功连接到数据库: {db_name}")
                
                with connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    print(f"    表数量: {len(tables)}")
                
                connection.close()
                
            except Exception as e:
                print(f"    ❌ 连接失败: {str(e)}")
        return True
        
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        error_msg = e.args[1]
        
        print(f"❌ 连接失败: {error_msg}")
        
        if error_code == 1045:
            print("\n可能的解决方案:")
            print("1. 检查用户名和密码是否正确")
            print("2. 确认root用户是否允许从您的IP连接")
            print("3. 在MySQL服务器上执行:")
            print(f"   GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '{DB_CONFIG['password']}';")
            print("   FLUSH PRIVILEGES;")
        elif error_code == 2003:
            print("\n可能的解决方案:")
            print("1. 检查IP地址和端口是否正确")
            print("2. 检查防火墙设置")
            print("3. 确认MySQL服务正在运行")
        
        return False
        
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 