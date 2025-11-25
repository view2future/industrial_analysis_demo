from flask import send_from_directory, send_file
import os

# 添加对Vue.js构建文件的处理
@app.route('/assets/<path:filename>')
def serve_static_asset(filename):
    """Serve Vue.js built assets."""
    return send_from_directory('frontend-vue/dist/assets', filename)

# 为Vue Router的history模式提供支持
@app.route('/<path:path>')
def serve_vue_routes(path):
    """Serve Vue.js app for client-side routing, except API routes."""
    # 不要拦截API路由
    if path.startswith('api/'):
        # 这个路由实际上不会匹配，因为API路由有特定定义
        # 所以我们不需要特别处理
        pass
    
    # 如果是静态资源，返回特定的静态文件
    if path.startswith('assets/'):
        return serve_static_asset(path[8:])  # 去掉'assets/'前缀
    
    # 其他情况返回Vue.js的index.html，让前端路由处理
    try:
        return send_file('frontend-vue/dist/index.html')
    except:
        # 如果构建文件不存在，返回原始的Jinja2模板
        if path.startswith('login') or path == 'login':
            return login()
        elif path.startswith('register') or path == 'register':
            return register()
        else:
            # 对于其他路径，返回到主页
            return index()

# 默认根路径 - 如果没有构建的Vue应用，使用原来的路由
@app.route('/')
def index_or_serve_vue():
    """Serve Vue.js app if built, otherwise serve original Flask app."""
    # 检查是否有构建的Vue应用
    vue_index_path = os.path.join(os.path.dirname(__file__), 'frontend-vue', 'dist', 'index.html')
    
    if os.path.exists(vue_index_path):
        try:
            return send_file(vue_index_path)
        except:
            # 如果无法发送Vue文件，则使用原来的Flask路由
            return index()
    else:
        # 没有构建的Vue应用，使用原来的Flask应用
        return index()