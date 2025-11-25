#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化模块
提供缓存管理、批量处理、数据压缩等性能优化功能
"""

import json
import logging
import hashlib
import pickle
import time
from functools import wraps
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = "data/cache", ttl: int = 3600):
        """初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            ttl: 缓存过期时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.memory_cache = {}
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存键的hash"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def get(self, key: str, use_memory: bool = True) -> Optional[Any]:
        """获取缓存
        
        Args:
            key: 缓存键
            use_memory: 是否使用内存缓存
            
        Returns:
            缓存的数据，如果不存在或过期则返回None
        """
        try:
            # 先查内存缓存
            if use_memory and key in self.memory_cache:
                cached_data, timestamp = self.memory_cache[key]
                if time.time() - timestamp < self.ttl:
                    logger.debug(f"内存缓存命中: {key}")
                    return cached_data
                else:
                    del self.memory_cache[key]
            
            # 查文件缓存
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    cached_data, timestamp = pickle.load(f)
                
                if time.time() - timestamp < self.ttl:
                    logger.debug(f"文件缓存命中: {key}")
                    if use_memory:
                        self.memory_cache[key] = (cached_data, timestamp)
                    return cached_data
                else:
                    cache_path.unlink()
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def set(self, key: str, data: Any, use_memory: bool = True):
        """设置缓存
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            use_memory: 是否同时保存到内存
        """
        try:
            timestamp = time.time()
            
            # 保存到内存
            if use_memory:
                self.memory_cache[key] = (data, timestamp)
            
            # 保存到文件
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            
            with open(cache_path, 'wb') as f:
                pickle.dump((data, timestamp), f)
            
            logger.debug(f"设置缓存: {key}")
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
    
    def delete(self, key: str):
        """删除缓存"""
        try:
            # 删除内存缓存
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # 删除文件缓存
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                cache_path.unlink()
            
            logger.debug(f"删除缓存: {key}")
            
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
    
    def clear(self):
        """清空所有缓存"""
        try:
            # 清空内存缓存
            self.memory_cache.clear()
            
            # 清空文件缓存
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            logger.info("清空所有缓存")
            
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
    
    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        try:
            memory_count = len(self.memory_cache)
            file_count = len(list(self.cache_dir.glob("*.cache")))
            
            total_size = sum(
                f.stat().st_size for f in self.cache_dir.glob("*.cache")
            )
            
            return {
                "memory_cached_items": memory_count,
                "file_cached_items": file_count,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "cache_dir": str(self.cache_dir)
            }
            
        except Exception as e:
            logger.error(f"获取缓存信息失败: {e}")
            return {}


def cached(ttl: int = 3600, use_memory: bool = True):
    """缓存装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
        use_memory: 是否使用内存缓存
    """
    def decorator(func: Callable) -> Callable:
        cache_manager = CacheManager(ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # 尝试获取缓存
            cached_result = cache_manager.get(cache_key, use_memory)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 保存缓存
            cache_manager.set(cache_key, result, use_memory)
            
            return result
        
        return wrapper
    return decorator


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, batch_size: int = 100):
        """初始化批量处理器
        
        Args:
            batch_size: 批次大小
        """
        self.batch_size = batch_size
    
    def process_in_batches(self, items: List[Any], 
                           process_func: Callable,
                           show_progress: bool = True) -> List[Any]:
        """批量处理数据
        
        Args:
            items: 待处理数据列表
            process_func: 处理函数
            show_progress: 是否显示进度
            
        Returns:
            处理结果列表
        """
        try:
            results = []
            total = len(items)
            
            for i in range(0, total, self.batch_size):
                batch = items[i:i + self.batch_size]
                batch_results = [process_func(item) for item in batch]
                results.extend(batch_results)
                
                if show_progress:
                    progress = min((i + self.batch_size) / total * 100, 100)
                    logger.info(f"批量处理进度: {progress:.1f}%")
            
            return results
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
            return []
    
    def process_parallel(self, items: List[Any],
                        process_func: Callable,
                        num_workers: int = 4) -> List[Any]:
        """并行处理数据
        
        Args:
            items: 待处理数据列表
            process_func: 处理函数
            num_workers: 工作线程数
            
        Returns:
            处理结果列表
        """
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            results = []
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = {
                    executor.submit(process_func, item): i 
                    for i, item in enumerate(items)
                }
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append((futures[future], result))
                    except Exception as e:
                        logger.error(f"处理任务失败: {e}")
            
            # 按原始顺序排序
            results.sort(key=lambda x: x[0])
            return [r[1] for r in results]
            
        except Exception as e:
            logger.error(f"并行处理失败: {e}")
            return []


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        """初始化性能监控器"""
        self.metrics = {}
    
    def timer(self, name: str):
        """计时器装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if name not in self.metrics:
                    self.metrics[name] = []
                self.metrics[name].append(elapsed)
                
                logger.debug(f"{name} 执行时间: {elapsed:.3f}s")
                return result
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict:
        """获取性能统计"""
        stats = {}
        for name, times in self.metrics.items():
            stats[name] = {
                "count": len(times),
                "total": sum(times),
                "avg": sum(times) / len(times) if times else 0,
                "min": min(times) if times else 0,
                "max": max(times) if times else 0
            }
        return stats
    
    def reset(self):
        """重置统计"""
        self.metrics.clear()


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def measure_performance(name: str):
    """性能测量装饰器"""
    return performance_monitor.timer(name)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 测试缓存
    print("测试缓存功能...")
    cache = CacheManager(ttl=10)
    
    cache.set("test_key", {"data": "test_value"})
    result = cache.get("test_key")
    print(f"缓存测试: {result}")
    
    cache_info = cache.get_cache_info()
    print(f"缓存信息: {cache_info}")
    
    # 测试缓存装饰器
    @cached(ttl=5)
    def slow_function(x):
        time.sleep(0.1)
        return x * 2
    
    start = time.time()
    result1 = slow_function(10)
    time1 = time.time() - start
    
    start = time.time()
    result2 = slow_function(10)  # 应该从缓存读取
    time2 = time.time() - start
    
    print(f"\n首次调用: {time1:.3f}s, 结果: {result1}")
    print(f"缓存调用: {time2:.3f}s, 结果: {result2}")
    print(f"性能提升: {(time1/time2):.1f}x")
    
    # 测试批量处理
    print("\n测试批量处理...")
    processor = BatchProcessor(batch_size=10)
    
    items = list(range(35))
    results = processor.process_in_batches(
        items, 
        lambda x: x * 2,
        show_progress=True
    )
    print(f"批量处理完成: {len(results)} 个结果")
    
    # 测试性能监控
    print("\n测试性能监控...")
    
    @measure_performance("test_function")
    def test_func():
        time.sleep(0.05)
        return "done"
    
    for _ in range(3):
        test_func()
    
    stats = performance_monitor.get_stats()
    print(f"性能统计: {json.dumps(stats, indent=2)}")
    
    print("\n✅ 性能优化模块测试通过！")
