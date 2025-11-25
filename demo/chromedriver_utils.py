#!/usr/bin/env python3
"""
ChromeDriver管理工具
用于优化ChromeDriver的下载和缓存管理
"""

import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from webdriver_manager.core.driver import Driver
from webdriver_manager.core.logger import log

logger = logging.getLogger(__name__)

class SkipVersionCheckCacheManager(DriverCacheManager):
    """跳过版本检查的缓存管理器"""
    
    def __init__(self, root_dir=None, valid_range=1, file_manager=None):
        # 设置一个非常大的有效范围，实际上总是认为缓存有效
        super().__init__(root_dir, 365*100, file_manager)  # 100年有效期
    
    def _DriverCacheManager__is_valid(self, driver_info):
        """重写验证方法，总是返回True"""
        return True  # 总是认为缓存有效
    
    def find_driver(self, driver: Driver):
        """重写查找驱动方法，跳过时间验证"""
        os_type = self.get_os_type()
        driver_name = driver.get_name()
        browser_type = driver.get_browser_type()
        browser_version = self._os_system_manager.get_browser_version_from_os(browser_type)
        if not browser_version:
            return None

        driver_version = self.get_cache_key_driver_version(driver)
        metadata = self.load_metadata_content()

        key = self._DriverCacheManager__get_metadata_key(driver)
        if key not in metadata:
            log(f'There is no [{os_type}] {driver_name} "{driver_version}" for browser {browser_type} '
                f'"{browser_version}" in cache')
            return None

        driver_info = metadata[key]
        path = driver_info["binary_path"]
        if not os.path.exists(path):
            return None

        # 跳过时间验证，总是认为缓存有效
        # if not self._DriverCacheManager__is_valid(driver_info):
        #     return None

        path = driver_info["binary_path"]
        log(f"Driver [{path}] found in cache")
        return path

