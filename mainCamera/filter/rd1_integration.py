"""
Fujifilm 軟片模擬 - RD-1 相機整合模組

這個模組專為您的 Raspberry Pi 雙螢幕相機專案設計，
可以輕鬆整合到現有的相機系統中。
"""

import os
import sys
from typing import Optional, Union, List
import time

# 嘗試導入所需的模組
try:
    import cv2
    import numpy as np
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("警告: OpenCV 或 NumPy 未安裝，部分功能將不可用")

class RD1FilmSimulation:
    """
    RD-1 相機軟片模擬處理器
    專為 Raspberry Pi 雙螢幕相機專案設計的輕量級版本
    """
    
    def __init__(self):
        """初始化軟片模擬器"""
        self.current_simulation = "PROVIA"  # 預設軟片
        self.simulations = {
            'PROVIA': {
                'name': 'PROVIA',
                'description': '標準專業反轉片',
                'icon': 'STD'
            },
            'Velvia': {
                'name': 'Velvia', 
                'description': '高飽和度風景片',
                'icon': 'VIV'
            },
            'ASTIA': {
                'name': 'ASTIA',
                'description': '人像柔和片', 
                'icon': 'AST'
            },
            'Classic_Chrome': {
                'name': 'Classic Chrome',
                'description': '經典正片',
                'icon': 'CHR'
            },
            'Classic_Negative': {
                'name': 'Classic Negative', 
                'description': '經典負片',
                'icon': 'NEG'
            },
            'ETERNA': {
                'name': 'ETERNA',
                'description': '電影膠片',
                'icon': 'ETN'
            },
            'ACROS': {
                'name': 'ACROS',
                'description': '細緻黑白',
                'icon': 'ACR'
            },
            'Monochrome': {
                'name': 'Monochrome',
                'description': '標準黑白',
                'icon': 'B&W'
            },
            'Sepia': {
                'name': 'Sepia',
                'description': '復古棕褐',
                'icon': 'SEP'
            }
        }
        
        # 軟片模擬清單 (循環切換用)
        self.simulation_list = list(self.simulations.keys())
        self.current_index = 0
        
        # 載入完整的軟片模擬引擎 (如果可用)
        self.full_engine = None
        if CV2_AVAILABLE:
            try:
                from .film_simulation import FujifilmSimulation
                self.full_engine = FujifilmSimulation()
                print("✓ 完整軟片模擬引擎已載入")
            except ImportError:
                print("⚠ 無法載入完整軟片模擬引擎，使用基礎模式")
    
    def get_current_simulation_info(self) -> dict:
        """取得當前軟片模擬資訊"""
        sim_info = self.simulations[self.current_simulation].copy()
        sim_info['key'] = self.current_simulation
        sim_info['index'] = self.current_index
        sim_info['total'] = len(self.simulation_list)
        return sim_info
    
    def get_simulation_icon(self) -> str:
        """取得當前軟片模擬的圖示文字 (用於 RD-1 錶盤顯示)"""
        return self.simulations[self.current_simulation]['icon']
    
    def get_simulation_name(self) -> str:
        """取得當前軟片模擬名稱"""
        return self.simulations[self.current_simulation]['name']
    
    def next_simulation(self) -> dict:
        """切換到下一個軟片模擬"""
        self.current_index = (self.current_index + 1) % len(self.simulation_list)
        self.current_simulation = self.simulation_list[self.current_index]
        return self.get_current_simulation_info()
    
    def previous_simulation(self) -> dict:
        """切換到上一個軟片模擬"""
        self.current_index = (self.current_index - 1) % len(self.simulation_list)
        self.current_simulation = self.simulation_list[self.current_index]
        return self.get_current_simulation_info()
    
    def set_simulation(self, simulation_name: str) -> bool:
        """
        設定指定的軟片模擬
        
        Args:
            simulation_name: 軟片模擬名稱
            
        Returns:
            bool: 設定是否成功
        """
        if simulation_name in self.simulations:
            self.current_simulation = simulation_name
            self.current_index = self.simulation_list.index(simulation_name)
            return True
        return False
    
    def apply_simulation(self, image_data, output_path: Optional[str] = None):
        """
        套用軟片模擬到圖像
        
        Args:
            image_data: 圖像資料 (可以是檔案路徑、numpy array 或 PIL Image)
            output_path: 輸出路徑 (可選)
            
        Returns:
            處理後的圖像資料
        """
        if not CV2_AVAILABLE or self.full_engine is None:
            print(f"⚠ 軟片模擬引擎不可用，返回原始圖像 (標記: {self.current_simulation})")
            return image_data
        
        try:
            # 套用軟片模擬
            result = self.full_engine.apply(image_data, self.current_simulation)
            
            # 如果指定輸出路徑，儲存圖像
            if output_path:
                cv2.imwrite(output_path, result)
                print(f"✓ 軟片模擬 {self.current_simulation} 已套用並儲存至 {output_path}")
            
            return result
            
        except Exception as e:
            print(f"✗ 軟片模擬處理失敗: {e}")
            return image_data
    
    def get_all_simulations(self) -> List[dict]:
        """取得所有軟片模擬的資訊列表"""
        return [
            {
                'key': key,
                'name': info['name'],
                'description': info['description'],
                'icon': info['icon']
            }
            for key, info in self.simulations.items()
        ]
    
    def create_simulation_gauge_values(self) -> List[str]:
        """
        為 RD-1 錶盤系統建立軟片模擬選項
        返回適合錶盤顯示的短標籤列表
        """
        return [info['icon'] for info in self.simulations.values()]


