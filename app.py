from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import datetime
from werkzeug.exceptions import HTTPException

app = Flask(__name__, static_folder='static')
CORS(app)

# 定义数据文件路径
DATA_FILE = 'static/data.json'

# 初始化数据结构
data = {
    "available_rooms": ["101", "201", "202", "203", "301"],
    "drawn_rooms": {},
    "users": {}
}

# 保存数据到文件
def save_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 从文件加载数据
def load_data():
    global data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data.update(json.load(f))
        except Exception as e:
            print(f"Error loading data: {e}")
    else:
        save_data()

# 初始化数据
load_data()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        return jsonify({
            'availableRooms': data['available_rooms'],
            'drawnRooms': list(data['drawn_rooms'].values()),
            'isLotteryOver': len(data['available_rooms']) == 0,
            'totalRooms': 5,
            'remainingRooms': len(data['available_rooms'])
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/draw', methods=['POST'])
def draw():
    try:
        # 获取用户设备指纹
        user_id = request.headers.get('User-Agent') + str(datetime.datetime.now())
        
        # 检查用户是否已抽取
        if user_id in data['users']:
            return jsonify({
                'error': '您已参与过本次抽奖，不能重复抽取。'
            }), 403
        
        # 检查是否有可用房号
        if not data['available_rooms']:
            return jsonify({
                'error': '所有房号已被抽完！'
            }), 403
        
        # 随机抽取一个房号
        room = data['available_rooms'][0]
        
        # 更新数据
        data['available_rooms'].remove(room)
        data['drawn_rooms'][user_id] = room
        data['users'][user_id] = datetime.datetime.now().isoformat()
        
        # 保存数据
        save_data()
        
        return jsonify({
            'success': True,
            'room': room,
            'message': f'恭喜您！抽中了 {room} 房间！'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    try:
        # 重置数据
        data['available_rooms'] = ["101", "201", "202", "203", "301"]
        data['drawn_rooms'] = {}
        data['users'] = {}
        
        # 保存重置后的数据
        save_data()
        
        return jsonify({
            'success': True,
            'message': '抽奖已重置，所有房间已恢复可用状态。'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "error": e.name,
        "description": e.description
    })
    response.content_type = "application/json"
    return response

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("Starting server...")
    print("Access the application at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
