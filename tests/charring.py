from src.zone_model_1.charring import *


def test_1():
    N = 60
    time_list = list(range(1, N + 1))
    temp_list = [standard_fire_curve(x) for x in time_list]
    integral = char_depth_integral(temp_list, time_list)
    assert abs(char_depth_integral(temp_list, time_list) - 49.617272031154265) < 1e-6, 'Unmatched char depth integral'
    print(integral)
