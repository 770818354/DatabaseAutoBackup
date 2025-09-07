# MySQL数据库自动备份脚本

这是一个Python脚本，用于自动备份MySQL数据库到指定目录，并自动清理过期的备份文件。

## 功能特性

✅ **定时备份**：每天在四个时间点自动执行数据库备份（06:00, 12:00, 18:00, 00:00）  
✅ **智能命名**：备份文件以时间戳命名，便于管理  
✅ **自动清理**：自动删除超过保留期限的旧备份文件  
✅ **详细日志**：提供完整的备份过程日志记录  
✅ **连接测试**：启动时自动测试数据库连接  
✅ **错误处理**：完善的错误处理和超时机制  

## 系统要求

- Python 3.6+
- MySQL客户端工具（mysql、mysqldump）
- 网络连接到目标数据库服务器

## 安装步骤

### 1. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 2. 安装MySQL客户端工具

**Windows:**
- 下载并安装MySQL命令行客户端
- 或安装完整的MySQL Server（包含客户端工具）

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mysql-client
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install mysql
```

### 3. 配置脚本

1. 配置文件：
```bash
    config.py
```

2. 编辑 `config.py` 文件，修改以下配置：

```python
DB_CONFIG = {
    'host': 'localhost',               # 数据库服务器地址
    'port': 3306,                      # 数据库端口
    'username': 'your_username',       # 数据库用户名
    'password': 'your_password',       # 数据库密码
    'database_names': [                # 要备份的数据库名列表
        'database1',
        'database2',
        'database3'
    ],
    'backup_dir': './backups'          # 备份存储目录
}

BACKUP_CONFIG = {
    'backup_times': [           # 备份时间列表（24小时制）
        '09:00',                # 早上9点
        '12:00',                # 中午12点
        '17:00',                # 下午5点
        '00:00'                 # 午夜12点
    ],
    'retention_days': 10,       # 备份文件保留天数
    'timeout_seconds': 3600,    # 备份超时时间（秒）
}
```

## 使用方法

### 运行脚本
```bash
python index.py
```

### 测试备份功能
如需立即测试备份功能，可以在 `index.py` 的main函数中取消注释以下行：
```python
# backup_manager.backup_database()
```

## 目录结构

脚本运行后会创建以下目录结构：

```
./backups/
├── logs/                              # 日志文件目录
│   └── backup_2024-07-16.log        # 每日日志文件
├── 2024-07-16/                       # 按日期组织的备份文件夹
│   ├── 0900/                         # 早上9点备份
│   │   ├── database1_backup_20240716_090000.sql
│   │   ├── database2_backup_20240716_090000.sql
│   │   └── ... (其他数据库备份文件)
│   ├── 1200/                         # 中午12点备份
│   │   ├── database1_backup_20240716_120000.sql
│   │   ├── database2_backup_20240716_120000.sql
│   │   └── ... (其他数据库备份文件)
│   ├── 1700/                         # 下午5点备份
│   │   └── ... (数据库备份文件)
│   └── 0000/                         # 午夜12点备份
│       └── ... (数据库备份文件)
├── 2024-07-17/                       # 下一天的备份
│   └── ... (4个时间点，每个时间点包含所有数据库备份文件)
└── ...
```

## 备份文件组织规则

**主文件夹命名格式**：`YYYY-MM-DD` （如：2024-07-16）

**时间子文件夹命名格式**：`HHMM` （如：0900, 1200, 1700, 0000）

**备份文件命名格式**：`{数据库名}_backup_{YYYYMMDD}_{HHMMSS}.sql`

例如2024年7月16日的备份结构：
```
./backups/2024-07-16/
├── 0900/                              # 早上9点备份
│   ├── database1_backup_20240716_090000.sql
│   ├── database2_backup_20240716_090000.sql
│   └── ... (其他数据库备份文件)
├── 1200/                              # 中午12点备份
│   ├── database1_backup_20240716_120000.sql
│   ├── database2_backup_20240716_120000.sql
│   └── ... (其他数据库备份文件)
├── 1700/                              # 下午5点备份
└── 0000/                              # 午夜12点备份
```

## 日志文件

- 日志文件位置：`{备份目录}/logs/backup_{YYYY-MM-DD}.log`
- 日志包含：备份开始/结束时间、文件大小、耗时、错误信息等
- 同时输出到控制台和日志文件

## 自动清理机制

- 脚本会在每次备份后自动检查并删除过期的备份文件夹
- 保留天数在 `config.py` 中的 `retention_days` 设置（默认10天）
- 超过保留期限的整个日期文件夹（包含该日的所有数据库备份）将被删除
- 删除操作会记录在日志中，显示删除的文件夹数量和文件数量

## 定时任务设置

脚本默认在每天四个时间点执行备份：09:00、12:00、17:00、00:00。要修改备份时间，请编辑 `config.py` 中的 `backup_times` 列表。

## 故障排除

### 1. 数据库连接失败
- 检查数据库服务器地址、端口是否正确
- 验证用户名和密码
- 确认数据库服务器允许远程连接
- 检查防火墙设置

### 2. 命令找不到错误
如果出现 `mysqldump` 或 `mysql` 命令找不到的错误：
- 确保已安装MySQL客户端工具
- 将MySQL客户端工具路径添加到系统PATH环境变量

### 3. 权限错误
- 确保Python脚本有权限写入备份目录
- 确保数据库用户有足够的权限执行备份操作

### 4. 磁盘空间不足
- 监控备份目录的磁盘空间
- 适当调整 `retention_days` 设置

## 作为系统服务运行

### Windows
可以使用任务计划程序或将脚本安装为Windows服务。

### Linux
可以创建systemd服务文件：

```ini
[Unit]
Description=MySQL Backup Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/script
ExecStart=/usr/bin/python3 /path/to/script/index.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 安全建议

1. **密码安全**：避免在配置文件中使用明文密码，考虑使用环境变量
2. **文件权限**：限制配置文件的读取权限
3. **网络安全**：使用SSL连接数据库（如果支持）
4. **备份加密**：对重要数据的备份文件进行加密存储

## 许可证

本项目采用MIT许可证。

## 支持

如有问题或建议，请联系开发者。 