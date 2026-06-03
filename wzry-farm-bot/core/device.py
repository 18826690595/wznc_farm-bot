"""
设备连接管理器 - 负责MuMu模拟器的ADB连接
采用单例模式确保全局只有一个设备连接
"""
import uiautomator2 as u2
from loguru import logger
from typing import Optional, Tuple
import time


class DeviceManager:
    """
    设备管理器（单例模式）
    负责MuMu模拟器的连接、截图、点击等基础操作
    """
    _instance: Optional['DeviceManager'] = None
    _device: Optional[u2.Device] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._device is None:
            self._connected = False
            self._screen_size = None
    
    def connect(self, adb_port: int = 7555) -> bool:
        """
        连接MuMu模拟器
        
        Args:
            adb_port: MuMu模拟器ADB端口，默认7555
            
        Returns:
            连接是否成功
        """
        try:
            # MuMu模拟器连接地址
            device_addr = f"127.0.0.1:{adb_port}"
            logger.info(f"正在连接MuMu模拟器: {device_addr}")
            
            # 使用uiautomator2连接
            self._device = u2.connect(device_addr)
            
            # 验证连接
            device_info = self._device.device_info
            logger.success(f"连接成功! 设备信息: {device_info}")
            
            # 获取屏幕尺寸
            self._screen_size = (self._device.info['displayWidth'], 
                                self._device.info['displayHeight'])
            logger.info(f"屏幕尺寸: {self._screen_size}")
            
            self._connected = True
            return True
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """断开连接"""
        if self._device:
            self._device = None
            self._connected = False
            logger.info("已断开设备连接")
    
    @property
    def device(self) -> u2.Device:
        """获取设备实例"""
        if not self._connected or self._device is None:
            raise RuntimeError("设备未连接，请先调用connect()")
        return self._device
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected
    
    @property
    def screen_size(self) -> Tuple[int, int]:
        """屏幕尺寸 (width, height)"""
        return self._screen_size or (1280, 720)
    
    def screenshot(self, save_path: Optional[str] = None) -> 'np.ndarray':
        """
        截取屏幕
        
        Args:
            save_path: 保存路径（可选）
            
        Returns:
            numpy数组格式的图片
        """
        import cv2
        import numpy as np
        
        # 使用uiautomator2截图
        img = self.device.screenshot(format='opencv')
        
        if save_path:
            cv2.imwrite(save_path, img)
            logger.debug(f"截图已保存: {save_path}")
        
        return img
    
    def tap(self, x: int, y: int, duration: float = 0.1):
        """
        点击屏幕坐标
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 按压时长
        """
        self.device.click(x, y)
        logger.debug(f"点击坐标: ({x}, {y})")
        time.sleep(duration)
    
    def swipe(self, start: Tuple[int, int], end: Tuple[int, int], duration: float = 0.5):
        """
        滑动屏幕
        
        Args:
            start: 起始坐标 (x, y)
            end: 结束坐标 (x, y)
            duration: 滑动时长
        """
        self.device.swipe(start[0], start[1], end[0], end[1], duration)
        logger.debug(f"滑动: {start} -> {end}")
    
    def swipe_up(self, distance: int = 500):
        """向上滑动"""
        width, height = self.screen_size
        center_x = width // 2
        self.swipe((center_x, height // 2), (center_x, height // 2 - distance))
    
    def swipe_down(self, distance: int = 500):
        """向下滑动"""
        width, height = self.screen_size
        center_x = width // 2
        self.swipe((center_x, height // 2 - distance), (center_x, height // 2))
    
    def back(self):
        """返回键"""
        self.device.press("back")
        logger.debug("按下返回键")
        time.sleep(0.3)
    
    def home(self):
        """HOME键"""
        self.device.press("home")
        logger.debug("按下HOME键")
        time.sleep(0.3)


# 全局单例
device_manager = DeviceManager()
