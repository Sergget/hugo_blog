# 1. 检查导航数据是否存在
node .\scripts\check-books-index.js

# 2. 把每本书构建到 static/books/<slug>（生成产物，不进 git）
Get-ChildItem books -Directory | ForEach-Object {
    npx honkit build $_.FullName "../../static/books/$($_.Name)"
}

# 3. 启动 Hugo 本地服务器（含草稿、热重载）
hugo server -D -F