"""
Fujifilm 軟片模擬測試與示範程式

這個程式提供了多種方式來測試和使用 Fujifilm 軟片模擬：
1. 批次處理單張圖像
2. 建立軟片模擬比較圖
3. 即時預覽 (使用攝像頭)
4. 批次處理資料夾
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path
import argparse
from typing import List, Tuple

# 加入模組路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from film_simulation import FujifilmSimulation

class FilmSimulationDemo:
    """Fujifilm 軟片模擬示範程式"""
    
    def __init__(self):
        self.sim = FujifilmSimulation()
        self.available_sims = self.sim.get_available_simulations()
    
    def process_single_image(self, input_path: str, output_dir: str, 
                           simulations: List[str] = None):
        """
        處理單張圖像，套用指定的軟片模擬
        
        Args:
            input_path: 輸入圖像路徑
            output_dir: 輸出資料夾
            simulations: 要套用的軟片模擬列表，None 表示全部
        """
        if not os.path.exists(input_path):
            print(f"錯誤: 找不到檔案 {input_path}")
            return
        
        # 建立輸出資料夾
        os.makedirs(output_dir, exist_ok=True)
        
        # 載入圖像
        original = cv2.imread(input_path)
        if original is None:
            print(f"錯誤: 無法載入圖像 {input_path}")
            return
        
        # 取得檔案名稱 (不含副檔名)
        file_stem = Path(input_path).stem
        
        # 處理指定的軟片模擬
        if simulations is None:
            simulations = self.available_sims
        
        print(f"處理圖像: {input_path}")
        print(f"套用 {len(simulations)} 種軟片模擬...")
        
        for sim_name in simulations:
            if sim_name not in self.available_sims:
                print(f"警告: 軟片模擬 '{sim_name}' 不存在，跳過")
                continue
            
            try:
                # 套用軟片模擬
                result = self.sim.apply(original, sim_name)
                
                # 儲存結果
                output_path = os.path.join(output_dir, f"{file_stem}_{sim_name}.jpg")
                cv2.imwrite(output_path, result)
                print(f"  ✓ {sim_name} -> {output_path}")
                
            except Exception as e:
                print(f"  ✗ {sim_name} 處理失敗: {e}")
    
    def create_comparison_grid(self, input_path: str, output_path: str, 
                             simulations: List[str] = None, cols: int = 4):
        """
        建立軟片模擬比較圖
        
        Args:
            input_path: 輸入圖像路徑
            output_path: 輸出比較圖路徑
            simulations: 要比較的軟片模擬
            cols: 每行顯示的圖像數量
        """
        if not os.path.exists(input_path):
            print(f"錯誤: 找不到檔案 {input_path}")
            return
        
        # 載入原始圖像
        original = cv2.imread(input_path)
        if original is None:
            print(f"錯誤: 無法載入圖像 {input_path}")
            return
        
        if simulations is None:
            simulations = self.available_sims[:12]  # 限制為前12個
        
        # 調整圖像大小以適合網格
        target_size = (300, 200)
        original_resized = cv2.resize(original, target_size)
        
        # 建立標題圖像
        def create_titled_image(img: np.ndarray, title: str) -> np.ndarray:
            # 建立標題欄
            title_height = 30
            title_img = np.ones((title_height, img.shape[1], 3), dtype=np.uint8) * 255
            
            # 加入標題文字
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            color = (0, 0, 0)
            thickness = 1
            
            # 計算文字位置 (置中)
            text_size = cv2.getTextSize(title, font, font_scale, thickness)[0]
            text_x = (title_img.shape[1] - text_size[0]) // 2
            text_y = (title_height + text_size[1]) // 2
            
            cv2.putText(title_img, title, (text_x, text_y), font, font_scale, color, thickness)
            
            # 組合圖像和標題
            return np.vstack([title_img, img])
        
        # 處理所有圖像
        images = []
        
        # 加入原始圖像
        original_titled = create_titled_image(original_resized, "Original")
        images.append(original_titled)
        
        # 處理軟片模擬
        print(f"建立比較圖，包含 {len(simulations)} 種軟片模擬...")
        
        for sim_name in simulations:
            if sim_name not in self.available_sims:
                continue
                
            try:
                # 套用軟片模擬
                result = self.sim.apply(original, sim_name)
                result_resized = cv2.resize(result, target_size)
                result_titled = create_titled_image(result_resized, sim_name)
                images.append(result_titled)
                print(f"  ✓ {sim_name}")
                
            except Exception as e:
                print(f"  ✗ {sim_name} 處理失敗: {e}")
        
        # 建立網格
        rows = (len(images) + cols - 1) // cols
        
        # 補齊空白圖像
        while len(images) < rows * cols:
            blank = np.ones_like(images[0]) * 128
            images.append(blank)
        
        # 組合網格
        grid_rows = []
        for r in range(rows):
            row_images = images[r*cols:(r+1)*cols]
            grid_row = np.hstack(row_images)
            grid_rows.append(grid_row)
        
        final_grid = np.vstack(grid_rows)
        
        # 儲存結果
        cv2.imwrite(output_path, final_grid)
        print(f"比較圖已儲存至: {output_path}")
    
    def real_time_preview(self, camera_id: int = 0):
        """
        即時攝像頭預覽 (循環切換軟片模擬)
        
        Args:
            camera_id: 攝像頭 ID
        """
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"錯誤: 無法開啟攝像頭 {camera_id}")
            return
        
        current_sim_idx = 0
        sim_names = ["Original"] + self.available_sims
        
        print("即時預覽啟動!")
        print("按鍵操作:")
        print("  空白鍵: 切換軟片模擬")
        print("  's': 儲存當前畫面")
        print("  'q': 退出")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 套用當前軟片模擬
            current_sim = sim_names[current_sim_idx]
            if current_sim == "Original":
                display_frame = frame.copy()
            else:
                try:
                    display_frame = self.sim.apply(frame, current_sim)
                except:
                    display_frame = frame.copy()
            
            # 加入資訊文字
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(display_frame, f"Film Simulation: {current_sim}", 
                       (10, 30), font, 1, (0, 255, 0), 2)
            cv2.putText(display_frame, "Space: Next | S: Save | Q: Quit", 
                       (10, display_frame.shape[0] - 10), font, 0.6, (0, 255, 0), 1)
            
            cv2.imshow("Fujifilm Simulation Preview", display_frame)
            
            # 處理按鍵
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):  # 空白鍵
                current_sim_idx = (current_sim_idx + 1) % len(sim_names)
                print(f"切換至: {sim_names[current_sim_idx]}")
            elif key == ord('s'):  # 儲存
                filename = f"capture_{current_sim}_{frame_count:04d}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"已儲存: {filename}")
                frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
    
    def batch_process_folder(self, input_dir: str, output_dir: str, 
                           simulations: List[str] = None, 
                           extensions: List[str] = ['.jpg', '.jpeg', '.png', '.bmp']):
        """
        批次處理資料夾中的所有圖像
        
        Args:
            input_dir: 輸入資料夾
            output_dir: 輸出資料夾
            simulations: 要套用的軟片模擬
            extensions: 支援的圖像格式
        """
        if not os.path.exists(input_dir):
            print(f"錯誤: 找不到資料夾 {input_dir}")
            return
        
        # 尋找所有圖像檔案
        image_files = []
        for ext in extensions:
            pattern = f"*{ext}"
            image_files.extend(Path(input_dir).glob(pattern))
            pattern = f"*{ext.upper()}"
            image_files.extend(Path(input_dir).glob(pattern))
        
        if not image_files:
            print(f"在 {input_dir} 中找不到任何圖像檔案")
            return
        
        print(f"找到 {len(image_files)} 個圖像檔案")
        
        # 批次處理
        for i, img_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 處理: {img_path.name}")
            
            # 為每個圖像建立子資料夾
            img_output_dir = os.path.join(output_dir, img_path.stem)
            self.process_single_image(str(img_path), img_output_dir, simulations)
    
    def list_simulations(self):
        """列出所有可用的軟片模擬"""
        print("可用的 Fujifilm 軟片模擬:")
        print("=" * 50)
        
        descriptions = {
            'PROVIA': '標準專業反轉片 - 平衡自然色彩',
            'Velvia': '高飽和度風景片 - 鮮豔銳利',
            'ASTIA': '人像柔和片 - 柔和膚色表現',
            'Classic_Chrome': '20世紀雜誌風格 - 低飽和度硬調',
            'Classic_Negative': 'SUPERIA底片風格 - 立體感強',
            'ETERNA': '電影膠片風格 - 抑制飽和度',
            'Nostalgic_Negative': '復古相冊風格 - 琥珀高光',
            'REALA_ACE': '中性色彩高對比 - 適合所有主題',
            'ACROS': '細緻黑白片 - 豐富陰影細節',
            'Monochrome': '基礎黑白 - 標準轉換',
            'Sepia': '復古棕褐色 - 懷舊氛圍'
        }
        
        for i, sim_name in enumerate(self.available_sims, 1):
            desc = descriptions.get(sim_name, '無描述')
            print(f"{i:2d}. {sim_name:<18} - {desc}")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='Fujifilm 軟片模擬工具')
    parser.add_argument('mode', choices=['single', 'comparison', 'preview', 'batch', 'list'],
                       help='執行模式')
    parser.add_argument('-i', '--input', help='輸入檔案或資料夾路徑')
    parser.add_argument('-o', '--output', help='輸出檔案或資料夾路徑')
    parser.add_argument('-s', '--simulations', nargs='+', help='指定軟片模擬 (空格分隔)')
    parser.add_argument('-c', '--camera', type=int, default=0, help='攝像頭 ID (預設: 0)')
    parser.add_argument('--cols', type=int, default=4, help='比較圖每行圖像數 (預設: 4)')
    
    args = parser.parse_args()
    
    demo = FilmSimulationDemo()
    
    if args.mode == 'list':
        demo.list_simulations()
        
    elif args.mode == 'single':
        if not args.input or not args.output:
            print("錯誤: 單張處理模式需要 -i (輸入) 和 -o (輸出) 參數")
            return
        demo.process_single_image(args.input, args.output, args.simulations)
        
    elif args.mode == 'comparison':
        if not args.input or not args.output:
            print("錯誤: 比較圖模式需要 -i (輸入) 和 -o (輸出) 參數")
            return
        demo.create_comparison_grid(args.input, args.output, args.simulations, args.cols)
        
    elif args.mode == 'preview':
        demo.real_time_preview(args.camera)
        
    elif args.mode == 'batch':
        if not args.input or not args.output:
            print("錯誤: 批次處理模式需要 -i (輸入資料夾) 和 -o (輸出資料夾) 參數")
            return
        demo.batch_process_folder(args.input, args.output, args.simulations)


if __name__ == "__main__":
    # 如果沒有命令列參數，顯示互動式選單
    if len(sys.argv) == 1:
        demo = FilmSimulationDemo()
        
        print("=" * 60)
        print("🎬 Fujifilm 軟片模擬工具")
        print("=" * 60)
        
        while True:
            print("\n選擇操作模式:")
            print("1. 列出所有軟片模擬")
            print("2. 處理單張圖像")
            print("3. 建立比較圖")
            print("4. 即時預覽 (攝像頭)")
            print("5. 批次處理資料夾")
            print("0. 退出")
            
            choice = input("\n請選擇 (0-5): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                demo.list_simulations()
            elif choice == '2':
                input_path = input("輸入圖像路徑: ").strip()
                output_dir = input("輸出資料夾: ").strip()
                demo.process_single_image(input_path, output_dir)
            elif choice == '3':
                input_path = input("輸入圖像路徑: ").strip()
                output_path = input("輸出比較圖路徑: ").strip()
                demo.create_comparison_grid(input_path, output_path)
            elif choice == '4':
                print("啟動即時預覽...")
                demo.real_time_preview()
            elif choice == '5':
                input_dir = input("輸入資料夾: ").strip()
                output_dir = input("輸出資料夾: ").strip()
                demo.batch_process_folder(input_dir, output_dir)
            else:
                print("無效選擇，請重試")
    else:
        main()
