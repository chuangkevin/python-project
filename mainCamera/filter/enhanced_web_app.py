"""
增強版軟片模擬 Web 應用程式
Enhanced Film Simulation Web App
"""

from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
from PIL import Image
import base64
import io
import os
import uuid
from werkzeug.utils import secure_filename
import threading
import time

# 導入增強軟片模擬引擎
try:
    from enhanced_film_simulation import EnhancedFilmSimulation
    print("✅ 增強軟片模擬引擎載入成功")
except ImportError:
    # 後備到原始版本
    from film_simulation import FilmSimulation as EnhancedFilmSimulation
    print("⚠️ 使用原始軟片模擬引擎")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 全局變數
processing_status = {}
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'

# 確保資料夾存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# 初始化軟片模擬引擎
film_engine = EnhancedFilmSimulation()

def allowed_file(filename):
    """檢查檔案類型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def process_image_with_simulation(image_path, simulation, job_id):
    """處理圖像的背景任務"""
    try:
        processing_status[job_id] = {'status': 'processing', 'progress': 0, 'message': f'正在套用 {simulation} 效果...'}
        
        # 載入圖像
        img = cv2.imread(image_path)
        if img is None:
            processing_status[job_id] = {'status': 'error', 'message': '無法載入圖像'}
            return
        
        processing_status[job_id]['progress'] = 20
        
        # 套用軟片模擬
        result = film_engine.apply_simulation(img, simulation)
        processing_status[job_id]['progress'] = 80
        
        # 轉換為 base64
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 95])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        processing_status[job_id] = {
            'status': 'completed',
            'progress': 100,
            'result': img_base64,
            'simulation': simulation,
            'message': '處理完成'
        }
        
    except Exception as e:
        processing_status[job_id] = {'status': 'error', 'message': str(e)}

def process_multiple_simulations(image_path, simulations, job_id):
    """處理多種軟片模擬的背景任務"""
    try:
        total_sims = len(simulations)
        results = {}
        
        # 載入圖像
        img = cv2.imread(image_path)
        if img is None:
            processing_status[job_id] = {'status': 'error', 'message': '無法載入圖像'}
            return
        
        for i, simulation in enumerate(simulations):
            processing_status[job_id] = {
                'status': 'processing', 
                'progress': int((i / total_sims) * 100),
                'message': f'正在處理 {simulation} ({i+1}/{total_sims})...'
            }
            
            try:
                # 套用軟片模擬
                result = film_engine.apply_simulation(img, simulation)
                
                # 轉換為 base64
                _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 85])
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                results[simulation] = img_base64
                
            except Exception as e:
                print(f"處理 {simulation} 時發生錯誤: {e}")
                results[simulation] = None
        
        processing_status[job_id] = {
            'status': 'completed',
            'progress': 100,
            'results': results,
            'message': f'成功處理 {len([r for r in results.values() if r is not None])}/{total_sims} 種效果'
        }
        
    except Exception as e:
        processing_status[job_id] = {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    """主頁面"""
    return render_template('enhanced_index.html')

@app.route('/get_simulations')
def get_simulations():
    """獲取所有可用的軟片模擬"""
    try:
        simulations = film_engine.get_available_simulations()
        
        # 按類別組織
        categories = {
            'Fujifilm 經典': [],
            'Kodak 經典': [],
            'Fujicolor 系列': [],
            '電影膠片': [],
            '復古風格': [],
            '特殊效果': []
        }
        
        for sim_name, description in simulations.items():
            if any(x in sim_name for x in ['PROVIA', 'VELVIA', 'ASTIA', 'CLASSIC', 'PRO_NEG', 'ETERNA', 'ACROS', 'MONO']):
                categories['Fujifilm 經典'].append({'name': sim_name, 'description': description})
            elif 'KODAK' in sim_name:
                categories['Kodak 經典'].append({'name': sim_name, 'description': description})
            elif 'FUJICOLOR' in sim_name or 'REALA' in sim_name:
                categories['Fujicolor 系列'].append({'name': sim_name, 'description': description})
            elif any(x in sim_name for x in ['CINESTILL', 'VISION']):
                categories['電影膠片'].append({'name': sim_name, 'description': description})
            elif any(x in sim_name for x in ['VINTAGE', 'NOSTALGIC', 'SUMMER', 'CALIFORNIA', 'PACIFIC', 'BRONZE']):
                categories['復古風格'].append({'name': sim_name, 'description': description})
            else:
                categories['特殊效果'].append({'name': sim_name, 'description': description})
        
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """處理檔案上傳"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        file = request.files['file']
        simulation = request.form.get('simulation', 'KODAK_PORTRA_400')
        
        if file.filename == '':
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        if file and allowed_file(file.filename):
            # 生成唯一檔名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            # 生成任務 ID
            job_id = str(uuid.uuid4())
            
            # 檢查是否要處理全部效果
            if simulation == 'ALL_EFFECTS':
                # 使用批次處理邏輯
                all_simulations = []
                for category_sims in film_engine.get_available_simulations().values():
                    all_simulations.extend([sim['name'] for sim in category_sims])
                
                thread = threading.Thread(
                    target=process_multiple_simulations, 
                    args=(filepath, all_simulations, job_id)
                )
                thread.start()
                
                return jsonify({'job_id': job_id, 'message': '檔案上傳成功，開始處理所有軟片效果...'})
            else:
                # 單一效果處理
                thread = threading.Thread(
                    target=process_image_with_simulation, 
                    args=(filepath, simulation, job_id)
                )
                thread.start()
                
                return jsonify({'job_id': job_id, 'message': '檔案上傳成功，開始處理...'})
        
        return jsonify({'error': '不支援的檔案格式'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch_upload', methods=['POST'])
def batch_upload():
    """批次處理上傳"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        file = request.files['file']
        selected_simulations = request.form.getlist('simulations')
        
        if not selected_simulations:
            # 默認使用熱門的軟片模擬
            selected_simulations = [
                'KODAK_PORTRA_400', 'VELVIA', 'KODACHROME_64', 
                'CLASSIC_CHROME', 'CINESTILL_800T', 'FUJICOLOR_C200'
            ]
        
        if file.filename == '':
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        if file and allowed_file(file.filename):
            # 生成唯一檔名
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            # 生成任務 ID
            job_id = str(uuid.uuid4())
            
            # 啟動背景處理
            thread = threading.Thread(
                target=process_multiple_simulations, 
                args=(filepath, selected_simulations, job_id)
            )
            thread.start()
            
            return jsonify({
                'job_id': job_id, 
                'message': f'檔案上傳成功，開始處理 {len(selected_simulations)} 種效果...',
                'total_simulations': len(selected_simulations)
            })
        
        return jsonify({'error': '不支援的檔案格式'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<job_id>')
def check_status(job_id):
    """檢查處理狀態"""
    if job_id in processing_status:
        return jsonify(processing_status[job_id])
    else:
        return jsonify({'status': 'not_found', 'message': '任務不存在'}), 404

@app.route('/download/<job_id>')
def download_result(job_id):
    """下載處理結果"""
    if job_id in processing_status and processing_status[job_id]['status'] == 'completed':
        try:
            result_data = processing_status[job_id]['result']
            simulation_name = processing_status[job_id]['simulation']
            
            # 解碼 base64 圖像
            img_data = base64.b64decode(result_data)
            
            # 創建檔案響應
            return send_file(
                io.BytesIO(img_data),
                mimetype='image/jpeg',
                as_attachment=True,
                download_name=f'film_simulation_{simulation_name}_{job_id[:8]}.jpg'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': '結果不可用'}), 404

@app.route('/preview')
def preview():
    """預覽頁面"""
    return render_template('preview.html')

@app.route('/about')
def about():
    """關於頁面"""
    return render_template('about.html')

if __name__ == '__main__':
    print("🎬 啟動增強版軟片模擬 Web 應用程式...")
    print(f"🎞️ 支援 {len(film_engine.get_available_simulations())} 種軟片效果")
    print("🌐 訪問 http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
