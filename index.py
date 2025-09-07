#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL数据库自动备份脚本
功能：每天凌晨2:30自动备份数据库，并删除10天前的备份文件
"""

import os
import subprocess
import datetime
import time
import glob
import schedule
import logging
import pymysql
import re
import shutil
from pathlib import Path
from config import DB_CONFIG, BACKUP_CONFIG, LOG_CONFIG

class MySQLBackupManager:
    def __init__(self, host, username, password, database_names, backup_dir, port=3306):
        """
        初始化备份管理器
        
        Args:
            host: 数据库主机地址
            username: 数据库用户名
            password: 数据库密码
            database_names: 要备份的数据库名称列表
            backup_dir: 备份文件存储目录
            port: 数据库端口（默认3306）
        """
        self.host = host
        self.username = username
        self.password = password
        self.database_names = database_names if isinstance(database_names, list) else [database_names]
        self.backup_dir = Path(backup_dir).expanduser()
        self.port = port
        
        # 设置日志
        self.setup_logging()
        
        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """设置日志记录"""
        log_dir = self.backup_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"backup_{datetime.date.today()}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def backup_database(self):
        """执行多数据库备份"""
        overall_start_time = datetime.datetime.now()
        successful_backups = []
        failed_backups = []
        
        self.logger.info("="*60)
        self.logger.info(f"开始多数据库备份任务")
        self.logger.info(f"备份时间: {overall_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"目标主机: {self.host}:{self.port}")
        self.logger.info(f"数据库数量: {len(self.database_names)}")
        self.logger.info(f"数据库列表: {', '.join(self.database_names)}")
        self.logger.info("="*60)
        
        # 创建以日期命名的备份文件夹
        date_folder = overall_start_time.strftime('%Y-%m-%d')
        daily_backup_dir = self.backup_dir / date_folder
        daily_backup_dir.mkdir(exist_ok=True)
        
        # 创建以时间命名的子文件夹（用于区分同一天的不同备份）
        time_folder = overall_start_time.strftime('%H%M')
        time_backup_dir = daily_backup_dir / time_folder
        time_backup_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"备份文件夹: {time_backup_dir}")
        
        for db_index, database_name in enumerate(self.database_names, 1):
            try:
                self.logger.info(f"\n[{db_index}/{len(self.database_names)}] 开始备份数据库: {database_name}")
                
                # 生成备份文件名（以时间命名）
                timestamp = overall_start_time.strftime('%Y%m%d_%H%M%S')
                backup_filename = f"{database_name}_backup_{timestamp}.sql"
                backup_filepath = time_backup_dir / backup_filename
                
                # 执行单个数据库备份
                db_start_time = datetime.datetime.now()
                success = self._create_backup_file(backup_filepath, database_name)
                
                if success:
                    # 获取备份文件大小
                    file_size = backup_filepath.stat().st_size
                    file_size_mb = file_size / (1024 * 1024)
                    
                    # 备份成功提示
                    db_end_time = datetime.datetime.now()
                    db_duration = db_end_time - db_start_time
                    
                    self.logger.info(f"✅ {database_name} 备份成功！")
                    self.logger.info(f"   文件: {backup_filename}")
                    self.logger.info(f"   大小: {file_size_mb:.2f} MB")
                    self.logger.info(f"   耗时: {db_duration}")
                    
                    successful_backups.append(database_name)
                else:
                    # 备份失败
                    self.logger.error(f"❌ {database_name} 备份失败")
                    failed_backups.append(database_name)
                    # 删除失败的备份文件
                    if backup_filepath.exists():
                        backup_filepath.unlink()
                        
            except Exception as e:
                self.logger.error(f"❌ {database_name} 备份过程中发生错误: {str(e)}")
                failed_backups.append(database_name)
        
        # 总结备份结果
        overall_end_time = datetime.datetime.now()
        total_duration = overall_end_time - overall_start_time
        
        self.logger.info("="*60)
        self.logger.info("多数据库备份任务完成！")
        self.logger.info(f"总耗时: {total_duration}")
        self.logger.info(f"成功备份: {len(successful_backups)} 个数据库")
        self.logger.info(f"失败备份: {len(failed_backups)} 个数据库")
        
        if successful_backups:
            self.logger.info(f"成功列表: {', '.join(successful_backups)}")
        if failed_backups:
            self.logger.error(f"失败列表: {', '.join(failed_backups)}")
        
        self.logger.info("="*60)
        
        # 清理旧备份文件
        self.cleanup_old_backups()
        
        return len(failed_backups) == 0  # 全部成功才返回True
    
    def _create_backup_file(self, backup_filepath, database_name):
        """使用pymysql创建数据库备份文件"""
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=database_name,
                charset='utf8mb4'
            )
            
            with open(backup_filepath, 'w', encoding='utf-8') as backup_file:
                # 写入备份文件头部
                backup_file.write(f"-- MySQL数据库备份\n")
                backup_file.write(f"-- 主机: {self.host}:{self.port}\n")
                backup_file.write(f"-- 数据库: {database_name}\n")
                backup_file.write(f"-- 备份时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                backup_file.write("-- --------------------------------------------------------\n\n")
                
                backup_file.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                
                with connection.cursor() as cursor:
                    # 获取所有表名
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        self.logger.info(f"正在备份表: {table_name}")
                        
                        # 获取建表语句
                        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                        create_table = cursor.fetchone()[1]
                        
                        backup_file.write(f"-- 表结构: {table_name}\n")
                        backup_file.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
                        backup_file.write(f"{create_table};\n\n")
                        
                        # 获取表数据
                        cursor.execute(f"SELECT * FROM `{table_name}`")
                        rows = cursor.fetchall()
                        
                        if rows:
                            backup_file.write(f"-- 表数据: {table_name}\n")
                            backup_file.write(f"INSERT INTO `{table_name}` VALUES\n")
                            
                            for i, row in enumerate(rows):
                                # 处理数据转义
                                values = []
                                for value in row:
                                    if value is None:
                                        values.append('NULL')
                                    elif isinstance(value, str):
                                        # 转义单引号和其他特殊字符
                                        escaped = value.replace('\\', '\\\\').replace("'", "\\'")
                                        values.append(f"'{escaped}'")
                                    else:
                                        values.append(str(value))
                                
                                row_data = f"({','.join(values)})"
                                if i == len(rows) - 1:
                                    backup_file.write(f"{row_data};\n\n")
                                else:
                                    backup_file.write(f"{row_data},\n")
                
                backup_file.write("SET FOREIGN_KEY_CHECKS=1;\n")
            
            connection.close()
            return True
            
        except Exception as e:
            self.logger.error(f"创建备份文件失败: {str(e)}")
            return False
    
    def cleanup_old_backups(self):
        """清理过期的备份文件夹"""
        try:
            retention_days = BACKUP_CONFIG['retention_days']
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
            
            deleted_folders = 0
            deleted_files = 0
            total_checked = 0
            
            # 遍历备份目录中的所有日期文件夹
            for item in self.backup_dir.iterdir():
                if item.is_dir() and re.match(r'^\d{4}-\d{2}-\d{2}$', item.name):  # 匹配 YYYY-MM-DD 格式
                    total_checked += 1
                    
                    # 从文件夹名解析日期
                    try:
                        folder_date = datetime.datetime.strptime(item.name, '%Y-%m-%d')
                        
                        if folder_date < cutoff_date:
                            # 计算该文件夹中的所有备份文件数量（包括子文件夹）
                            backup_files = []
                            for time_folder in item.iterdir():
                                if time_folder.is_dir() and re.match(r'^\d{4}$', time_folder.name):  # 匹配 HHMM 格式
                                    backup_files.extend(list(time_folder.glob("*_backup_*.sql")))
                            
                            file_count = len(backup_files)
                            
                            # 删除整个过期的日期文件夹
                            shutil.rmtree(item)
                            
                            self.logger.info(f"已删除过期备份文件夹: {item.name} (包含 {file_count} 个备份文件)")
                            deleted_folders += 1
                            deleted_files += file_count
                            
                    except ValueError:
                        # 如果文件夹名不是有效日期格式，跳过
                        continue
                    except Exception as e:
                        self.logger.error(f"删除文件夹失败 {item.name}: {str(e)}")
            
            if deleted_folders > 0:
                self.logger.info(f"共清理了 {deleted_folders} 个过期备份文件夹，{deleted_files} 个备份文件（检查了 {total_checked} 个文件夹）")
            else:
                self.logger.info(f"没有找到需要清理的过期备份文件夹（检查了 {total_checked} 个文件夹）")
                
        except Exception as e:
            self.logger.error(f"清理旧备份文件时发生错误: {str(e)}")
    
    def test_connection(self):
        """测试数据库服务器连接"""
        try:
            # 先测试服务器连接（不指定数据库）
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                connect_timeout=30
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
                # 验证每个目标数据库是否存在
                cursor.execute("SHOW DATABASES")
                available_dbs = [db[0] for db in cursor.fetchall()]
                
                missing_dbs = []
                for db_name in self.database_names:
                    if db_name not in available_dbs:
                        missing_dbs.append(db_name)
                
                if missing_dbs:
                    self.logger.warning(f"以下数据库不存在: {', '.join(missing_dbs)}")
            
            connection.close()
            return True
        except Exception as e:
            self.logger.error(f"测试数据库连接失败: {str(e)}")
            return False


def main():
    """主函数"""
    # 创建备份管理器实例
    backup_manager = MySQLBackupManager(**DB_CONFIG)
    
    print("MySQL多数据库自动备份脚本启动")
    print(f"目标服务器: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"数据库数量: {len(DB_CONFIG['database_names'])} 个")
    print(f"数据库列表: {', '.join(DB_CONFIG['database_names'])}")
    print(f"备份根目录: {DB_CONFIG['backup_dir']}")
    print(f"文件组织方式: 按日期分文件夹存储 (YYYY-MM-DD)")
    print(f"定时备份时间: 每天 {len(BACKUP_CONFIG['backup_times'])} 次")
    print(f"备份时间点: {', '.join(BACKUP_CONFIG['backup_times'])}")
    print(f"备份文件保留天数: {BACKUP_CONFIG['retention_days']} 天")
    print("-" * 60)
    
    # 测试数据库连接
    print("正在测试数据库连接...")
    if backup_manager.test_connection():
        print("✓ 数据库连接测试成功")
    else:
        print("✗ 数据库连接测试失败，请检查config.py中的配置信息")
        print("请确保以下信息正确：")
        print(f"  - 主机地址: {DB_CONFIG['host']}")
        print(f"  - 端口: {DB_CONFIG['port']}")
        print(f"  - 用户名: {DB_CONFIG['username']}")
        print(f"  - 数据库列表: {', '.join(DB_CONFIG['database_names'])}")
        print("  - 密码和网络连接")
        return
    
    # 安排多个定时任务
    for backup_time in BACKUP_CONFIG['backup_times']:
        schedule.every().day.at(backup_time).do(backup_manager.backup_database)
        print(f"已设置备份任务: 每天 {backup_time}")
    
    print("定时备份任务已设置，等待执行...")
    print("按 Ctrl+C 退出程序")
    print("# backup_manager.backup_database()")
    
    # 可选：立即执行一次备份进行测试
    # print("正在执行测试备份...")
    # backup_manager.backup_database()
    
    try:
        # 保持程序运行，等待定时任务执行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n程序已退出")


if __name__ == "__main__":
    main()