class RD1CameraIntegration:
    """
    RD-1 相機系統整合類別
    提供軟片模擬與相機系統的完整整合
    """
    
    def __init__(self):
        """初始化相機整合系統"""
        self.film_sim = RD1FilmSimulation()
        self.photo_count = 0
        self.base_output_dir = "captured_photos"
        
        # 建立輸出資料夾
        os.makedirs(self.base_output_dir, exist_ok=True)
        
        print("🎬 RD-1 軟片模擬系統已初始化")
        print(f"📁 輸出資料夾: {self.base_output_dir}")
    
    def take_photo_with_simulation(self, image_data, metadata: dict = None) -> str:
        """
        拍攝照片並套用當前軟片模擬
        
        Args:
            image_data: 圖像資料
            metadata: 相機元資料 (ISO, 光圈, 快門等)
            
        Returns:
            str: 儲存的檔案路徑
        """
        # 生成檔案名稱
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        sim_name = self.film_sim.current_simulation
        self.photo_count += 1
        
        filename = f"RD1_{timestamp}_{sim_name}_{self.photo_count:04d}.jpg"
        output_path = os.path.join(self.base_output_dir, filename)
        
        # 套用軟片模擬並儲存
        result = self.film_sim.apply_simulation(image_data, output_path)
        
        # 記錄拍攝資訊
        print(f"📸 拍攝完成: {filename}")
        print(f"🎬 軟片模擬: {self.film_sim.get_simulation_name()}")
        if metadata:
            print(f"📊 參數: {metadata}")
        
        return output_path
    
    def cycle_film_simulation(self, direction: str = "next") -> dict:
        """
        循環切換軟片模擬
        
        Args:
            direction: "next" 或 "previous"
            
        Returns:
            dict: 當前軟片模擬資訊
        """
        if direction == "next":
            info = self.film_sim.next_simulation()
        else:
            info = self.film_sim.previous_simulation()
        
        print(f"🎬 軟片模擬切換至: {info['name']} ({info['index']+1}/{info['total']})")
        return info
    
    def get_rd1_gauge_value(self) -> str:
        """
        取得用於 RD-1 錶盤顯示的軟片模擬值
        這個方法可以直接整合到您現有的 rd1_gauge.py 中
        """
        return self.film_sim.get_simulation_icon()
    
    def update_rd1_gauge_values(self) -> List[str]:
        """
        更新 RD-1 錶盤的軟片模擬選項列表
        可以用來更新錶盤上的軟片選項
        """
        return self.film_sim.create_simulation_gauge_values()


# === 與現有 RD-1 系統整合的範例 ===

def integrate_with_rd1_gauge():
    """
    與現有 rd1_gauge.py 整合的範例
    您可以將此邏輯加入到您的 rd1_gauge.py 中
    """
    
    # 建立軟片模擬系統
    camera_system = RD1CameraIntegration()
    
    # 取得軟片模擬錶盤值
    film_gauge_values = camera_system.update_rd1_gauge_values()
    
    # 您可以將這些值加入到現有的 gauges 列表中
    # 例如在 rd1_gauge.py 中加入:
    film_gauge = {
        "name": "FILM", 
        "label": "軟片模擬", 
        "values": film_gauge_values
    }
    
    print("軟片模擬錶盤設定:")
    print(f"名稱: {film_gauge['name']}")
    print(f"標籤: {film_gauge['label']}")
    print(f"選項: {film_gauge['values']}")
    
    return film_gauge


def demo_integration():
    """整合示範"""
    print("=" * 60)
    print("🎬 RD-1 軟片模擬系統整合示範")
    print("=" * 60)
    
    # 建立整合系統
    camera = RD1CameraIntegration()
    
    # 顯示所有可用軟片
    print("\n📋 可用軟片模擬:")
    for i, sim in enumerate(camera.film_sim.get_all_simulations(), 1):
        print(f"{i:2d}. {sim['icon']} - {sim['name']} ({sim['description']})")
    
    # 模擬切換軟片
    print("\n🔄 軟片模擬切換示範:")
    for i in range(3):
        current = camera.cycle_film_simulation("next")
        gauge_value = camera.get_rd1_gauge_value()
        print(f"   錶盤顯示: {gauge_value}")
        time.sleep(1)
    
    # 模擬拍照
    print("\n📸 模擬拍照 (需要實際圖像資料時才會真正處理):")
    # camera.take_photo_with_simulation(image_data, metadata)
    
    print("\n✅ 整合示範完成")


if __name__ == "__main__":
    # 執行示範
    demo_integration()
    
    # 顯示 RD-1 整合資訊
    print("\n" + "=" * 60)
    print("🔧 RD-1 系統整合說明")
    print("=" * 60)
    
    integrate_with_rd1_gauge()
    
    print("\n📝 整合步驟:")
    print("1. 將此模組複製到您的 mainCamera/filter/ 資料夾")
    print("2. 在 rd1_gauge.py 中加入軟片模擬錶盤")
    print("3. 在主相機程式中整合 RD1CameraIntegration 類別")
    print("4. 使用旋轉編碼器控制軟片切換")
    print("5. 拍照時自動套用當前選擇的軟片模擬")
