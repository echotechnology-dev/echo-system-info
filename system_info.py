import psutil
import platform
import time


def get_cpu():
    usage = psutil.cpu_percent(interval=0.3)
    return {
        "name": platform.processor(),
        "usage": usage,
        "status": "Normal" if usage < 60 else "High" if usage < 85 else "Critical",
        "message": (
            "CPU load is normal."
            if usage < 60 else
            "High CPU load may slow down the system."
            if usage < 85 else
            "Critical CPU load detected."
        )
    }


def get_ram():
    mem = psutil.virtual_memory()
    return {
        "used": round(mem.used / (1024 ** 3), 1),
        "total": round(mem.total / (1024 ** 3), 1),
        "percent": mem.percent,
        "status": "Normal" if mem.percent < 70 else "High" if mem.percent < 90 else "Critical",
        "message": (
            "Memory usage is normal."
            if mem.percent < 70 else
            "High memory usage detected."
            if mem.percent < 90 else
            "Very low free memory."
        )
    }


def get_disks():
    disks = []
    for part in psutil.disk_partitions():
        if not part.fstype:
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            free_gb = round(usage.free / (1024 ** 3), 1)
            total_gb = round(usage.total / (1024 ** 3), 1)

            disks.append({
                "name": part.device.replace("\\", ""),
                "free": free_gb,
                "total": total_gb,
                "status": "Normal" if free_gb > 20 else "Critical"
            })
        except PermissionError:
            pass
    return disks


def get_system():
    uptime = round((time.time() - psutil.boot_time()) / 3600, 1)
    return {
        "os": f"{platform.system()} {platform.release()}",
        "arch": platform.architecture()[0],
        "uptime": f"{uptime} hours"
    }
