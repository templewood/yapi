from typing import List
import re
from datetime import datetime


class TimeInterval:
    def __init__(self, hours: str, adjust=False, current=None):
        self.start, self.stop = hours.split("-")
        if adjust and current:
            # [.......]| => []
            # [.......|  => []
            if current >= self.stop:
                self.start = self.stop
            # [......|...] => |...]
            elif current > self.start and current < self.stop:
                self.start = current

    def __str__(self):
        return f'{self.start}-{self.stop}'

    def __repr__(self):
        return f'{self.start}-{self.stop}'


def get_adjusted_time_intervals(hours: List[str], current_time):
    result = []
    for interval in hours:
        tmp = TimeInterval(interval, True, current_time)
        if tmp.start != tmp.stop:
            result.append(tmp)
    return result


def can_be_delivered_in_time(current_time: str,
                             courier_hours: List[str],
                             delivery_hours: List[str]):
    c_h = get_adjusted_time_intervals(courier_hours, current_time)
    d_h = get_adjusted_time_intervals(delivery_hours, current_time)
    if not c_h or not d_h:
        return False
    for courier_interval in c_h:
        for delivery_interval in d_h:
            if (courier_interval.start < delivery_interval.stop) and (
                courier_interval.stop > delivery_interval.start):
                return True
    return False


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


if __name__ == "__main__":
    assign_time = datetime.now()
    current_time = assign_time.strftime('%H:%M')
    courier_hours = ["11:35-14:08", "09:00-11:05"]
    delivery_hours = ["14:05-14:35", "11:00-11:35"]

    current_time = '16:08'
    print(can_be_delivered_in_time(current_time, courier_hours, delivery_hours))
