from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import datetime
import random
from werkzeug.exceptions import HTTPException

app = Flask(__name__, static_folder='static')
CORS(app)

# 定义数据文件路径
DATA_FILE = 'static/data.json'

# 初始化数据结构
data = {
    "available_rooms": ["101", "201", "202", "203", "301"],
    "drawn_rooms": {},
    "users": {},
    "participants": [
        {"name": "梓恒", "participated": False},
        {"name": "航航", "participated": False},
        {"name": "一鸣", "participated": False},
        {"name": "康康", "participated": False},
        {"name": "凯睿", "participated": False}
    ]
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
                loaded_data = json.load(f)
                # 确保数据结构完整
                if 'participants' not in loaded_data:
                    loaded_data['participants'] = data['participants']
                data.update(loaded_data)
        except Exception as e:
            print(f"Error loading data: {e}")
    else:
        save_data()

# 初始化数据
load_data()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/index.html')
def index_html():
    return app.send_static_file('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        return jsonify({
            'available_rooms': data['available_rooms'],
            'drawn_rooms': data['drawn_rooms'],  # 确保是对象格式
            'isLotteryOver': len(data['available_rooms']) == 0,
            'totalRooms': 5,
            'remainingRooms': len(data['available_rooms']),
            'participants': data['participants']
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/draw', methods=['POST'])
def draw():
    try:
        request_data = request.json
        participant_name = request_data.get('participantName')
        
        participant = next((p for p in data['participants'] if p['name'] == participant_name), None)
        if not participant:
            return jsonify({
                'error': f'无效的参与者名称: {participant_name}'
            }), 403
        
        if participant['participated']:
            return jsonify({
                'error': f'{participant_name} 已经参与过抽奖'
            }), 403
        
        if not data['available_rooms']:
            return jsonify({
                'error': '所有房号已被抽完！'
            }), 403
        
        # 随机选择一个房间
        room = random.choice(data['available_rooms'])
        
        data['available_rooms'].remove(room)
        data['drawn_rooms'][participant_name] = room
        data['users'][participant_name] = datetime.datetime.now().isoformat()
        participant['participated'] = True
        
        save_data()
        
        return jsonify({
            'success': True,
            'room': room,
            'message': f'恭喜 {participant_name}！抽中了 {room} 房间！'
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
        for participant in data['participants']:
            participant['participated'] = False
        
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