class ChromeDriverManagerOptimized:
    """优化的ChromeDriver管理器"""
    
    _instance = None
    _driver_path = None
    _cache_manager = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromeDriverManagerOptimized, cls).__new__(cls)
            # 使用跳过版本检查的缓存管理器
            cls._cache_manager = SkipVersionCheckCacheManager()
        return cls._instance
    
    def get_driver_path(self, skip_version_check=True):
        """获取ChromeDriver路径，带缓存优化
        
        Args:
            skip_version_check (bool): 是否跳过版本检查，直接使用缓存的驱动
        """
        if self._driver_path is None:
            try:
                logger.info("正在获取ChromeDriver...")
                
                if skip_version_check:
                    # 直接从缓存中获取ChromeDriver路径，跳过版本检查
                    self._driver_path = self._get_cached_driver_path()
                    if self._driver_path:
                        logger.info(f"跳过版本检查，直接使用缓存的ChromeDriver: {self._driver_path}")
                        return self._driver_path
                    else:
                        logger.warning("未找到缓存的ChromeDriver，将执行版本检查")
                
                # 使用跳过版本检查的缓存管理器获取驱动路径
                self._driver_path = ChromeDriverManager(
                    cache_manager=self._cache_manager
                ).install()
                logger.info(f"ChromeDriver路径: {self._driver_path}")
            except Exception as e:
                logger.error(f"获取ChromeDriver失败: {e}")
                raise
        return self._driver_path
    
    def _get_cached_driver_path(self):
        """直接从缓存中获取ChromeDriver路径，不进行版本检查"""
        try:
            # 尝试从缓存中查找ChromeDriver
            import platform
            
            # 确定操作系统类型
            system = platform.system().lower()
            if system == "darwin":  # macOS
                # 检查是否为ARM架构
                if platform.machine() == "arm64":
                    os_type = "mac_arm64"
                else:
                    os_type = "mac64"
            elif system == "windows":
                os_type = "win32"
            else:
                os_type = "linux64"
            
            # 查找缓存目录
            cache_paths = [
                os.path.join(os.getcwd(), '.wdm'),  # 项目目录缓存
                os.path.expanduser('~/.wdm'),       # 用户目录缓存
            ]
            
            for cache_path in cache_paths:
                drivers_json_path = os.path.join(cache_path, 'drivers.json')
                if os.path.exists(drivers_json_path):
                    import json
                    with open(drivers_json_path, 'r') as f:
                        metadata = json.load(f)
                    
                    # 查找匹配的ChromeDriver条目
                    for key, driver_info in metadata.items():
                        if 'chromedriver' in key:
                            # 检查是否匹配操作系统类型（兼容mac64和mac_arm64）
                            if os_type in key or (os_type == "mac_arm64" and "mac64" in key):
                                binary_path = driver_info.get('binary_path')
                                if binary_path and os.path.exists(binary_path):
                                    return binary_path
            
            # 如果在drivers.json中没有找到，尝试直接在目录结构中查找
            for cache_path in cache_paths:
                drivers_dir = os.path.join(cache_path, 'drivers', 'chromedriver', os_type)
                if not os.path.exists(drivers_dir) and os_type == "mac_arm64":
                    # 如果mac_arm64目录不存在，尝试mac64目录
                    drivers_dir = os.path.join(cache_path, 'drivers', 'chromedriver', 'mac64')
                
                if os.path.exists(drivers_dir):
                    # 查找版本目录
                    for version_dir in os.listdir(drivers_dir):
                        version_path = os.path.join(drivers_dir, version_dir)
                        if os.path.isdir(version_path):
                            # 查找实际的chromedriver文件
                            possible_paths = [
                                os.path.join(version_path, f'chromedriver-{os_type}', 'chromedriver'),
                                os.path.join(version_path, 'chromedriver-mac-arm64', 'chromedriver'),
                                os.path.join(version_path, 'chromedriver'),
                                os.path.join(version_path, 'chromedriver.exe')
                            ]
                            
                            for binary_path in possible_paths:
                                if os.path.exists(binary_path):
                                    return binary_path
            
            return None
        except Exception as e:
            logger.warning(f"从缓存获取ChromeDriver路径失败: {e}")
            return None
    
    def create_driver(self, headless=True, additional_options=None, skip_version_check=True):
        """创建优化的Chrome WebDriver实例
        
        Args:
            headless (bool): 是否使用无头模式
            additional_options (list): 额外的Chrome选项
            skip_version_check (bool): 是否跳过版本检查
        """
        chrome_options = Options()
        
        # 基本优化选项
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        if headless:
            chrome_options.add_argument("--headless")
            
        # 添加额外选项
        if additional_options:
            for option in additional_options:
                chrome_options.add_argument(option)
        
        # 获取驱动路径并创建服务
        driver_path = self.get_driver_path(skip_version_check)
        service = Service(driver_path)
        
        # 创建WebDriver实例
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 移除webdriver标识以避免被检测
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

# 全局实例
chrome_manager = ChromeDriverManagerOptimized()

def get_chrome_driver(headless=True, additional_options=None, skip_version_check=True):
    """
    获取优化的Chrome WebDriver实例
    
    Args:
        headless (bool): 是否使用无头模式
        additional_options (list): 额外的Chrome选项
        skip_version_check (bool): 是否跳过版本检查
        
    Returns:
        webdriver.Chrome: Chrome WebDriver实例
    """
    return chrome_manager.create_driver(headless, additional_options, skip_version_check)

def setup_webdriver_manager_env():
    """设置webdriver-manager环境变量"""
    # 设置缓存有效期为7天
    os.environ.setdefault('WDM_CACHE_VALID_RANGE', '7')
    # 启用本地缓存
    os.environ.setdefault('WDM_LOCAL', '1')
    # 设置缓存目录
    os.environ.setdefault('WDM_CACHE_PATH', os.path.join(os.getcwd(), '.wdm'))

# 初始化环境变量
setup_webdriver_manager_env()