# Student Package System

## 簡介
Student Package System 是一個用於管理宿舍包裹的系統，包含管理者頁面和學生簽收頁面。管理者可以添加包裹並查看待簽收包裹，學生可以查詢並簽收自己的包裹。

## 技術棧
**後端**: Flask, MySQL

**前端**: Vue 3, Axios, Vue Router

## 安裝與執行
### 後端設置
1. 安裝 Python ：
```
cd backend
pip install -r requirements.txt
```
2. 配置 MySQL 資料庫：
   - 新增`backend/db_config.py` 中的資料庫配置
```
DB_CONFIG = {
    'host': 'locolhost',   # 或你的 MySQL 主機 IP
    'user': 'username',
    'password': 'password',
    'database': 'database name'
}
```
- 確保資料庫中已存在 student_list 和 packages 表。
1. 啟動 Flask 後端： `python app.py`

### 前端設置
1. 安裝Node.js：
```
cd frontend
npm install
```
2. 啟動 Vue 前端： `npm run serve`
3. 訪問網頁
   - 管理者頁面: http://localhost/admin
   - 學生簽收頁面: http://localhost/pickup

## 功能
- 管理者頁面:
  - 查看學生列表
  - 添加包裹
  - 查看待簽收包裹
- 學生簽收頁面:
  - 查詢待簽收包裹
  - 簽收包裹