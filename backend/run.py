from flask import Flask
from flask_cors import CORS
from app.routes import api_bp

# 创建 Flask 应用实例
app = Flask(__name__)

# 配置 CORS，允许来自 http://localhost:8080 (我们的前端地址) 的请求
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

# 注册我们创建的蓝图
app.register_blueprint(api_bp)

# 当直接运行这个文件时，启动服务器
if __name__ == '__main__':
    # debug=True 表示开启调试模式，代码修改后服务器会自动重启
    # port=5000 指定服务器在 5000 端口运行
    app.run(debug=True, port=5000)