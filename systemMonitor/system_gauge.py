"""
系統監控類比錶盤模組
使用 RD-1 風格錶盤顯示 CPU、RAM、硬碟活動、網路使用率
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import psutil
import time
from analogGauge.rd1_gauge import RD1Gauge

class SystemMonitorGauge:
    """系統監控錶盤類別"""
    
    def __init__(self):
        self.gauge = RD1Gauge()
        self.setup_system_gauges()
        
        # 網路統計基準值
        self.net_io_counters = psutil.net_io_counters()
        self.last_net_time = time.time()
        self.net_speed_history = {"upload": [], "download": []}
        
    def setup_system_gauges(self):
        """設置系統監控錶盤配置，保持原有的 RD-1 視覺風格"""
        # 配置 SHOTS (最外圈) -> CPU 使用率 (原本是黑色，改為紅色)
        self.gauge.configure_gauge_dynamic(
            gauge_type="SHOTS",
            gauge_purpose="CPU",
            values=["0%", "25%", "50%", "75%", "100%"],
            color=(220, 50, 50)  # 紅色指針
        )
        
        # 配置 WB (左上，原本橘色) -> RAM 記憶體使用率 (改為藍色)
        self.gauge.configure_gauge_dynamic(
            gauge_type="WB",
            gauge_purpose="RAM",
            values=["0%", "25%", "50%", "75%", "100%"],
            color=(50, 150, 220)  # 藍色指針
        )
        
        # 配置 QUALITY (右上，原本紅色) -> 硬碟活動 (改為橙色)
        self.gauge.configure_gauge_dynamic(
            gauge_type="QUALITY",
            gauge_purpose="DISK",
            values=["0%", "25%", "50%", "75%", "100%"],
            color=(255, 140, 0)  # 橙色指針
        )
        
        # 配置 BATTERY (中下，原本綠色) -> 網路活動 (保持綠色)
        self.gauge.configure_gauge_dynamic(
            gauge_type="BATTERY",
            gauge_purpose="Network",
            values=["空閒", "低", "中", "高", "滿載"],
            color=(50, 200, 50)  # 綠色指針
        )
    
    def set_label_visibility(self, show: bool):
        """
        設置錶盤標籤顯示狀態
        
        Args:
            show: True 顯示標籤，False 隱藏標籤
        """
        self.gauge.set_label_visibility(show)
    
    def get_label_visibility(self) -> bool:
        """
        獲取錶盤標籤顯示狀態
        
        Returns:
            bool: 當前標籤顯示狀態
        """
        return self.gauge.get_label_visibility()
    
    def get_cpu_usage(self):
        """獲取 CPU 使用率"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent <= 20:
            return 0
        elif cpu_percent <= 40:
            return 1
        elif cpu_percent <= 60:
            return 2
        elif cpu_percent <= 80:
            return 3
        else:
            return 4
    
    def get_memory_usage(self):
        """獲取記憶體使用率"""
        memory = psutil.virtual_memory()
        mem_percent = memory.percent
        if mem_percent <= 20:
            return 0
        elif mem_percent <= 40:
            return 1
        elif mem_percent <= 60:
            return 2
        elif mem_percent <= 80:
            return 3
        else:
            return 4
    
    def get_disk_usage(self):
        """獲取硬碟活動率 (仿照工作管理員)"""
        try:
            # 獲取當前磁碟 I/O 統計
            current_disk = psutil.disk_io_counters()
            if current_disk is None:
                return 0
            
            # 如果是第一次調用，初始化上次的數據
            if not hasattr(self, 'last_disk_io'):
                self.last_disk_io = current_disk
                self.last_disk_time = time.time()
                return 0
            
            # 計算時間差
            current_time = time.time()
            time_diff = current_time - self.last_disk_time
            
            if time_diff <= 0:
                return 0
            
            # 計算讀寫字節數差異
            read_diff = current_disk.read_bytes - self.last_disk_io.read_bytes
            write_diff = current_disk.write_bytes - self.last_disk_io.write_bytes
            total_diff = read_diff + write_diff
            
            # 計算每秒字節數 (B/s)
            bytes_per_sec = total_diff / time_diff
            
            # 更新上次的數據
            self.last_disk_io = current_disk
            self.last_disk_time = current_time
            
            # 將字節/秒轉換為活動等級
            # 參考值：假設 10MB/s 為高活動
            mb_per_sec = bytes_per_sec / (1024 * 1024)
            
            if mb_per_sec <= 1:      # 低於 1MB/s
                return 0
            elif mb_per_sec <= 5:    # 1-5MB/s
                return 1
            elif mb_per_sec <= 15:   # 5-15MB/s
                return 2
            elif mb_per_sec <= 30:   # 15-30MB/s
                return 3
            else:                    # 超過 30MB/s
                return 4
                
        except Exception as e:
            print(f"磁碟活動監控錯誤: {e}")
            return 0
    
    def get_network_activity(self):
        """獲取網路活動等級"""
        try:
            current_net = psutil.net_io_counters()
            current_time = time.time()
            time_delta = current_time - self.last_net_time
            
            if time_delta < 0.5:  # 至少 0.5 秒間隔
                return self.gauge.target_values.get("BATTERY", 0)
            
            # 計算上下行速度 (bytes/sec)
            upload_speed = (current_net.bytes_sent - self.net_io_counters.bytes_sent) / time_delta
            download_speed = (current_net.bytes_recv - self.net_io_counters.bytes_recv) / time_delta
            
            # 更新基準值
            self.net_io_counters = current_net
            self.last_net_time = current_time
            
            # 計算總活動量 (KB/s)
            total_speed = (upload_speed + download_speed) / 1024
            
            # 維持歷史記錄（最近 10 次）
            self.net_speed_history["upload"].append(upload_speed)
            self.net_speed_history["download"].append(download_speed)
            if len(self.net_speed_history["upload"]) > 10:
                self.net_speed_history["upload"].pop(0)
                self.net_speed_history["download"].pop(0)
            
            # 根據網路活動量分級
            if total_speed < 10:      # < 10 KB/s
                return 0
            elif total_speed < 100:   # < 100 KB/s
                return 1
            elif total_speed < 1000:  # < 1 MB/s
                return 2
            elif total_speed < 10000: # < 10 MB/s
                return 3
            else:                     # >= 10 MB/s
                return 4
                
        except Exception:
            return 0
    
    def update_system_metrics(self):
        """更新所有系統指標"""
        # 獲取系統數據
        cpu_level = self.get_cpu_usage()
        ram_level = self.get_memory_usage() 
        disk_level = self.get_disk_usage()
        net_level = self.get_network_activity()
        
        # 設置錶盤數值（正確對應）
        self.gauge.set_value("SHOTS", cpu_level)     # 最外圈 -> CPU
        self.gauge.set_value("WB", ram_level)        # 左上 -> RAM
        self.gauge.set_value("QUALITY", disk_level)  # 右上 -> 硬碟活動
        self.gauge.set_value("BATTERY", net_level)   # 中下 -> 網路
        
        # 注意：動畫更新由主循環以 120fps 頻率處理，此處不需要調用
        
        return {
            "cpu": cpu_level,
            "ram": ram_level, 
            "disk": disk_level,
            "net": net_level
        }
    
    def get_detailed_info(self):
        """獲取詳細系統資訊"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        disk = psutil.disk_usage('/')
        if os.name == 'nt':
            disk = psutil.disk_usage('C:')
        
        # 網路速度計算
        net_speed = 0
        if len(self.net_speed_history["upload"]) > 0:
            recent_up = sum(self.net_speed_history["upload"][-3:]) / len(self.net_speed_history["upload"][-3:])
            recent_down = sum(self.net_speed_history["download"][-3:]) / len(self.net_speed_history["download"][-3:])
            net_speed = (recent_up + recent_down) / 1024  # KB/s
        
        return {
            "cpu_percent": f"{cpu_percent:.1f}%",
            "memory_percent": f"{memory.percent:.1f}%",
            "memory_used": f"{memory.used / (1024**3):.1f}GB",
            "memory_total": f"{memory.total / (1024**3):.1f}GB",
            "disk_percent": f"{(disk.used / disk.total) * 100:.1f}%",
            "disk_used": f"{disk.used / (1024**3):.1f}GB", 
            "disk_total": f"{disk.total / (1024**3):.1f}GB",
            "net_speed": f"{net_speed:.1f} KB/s"
        }
    
    def draw_system_monitor_display(self):
        """生成系統監控錶盤圖像"""
        return self.gauge.draw_integrated_rd1_display()