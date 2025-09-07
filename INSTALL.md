# 安装指南

## 快速开始

1. **克隆或下载项目**
   ```bash
   git clone <your-repo-url>
   cd mysql-backup-script
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置数据库连接**
   ```bash
   cp config.example.py config.py
   ```
   然后编辑 `config.py` 文件，填入你的数据库连接信息。

4. **测试连接**
   ```bash
   python test_connection.py
   ```

5. **运行备份脚本**
   ```bash
   python index.py
   ```

## 配置说明

### 数据库配置
- `host`: 数据库服务器地址
- `port`: 数据库端口（默认3306）
- `username`: 数据库用户名
- `password`: 数据库密码
- `database_names`: 要备份的数据库列表
- `backup_dir`: 备份文件存储目录

### 备份配置
- `backup_times`: 备份时间点列表
- `retention_days`: 备份文件保留天数
- `timeout_seconds`: 备份超时时间

## 注意事项

1. 确保数据库用户有足够的权限执行备份操作
2. 确保备份目录有足够的磁盘空间
3. 建议在测试环境先验证配置正确性
4. 定期检查备份文件是否正常生成

## 故障排除

如果遇到问题，请检查：
1. 数据库连接信息是否正确
2. 网络连接是否正常
3. 数据库服务是否运行
4. 用户权限是否足够
5. 磁盘空间是否充足
