from operator import sub
from datetime import timedelta


def convert_two_bytes_to_celsius(first_byte, second_byte):
    return (first_byte + 256 * second_byte) * 0.1


def median(x):
    if len(x) % 2 != 0:
        return sorted(x)[len(x) / 2]
    else:
        midavg = (sorted(x)[len(x) / 2] + sorted(x)[len(x) / 2 - 1]) / 2.0
        return midavg


def get_six_lowest_values(x):
    return sorted(x)[:6]


def absolute_diff(former_list, current_list):
    diff = map(sub, current_list, former_list)
    return map(abs, diff)


def is_max_larger_than(pixel_list, number):
    return max(pixel_list) > number


def convert_1d_to_2d(index_1d):
    x = index_1d % 4
    y = index_1d / 4
    return x, y


def is_in_the_middle(x, y):
    return x in (1, 2) and y in (1, 2)


def is_almost_equal(a, b, eps=0.05):
    return abs(a - b) <= eps


def is_human(celsius_data):
    max_temp = max(celsius_data)
    lowest_values = get_six_lowest_values(celsius_data)
    median_of_lowest_values = median(lowest_values)
    diff_median_max = max_temp - median_of_lowest_values

    warm_enough = diff_median_max >= 2.2

    should_activate = False  # becomes true if warm enough in the middle
    if warm_enough:
        for i in xrange(len(celsius_data)):
            if is_almost_equal(celsius_data[i], max_temp):
                x, y = convert_1d_to_2d(i)
                if is_in_the_middle(x, y):
                    should_activate = True
    # print 'is human detected:', warm_enough
    return warm_enough, should_activate


def is_moving_human(celsius_data, previous_celsius_data):
    result = False

    if len(previous_celsius_data) == 16:
        abs_diff_between_frames = absolute_diff(previous_celsius_data, celsius_data)
        max_abs_diff_between_frames = max(abs_diff_between_frames)
        if max_abs_diff_between_frames >= 0.4:
            result = True

    # print 'is moving human detected:', result
    return result
