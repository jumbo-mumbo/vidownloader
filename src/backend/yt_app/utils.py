import requests

# check if thumbnail url exists
def check_thumbnail(thumb_url: str) -> bool:
    r = requests.get(thumb_url)
    if r.status_code == 200:
        return True
    return False

    
# Format bytes to Kib, Mib...
def format_bytes(size: float | int) -> str:
        # 2**10 = 1024
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'KiB', 2: 'MiB', 3: 'GiB', 4: 'TiB'}
        while size > power:
            size /= power
            n += 1
        return f"{round(size, 2)} {power_labels[n]}"

# Remove width form resolution
def format_resolution(resolution: str) -> str:
    if resolution:
        x_idx = resolution.find("x")
        if x_idx != -1:
            return resolution[x_idx + 1:]

        return None

# Formatting time (seconds)
def time_format(time_s: int):
    minutes = time_s //60
    if minutes == 0:
        return f"{time_s %60}s."

    elif minutes > 60:
        return f"{time_s//3600}h. {(time_s%3600)//60}m. {time_s%60}s."

    return f"{time_s//60}m. {time_s%60}s."


    
    