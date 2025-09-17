"""
A near-copy of the original `systemMonitor/system_gauge.py`, adjusted for package layout.
This file provides `SystemMonitorGauge` which wraps `analogGauge.rd1_gauge.RD1Gauge` and
maps system metrics (via psutil) to the RD-1 style gauges.

This example expects `psutil` to be installed on the host system.
"""

import sys
import os
import time
import psutil
from analogGauge.rd1_gauge import RD1Gauge

class SystemMonitorGauge:
    """System monitor gauge (example wrapper)"""
    def __init__(self):
        self.gauge = RD1Gauge()
        self.setup_system_gauges()
        self.net_io_counters = psutil.net_io_counters()
        self.last_net_time = time.time()
        self.net_speed_history = {"upload": [], "download": []}

    def setup_system_gauges(self):
        self.gauge.configure_gauge_dynamic(
            gauge_type="SHOTS",
            gauge_purpose="CPU",
            values=["0%", "25%", "50%", "75%", "100%"],
            color=(220, 50, 50)
        )

        self.gauge.configure_gauge_dynamic(
            gauge_type="WB",
            gauge_purpose="RAM",
            values=["0%", "25%", "50%", "75%", "100%"],
            color=(50, 150, 220)
        )

        self.gauge.configure_gauge_dynamic(
            gauge_type="QUALITY",
            gauge_purpose="DISK",
            values=["0%", "25%", "50%", "75%", "100%"],
            color=(255, 140, 0)
        )

        self.gauge.configure_gauge_dynamic(
            gauge_type="BATTERY",
            gauge_purpose="Network",
            values=["空閒", "低", "中", "高", "滿載"],
            color=(50, 200, 50)
        )

    def set_label_visibility(self, show: bool):
        self.gauge.set_label_visibility(show)

    def get_label_visibility(self) -> bool:
        return self.gauge.get_label_visibility()

    def set_glass_effect(self, enabled: bool):
        self.gauge.set_glass_effect(enabled)

    def get_glass_effect(self) -> bool:
        return self.gauge.get_glass_effect()

    def get_cpu_usage(self):
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
        try:
            current_disk = psutil.disk_io_counters()
            if current_disk is None:
                return 0
            if not hasattr(self, 'last_disk_io'):
                self.last_disk_io = current_disk
                self.last_disk_time = time.time()
                return 0
            current_time = time.time()
            time_diff = current_time - self.last_disk_time
            if time_diff <= 0:
                return 0
            read_diff = current_disk.read_bytes - self.last_disk_io.read_bytes
            write_diff = current_disk.write_bytes - self.last_disk_io.write_bytes
            total_diff = read_diff + write_diff
            bytes_per_sec = total_diff / time_diff
            self.last_disk_io = current_disk
            self.last_disk_time = current_time
            mb_per_sec = bytes_per_sec / (1024 * 1024)
            if mb_per_sec <= 1:
                return 0
            elif mb_per_sec <= 5:
                return 1
            elif mb_per_sec <= 15:
                return 2
            elif mb_per_sec <= 30:
                return 3
            else:
                return 4
        except Exception as e:
            print(f"磁碟活動監控錯誤: {e}")
            return 0

    def get_network_activity(self):
        try:
            current_net = psutil.net_io_counters()
            current_time = time.time()
            time_delta = current_time - self.last_net_time
            if time_delta < 0.5:
                return self.gauge.target_values.get("BATTERY", 0)
            upload_speed = (current_net.bytes_sent - self.net_io_counters.bytes_sent) / time_delta
            download_speed = (current_net.bytes_recv - self.net_io_counters.bytes_recv) / time_delta
            self.net_io_counters = current_net
            self.last_net_time = current_time
            total_speed = (upload_speed + download_speed) / 1024
            self.net_speed_history["upload"].append(upload_speed)
            self.net_speed_history["download"].append(download_speed)
            if len(self.net_speed_history["upload"]) > 10:
                self.net_speed_history["upload"].pop(0)
                self.net_speed_history["download"].pop(0)
            if total_speed < 10:
                return 0
            elif total_speed < 100:
                return 1
            elif total_speed < 1000:
                return 2
            elif total_speed < 10000:
                return 3
            else:
                return 4
        except Exception:
            return 0

    def update_system_metrics(self):
        cpu_level = self.get_cpu_usage()
        ram_level = self.get_memory_usage()
        disk_level = self.get_disk_usage()
        net_level = self.get_network_activity()
        self.gauge.set_value("SHOTS", cpu_level)
        self.gauge.set_value("WB", ram_level)
        self.gauge.set_value("QUALITY", disk_level)
        self.gauge.set_value("BATTERY", net_level)
        return {
            "cpu": cpu_level,
            "ram": ram_level,
            "disk": disk_level,
            "net": net_level
        }

    def get_detailed_info(self):
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        if os.name == 'nt':
            disk = psutil.disk_usage('C:')
        net_speed = 0
        if len(self.net_speed_history["upload"]) > 0:
            recent_up = sum(self.net_speed_history["upload"][-3:]) / len(self.net_speed_history["upload"][-3:])
            recent_down = sum(self.net_speed_history["download"][-3:]) / len(self.net_speed_history["download"][-3:])
            net_speed = (recent_up + recent_down) / 1024
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
        return self.gauge.draw_integrated_rd1_display()
