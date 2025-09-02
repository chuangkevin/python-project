"""
簡化版軟片模擬器 - 自動套用全部效果
模仿原本 web_app.py 的行為，上傳後自動處理所有軟片效果
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

# 導入增強軟片模擬模組
try:
    from enhanced_film_simulation import EnhancedFilmSimulation
except ImportError:
    from film_simulation import FilmSimulation as EnhancedFilmSimulation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enhanced_film_simulation_key'
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

# 全域增強軟片模擬器
try:
    enhanced_film_sim = EnhancedFilmSimulation()
    print("✅ 增強軟片模擬引擎載入成功")
except Exception as e:
    print(f"❌ 載入增強軟片模擬引擎失敗: {e}")
    exit(1)

# 處理狀態追蹤
processing_status = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image_with_all_simulations(image_path, session_id):
    """背景處理圖像的所有增強軟片模擬"""
    try:
        # 獲取所有可用的軟片模擬
        available_sims = enhanced_film_sim.get_available_simulations()
        all_simulations = []
        for category_sims in available_sims.values():
            all_simulations.extend([sim['name'] for sim in category_sims])
        
        processing_status[session_id] = {
            'status': 'processing',
            'progress': 0,
            'results': {},
            'total': len(all_simulations)
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
        
        for i, sim_name in enumerate(all_simulations):
            try:
                # 套用軟片模擬
                result = enhanced_film_sim.apply_simulation(original, sim_name)
                
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
                processing_status[session_id]['progress'] = ((i + 1) / len(all_simulations)) * 100
                
            except Exception as e:
                print(f"處理 {sim_name} 時發生錯誤: {e}")
                continue
        
        # 加入原始圖像
        _, buffer = cv2.imencode('.jpg', original, [cv2.IMWRITE_JPEG_QUALITY, 85])
        original_base64 = base64.b64encode(buffer).decode('utf-8')
        
        processing_status[session_id]['results']['原始圖像'] = {
            'image': original_base64,
            'name': '原始圖像',
            'description': '未套用任何軟片效果的原始照片'
        }
        
        processing_status[session_id]['status'] = 'completed'
        
    except Exception as e:
        processing_status[session_id]['status'] = 'error'
        processing_status[session_id]['error'] = str(e)

def get_simulation_description(sim_name):
    """取得軟片模擬的描述"""
    descriptions = {
        # Fujifilm 經典
        'PROVIA': '標準專業反轉片 - 平衡自然色彩，適合日常拍攝',
        'VELVIA': '高飽和度風景片 - 鮮豔明亮，完美呈現自然風光',
        'ASTIA': '人像柔和片 - 優秀膚色表現，柔和自然',
        'CLASSIC_CHROME': '經典正片風格 - 復古質感，紀實攝影首選',
        'CLASSIC_NEGATIVE': 'SUPERIA底片風格 - 立體感強，生活記錄',
        'ETERNA': '電影膠片風格 - 電影級色彩，專業質感',
        'NOSTALGIC_NEGATIVE': '復古相冊風格 - 溫暖懷舊，琥珀色調',
        'REALA_ACE': '中性高對比 - 明亮自然，適合所有場景',
        'ACROS': '細緻黑白片 - 豐富層次，藝術創作',
        'MONOCHROME': '標準黑白 - 經典單色，簡約風格',
        'SEPIA': '復古棕褐色 - 懷舊氛圍，古典美感',
        
        # Kodak 經典
        'KODAK_PORTRA_400': 'Kodak Portra 400 - 自然膚色，專業人像之選',
        'KODAK_PORTRA_400_V2': 'Kodak Portra 400 V2 - 增強版，更佳的動態範圍',
        'KODAK_PORTRA_800': 'Kodak Portra 800 - 高感光度人像膠片',
        'KODACHROME_64': 'Kodachrome 64 - 傳奇彩色膠片，色彩飽滿',
        'KODAK_GOLD_100': 'Kodak Gold 100 - 經典日常膠片，溫暖色調',
        'KODAK_GOLD_200': 'Kodak Gold 200 - 萬用膠片，平衡色彩',
        'KODAK_ULTRAMAX_400': 'Kodak UltraMax 400 - 鮮豔色彩，適合戶外',
        'KODAK_COLORPLUS_200': 'Kodak ColorPlus 200 - 入門膠片，經濟實惠',
        'KODAK_TRI_X_400': 'Kodak Tri-X 400 - 經典黑白膠片，街拍首選',
        
        # Fujicolor 系列
        'FUJICOLOR_C200': 'Fujicolor C200 - 日系溫暖色調，生活記錄',
        'FUJICOLOR_SUPERIA_400': 'Fujicolor Superia 400 - 鮮豔色彩，戶外專用',
        'FUJICOLOR_SUPERIA_800': 'Fujicolor Superia 800 - 高感光度，室內拍攝',
        'FUJICOLOR_NATURA_1600': 'Fujicolor Natura 1600 - 極高感光度，夜拍專用',
        
        # 電影膠片
        'CINESTILL_800T': 'CineStill 800T - 電影膠片，霓虹燈效果',
        'KODAK_VISION3_50D': 'Kodak Vision3 50D - 專業電影膠片，日光版',
        'KODAK_VISION3_250D': 'Kodak Vision3 250D - 電影膠片，平衡日光',
        'KODAK_VISION3_500T': 'Kodak Vision3 500T - 電影膠片，鎢絲燈版',
        
        # 復古風格
        'VINTAGE_1970S': '70年代復古 - 溫暖褪色，懷舊氛圍',
        'VINTAGE_1980S': '80年代復古 - 鮮豔對比，時尚感',
        'INSTANT_FILM': '拍立得風格 - 柔和色調，溫暖懷舊',
        'FADED_FILM': '褪色膠片 - 時光流逝的美感',
        
        # 特殊效果
        'REDSCALE_FILM': '紅片效果 - 溫暖紅調，創意表現',
        'CROSS_PROCESSED': '交叉沖洗 - 異常色彩，藝術效果',
        'INFRARED_FILM': '紅外線膠片 - 超現實效果，黑白紅外',
        'BLEACH_BYPASS': '漂白旁路 - 高對比，銀色調',
        'SEPIA_WARM': '暖調棕褐 - 古典懷舊，溫暖色調',
        'SEPIA_COOL': '冷調棕褐 - 古典懷舊，冷色調'
    }
    return descriptions.get(sim_name, f'{sim_name} - 專業軟片模擬效果')

@app.route('/')
def index():
    return render_template('simple_all_effects.html')

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
        
        # 開始背景處理 - 自動套用所有軟片效果
        thread = Thread(target=process_image_with_all_simulations, args=(filepath, session_id))
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': '檔案上傳成功，開始處理所有 41 種軟片效果...'
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
            download_name=f'{sim_name}_enhanced_simulation.jpg'
        )
    
    return jsonify({'error': '找不到圖像'}), 404

if __name__ == '__main__':
    print("🎬 增強版軟片模擬器 - 全效果模式啟動中...")
    print("📱 請開啟瀏覽器訪問: http://localhost:5001")
    print("📸 支援格式: JPG, PNG, GIF, BMP")
    print("💡 最大檔案大小: 16MB")
    print("🎞️ 自動套用全部 41 種軟片效果")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
