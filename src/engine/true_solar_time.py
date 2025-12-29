"""
真太阳时计算模块

真太阳时 = 地方平太阳时 + 时差
地方平太阳时 = 北京时间 + (当地经度 - 120) × 4分钟

时差（Equation of Time）是由于地球公转轨道是椭圆形以及地轴倾斜造成的，
每天的时差值不同，需要根据日期计算。
"""

from datetime import datetime, timedelta
import math


def calculate_equation_of_time(day_of_year: int) -> float:
    """
    计算时差（分钟）
    使用简化公式计算时差，精度约为30秒

    Args:
        day_of_year: 一年中的第几天（1-366）

    Returns:
        时差，单位为分钟
    """
    # 将日期转换为弧度
    b = 2 * math.pi * (day_of_year - 81) / 365

    # 时差公式（单位：分钟）
    # E = 9.87 * sin(2B) - 7.53 * cos(B) - 1.5 * sin(B)
    equation_of_time = (
        9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    )

    return equation_of_time


def calculate_local_mean_solar_time(
    beijing_time: datetime, longitude: float
) -> datetime:
    """
    计算地方平太阳时

    Args:
        beijing_time: 北京时间（东八区，以东经120度为基准）
        longitude: 当地经度

    Returns:
        地方平太阳时
    """
    # 每度经度对应4分钟的时间差
    # 东经120度是北京时间的基准经度
    longitude_diff = longitude - 120.0
    time_diff_minutes = longitude_diff * 4

    return beijing_time + timedelta(minutes=time_diff_minutes)


def calculate_true_solar_time(
    beijing_time: datetime, longitude: float, latitude: float = 0.0
) -> datetime:
    """
    计算真太阳时

    Args:
        beijing_time: 北京时间
        longitude: 当地经度
        latitude: 当地纬度（当前未使用，预留）

    Returns:
        真太阳时
    """
    # 计算一年中的第几天
    day_of_year = beijing_time.timetuple().tm_yday

    # 计算时差
    equation_of_time = calculate_equation_of_time(day_of_year)

    # 计算地方平太阳时
    local_mean_solar_time = calculate_local_mean_solar_time(beijing_time, longitude)

    # 真太阳时 = 地方平太阳时 + 时差
    true_solar_time = local_mean_solar_time + timedelta(minutes=equation_of_time)

    return true_solar_time


def get_true_solar_time_offset(
    beijing_time: datetime, longitude: float
) -> timedelta:
    """
    获取真太阳时与北京时间的偏移量

    Args:
        beijing_time: 北京时间
        longitude: 当地经度

    Returns:
        时间偏移量（真太阳时 - 北京时间）
    """
    true_solar = calculate_true_solar_time(beijing_time, longitude)
    return true_solar - beijing_time


def format_time_offset(offset: timedelta) -> str:
    """
    格式化时间偏移量为可读字符串

    Args:
        offset: 时间偏移量

    Returns:
        格式化的字符串，如 "+15分钟" 或 "-8分钟"
    """
    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else ""
    minutes = total_seconds // 60
    seconds = abs(total_seconds % 60)

    if seconds == 0:
        return f"{sign}{minutes}分钟"
    else:
        return f"{sign}{minutes}分{seconds}秒"

