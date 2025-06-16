from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import uuid
import json
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
CORS(app)  # 允许跨域访问

# 房号列表
ALL_ROOMS = ['101', '201', '202', '203', '301']

# 初始化数据存储
data = {
    'available_rooms': ALL_ROOMS.copy(),  # 可用房号
    'drawn_rooms': {},  # 已抽取的房号（用户ID:房号）
    'users': {}  # 用户参与记录（用户ID:抽取时间）
}

# 保存数据到文件
def save_data():
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

# 从文件加载数据
def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            global data
            data = json.load(f)
    except FileNotFoundError:
        save_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        save_data()

# 初始化时加载数据
load_data()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        user_id = request.headers.get('User-Agent') + str(datetime.now())
        
        return jsonify({
            'userHasDrawn': user_id in data['users'],
            'userRoom': data['drawn_rooms'].get(user_id) if user_id in data['users'] else None,
            'availableRooms': data['available_rooms']
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/draw', methods=['POST'])
def draw():
    try:
        user_id = request.headers.get('User-Agent') + str(datetime.now())
        
        # 检查用户是否已抽取
        if user_id in data['users']:
            return jsonify({
                'success': False,
                'message': '您已经参与过本次抽奖活动。'
            })
        
        # 检查是否有可用房号
        if not data['available_rooms']:
            return jsonify({
                'success': False,
                'message': '太遗憾了，所有房号已被抽完！'
            })
        
        # 随机抽取一个房号
        room = data['available_rooms'][0]
        
        # 更新数据
        data['available_rooms'].remove(room)
        data['drawn_rooms'][user_id] = room
        data['users'][user_id] = datetime.now().isoformat()
        
        # 保存数据
        save_data()
        
        return jsonify({
            'success': True,
            'room': room,
            'availableRooms': data['available_rooms']
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    try:
        print("Starting server...")
        print("Access the application at http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")
