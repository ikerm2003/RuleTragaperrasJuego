#!/usr/bin/env python3
"""
Optimization Utilities for Casino Game
Performance and memory optimization tools
"""

import functools
import time
from typing import Callable, Dict, Any, Optional
import gc


class PerformanceMonitor:
    """Monitor and optimize performance"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.enabled = True
    
    def measure_time(self, func_name: str = None):
        """Decorator to measure function execution time"""
        def decorator(func: Callable) -> Callable:
            name = func_name or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                
                execution_time = (end_time - start_time) * 1000  # Convert to ms
                
                if name not in self.metrics:
                    self.metrics[name] = []
                self.metrics[name].append(execution_time)
                
                # Keep only last 100 measurements
                if len(self.metrics[name]) > 100:
                    self.metrics[name] = self.metrics[name][-100:]
                
                return result
            
            return wrapper
        return decorator
    
    def get_average_time(self, func_name: str) -> Optional[float]:
        """Get average execution time for a function"""
        if func_name not in self.metrics or not self.metrics[func_name]:
            return None
        return sum(self.metrics[func_name]) / len(self.metrics[func_name])
    
    def get_max_time(self, func_name: str) -> Optional[float]:
        """Get maximum execution time for a function"""
        if func_name not in self.metrics or not self.metrics[func_name]:
            return None
        return max(self.metrics[func_name])
    
    def get_metrics_report(self) -> str:
        """Get formatted metrics report"""
        if not self.metrics:
            return "No metrics collected"
        
        report = "Performance Metrics:\n"
        report += "=" * 60 + "\n"
        
        for func_name, times in self.metrics.items():
            if times:
                avg = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                count = len(times)
                
                report += f"{func_name}:\n"
                report += f"  Calls: {count}\n"
                report += f"  Avg: {avg:.2f}ms\n"
                report += f"  Min: {min_time:.2f}ms\n"
                report += f"  Max: {max_time:.2f}ms\n"
                report += "-" * 60 + "\n"
        
        return report
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        self.metrics.clear()


class MemoryOptimizer:
    """Memory optimization utilities"""
    
    @staticmethod
    def force_garbage_collection():
        """Force garbage collection"""
        gc.collect()
    
    @staticmethod
    def get_memory_usage():
        """Get current memory usage (requires psutil)"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
            }
        except ImportError:
            return None
    
    @staticmethod
    def optimize_pixmap_cache_size(size_mb: int = 50):
        """Set pixmap cache size for PyQt6"""
        try:
            from PyQt6.QtGui import QPixmapCache
            QPixmapCache.setCacheLimit(size_mb * 1024)  # Convert to KB
        except ImportError:
            pass
    
    @staticmethod
    def clear_pixmap_cache():
        """Clear the pixmap cache"""
        try:
            from PyQt6.QtGui import QPixmapCache
            QPixmapCache.clear()
        except ImportError:
            pass


class CacheManager:
    """Simple caching system for expensive operations"""
    
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.access_count: Dict[str, int] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set cached value"""
        # If cache is full, remove least accessed item
        if len(self.cache) >= self.max_size:
            least_accessed = min(self.access_count, key=self.access_count.get)
            del self.cache[least_accessed]
            del self.access_count[least_accessed]
        
        self.cache[key] = value
        self.access_count[key] = 1
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_count.clear()
    
    def cached(self, key_func: Callable = None):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Check cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Compute and cache
                result = func(*args, **kwargs)
                self.set(cache_key, result)
                return result
            
            return wrapper
        return decorator


class ResourceManager:
    """Manage resource loading and cleanup"""
    
    def __init__(self):
        self.loaded_resources: Dict[str, Any] = {}
        self.resource_refs: Dict[str, int] = {}
    
    def load_resource(self, resource_id: str, loader_func: Callable) -> Any:
        """Load a resource (or get from cache)"""
        if resource_id in self.loaded_resources:
            self.resource_refs[resource_id] += 1
            return self.loaded_resources[resource_id]
        
        resource = loader_func()
        self.loaded_resources[resource_id] = resource
        self.resource_refs[resource_id] = 1
        return resource
    
    def unload_resource(self, resource_id: str):
        """Unload a resource (decrease ref count)"""
        if resource_id not in self.loaded_resources:
            return
        
        self.resource_refs[resource_id] -= 1
        
        # If no more references, unload
        if self.resource_refs[resource_id] <= 0:
            del self.loaded_resources[resource_id]
            del self.resource_refs[resource_id]
            gc.collect()
    
    def clear_all(self):
        """Clear all loaded resources"""
        self.loaded_resources.clear()
        self.resource_refs.clear()
        gc.collect()


# Global instances
_performance_monitor = PerformanceMonitor()
_cache_manager = CacheManager()
_resource_manager = ResourceManager()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    return _performance_monitor


def get_cache_manager() -> CacheManager:
    """Get global cache manager"""
    return _cache_manager


def get_resource_manager() -> ResourceManager:
    """Get global resource manager"""
    return _resource_manager


# Convenience function for performance measurement
def measure_performance(func_name: str = None):
    """Convenience decorator for performance measurement"""
    return _performance_monitor.measure_time(func_name)


# Convenience function for caching
def cached(key_func: Callable = None):
    """Convenience decorator for caching"""
    return _cache_manager.cached(key_func)
