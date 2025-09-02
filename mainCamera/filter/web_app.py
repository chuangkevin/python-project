"""
Fujifilm 軟片模擬 Web 界面
提供上傳照片並顯示所有軟片模擬結果的功能
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from PIL import Image
import uuid
import time
from threading import Thread

# 導入軟片模擬模組
from film_simulation import FujifilmSimulation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fujifilm_simulation_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大檔案大小

# 建立必要的資料夾
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# 允許的檔案格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# 全域軟片模擬器
film_sim = FujifilmSimulation()

# 處理狀態追蹤
processing_status = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image_with_simulations(image_path, session_id):
    """背景處理圖像的所有軟片模擬"""
    try:
        processing_status[session_id] = {
            'status': 'processing',
            'progress': 0,
            'results': {},
            'total': len(film_sim.get_available_simulations())
        }
        
        # 載入原始圖像
        original = cv2.imread(image_path)
        if original is None:
            processing_status[session_id]['status'] = 'error'
            processing_status[session_id]['error'] = '無法載入圖像'
            return
        
        # 調整圖像大小以提高處理速度
        height, width = original.shape[:2]
        if width > 1200:
            new_width = 1200
            new_height = int(height * (new_width / width))
            original = cv2.resize(original, (new_width, new_height))
        
        simulations = film_sim.get_available_simulations()
        
        for i, sim_name in enumerate(simulations):
            try:
                # 套用軟片模擬
                result = film_sim.apply(original, sim_name)
                
                # 轉換為 base64 以便傳送到前端
                _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 85])
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # 儲存結果
                processing_status[session_id]['results'][sim_name] = {
                    'image': img_base64,
                    'name': sim_name,
                    'description': get_simulation_description(sim_name)
                }
                
                # 更新進度
                processing_status[session_id]['progress'] = ((i + 1) / len(simulations)) * 100
                
            except Exception as e:
                print(f"處理 {sim_name} 時發生錯誤: {e}")
                continue
        
        # 加入原始圖像
        _, buffer = cv2.imencode('.jpg', original, [cv2.IMWRITE_JPEG_QUALITY, 85])
        original_base64 = base64.b64encode(buffer).decode('utf-8')
        
        processing_status[session_id]['results']['Original'] = {
            'image': original_base64,
            'name': 'Original',
            'description': '原始圖像'
        }
        
        processing_status[session_id]['status'] = 'completed'
        
    except Exception as e:
        processing_status[session_id]['status'] = 'error'
        processing_status[session_id]['error'] = str(e)

def get_simulation_description(sim_name):
    """取得軟片模擬的描述"""
    descriptions = {
        'PROVIA': '標準專業反轉片 - 平衡自然色彩，適合日常拍攝',
        'Velvia': '高飽和度風景片 - 鮮豔明亮，完美呈現自然風光',
        'ASTIA': '人像柔和片 - 優秀膚色表現，柔和自然',
        'Classic_Chrome': '經典正片風格 - 復古質感，紀實攝影首選',
        'Classic_Negative': 'SUPERIA底片風格 - 立體感強，生活記錄',
        'ETERNA': '電影膠片風格 - 電影級色彩，專業質感',
        'Nostalgic_Negative': '復古相冊風格 - 溫暖懷舊，琥珀色調',
        'REALA_ACE': '中性高對比 - 明亮自然，適合所有場景',
        'ACROS': '細緻黑白片 - 豐富層次，藝術創作',
        'Monochrome': '標準黑白 - 經典單色，簡約風格',
        'Sepia': '復古棕褐色 - 懷舊氛圍，古典美感'
    }
    return descriptions.get(sim_name, '軟片模擬效果')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '沒有選擇檔案'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '沒有選擇檔案'}), 400
    
    if file and allowed_file(file.filename):
        # 生成唯一的 session ID
        session_id = str(uuid.uuid4())
        
        # 儲存上傳的檔案
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 開始背景處理
        thread = Thread(target=process_image_with_simulations, args=(filepath, session_id))
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': '檔案上傳成功，開始處理...'
        })
    
    return jsonify({'error': '不支援的檔案格式'}), 400

@app.route('/status/<session_id>')
def get_status(session_id):
    if session_id in processing_status:
        return jsonify(processing_status[session_id])
    return jsonify({'error': '找不到處理狀態'}), 404

@app.route('/download/<session_id>/<sim_name>')
def download_image(session_id, sim_name):
    if session_id in processing_status and sim_name in processing_status[session_id]['results']:
        img_data = processing_status[session_id]['results'][sim_name]['image']
        img_bytes = base64.b64decode(img_data)
        
        return send_file(
            BytesIO(img_bytes),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f'{sim_name}_simulation.jpg'
        )
    
    return jsonify({'error': '找不到圖像'}), 404

if __name__ == '__main__':
    print("🎬 Fujifilm 軟片模擬 Web 服務啟動中...")
    print("📱 請開啟瀏覽器訪問: http://localhost:5000")
    print("📸 支援格式: JPG, PNG, GIF, BMP")
    print("💡 最大檔案大小: 16MB")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
