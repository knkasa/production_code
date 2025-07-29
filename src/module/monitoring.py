import psutil
import time
import threading
from loguru import logger
from datetime import datetime

class SystemMonitor:
    __slots__ = ['log_interval', 'monitoring', 'monitor_thread']
    def __init__(self, *, log_interval):
        """
            リソースモニタリング

            Args:
                log_interval(int) = int (ログの頻度を秒で入力)
            Return:
                None
        """

        logger.info('System monitoring started.')
        self.log_interval = log_interval
        self.monitoring = False
        self.monitor_thread = None

    def __str__(self): 
        return f"Attribute vars: {self.log_interval}, {self.monitoring}, {self.monitor_thread}"
            
    def get_system_metrics(self):
        """Collect current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            process = psutil.Process()
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info()
            process_memory_mb = process_memory.rss / (1024**2)
            
            disk_io = psutil.disk_io_counters()
            disk_usage = psutil.disk_usage('/')
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system_cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "system_memory_percent": memory_percent,
                "system_memory_available_gb": round(memory_available_gb, 2),
                "system_memory_used_gb": round(memory_used_gb, 2),
                "system_memory_total_gb": round(memory_total_gb, 2),
                "process_cpu_percent": process_cpu,
                "process_memory_mb": round(process_memory_mb, 2),
                "disk_usage_percent": disk_usage.percent,
                "disk_read_bytes": disk_io.read_bytes if disk_io else 0,
                "disk_write_bytes": disk_io.write_bytes if disk_io else 0
                }
        except Exception as e:
            logger.exception("Error at SystemMonitor.get_system_metrics:")
    
    def log_metrics(self):
        """Log current system metrics with structured format"""
        try:
            metrics = self.get_system_metrics()
            
            logger.info(
                "System Metrics | "
                f"CPU: {metrics['system_cpu_percent']}% | "
                f"Memory: {metrics['system_memory_percent']}% "
                #f"({metrics['system_memory_used_gb']}/{metrics['system_memory_total_gb']} GB) | "
                f"Process CPU: {metrics['process_cpu_percent']}% | "
                #f"Process Memory: {metrics['process_memory_mb']} MB | "
                f"Disk: {metrics['disk_usage_percent']}%",
                extra={"metrics": metrics}
                )
            
            # Log warnings for high usage
            if metrics['system_cpu_percent'] > 90:
                logger.warning(f"High CPU usage detected: {metrics['system_cpu_percent']}%")
            
            if metrics['system_memory_percent'] > 95:
                logger.warning(f"High memory usage detected: {metrics['system_memory_percent']}%")
                
            #if metrics['process_memory_mb'] > 1000:  # Adjust threshold as needed
            #    logger.warning(f"Process using high memory: {metrics['process_memory_mb']} MB")
                
        except Exception as e:
            logger.exception(f"Error at SystemMonitor.log_metrics:")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            self.log_metrics()
            time.sleep(self.log_interval)
    
    def start_monitoring(self):
        """Start background monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info(f"Started system monitoring (interval: {self.log_interval}s)")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("Stopped system monitoring")
    
    def log_single_metric(self):
        """Log manually"""
        self.log_metrics()
