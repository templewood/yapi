from typing import List
import re
from datetime import datetime

def validate_hours_input(wh: List[str]):
    p = re.compile(r'^\d{2}:\d{2}-\d{2}:\d{2}$')
    for interval in wh:
        if not p.match(interval):
            return False
        try:
            tmp = [datetime.strptime(x, "%H:%M") for x in re.split("-", interval)]
        except ValueError:
            return False
    return True
