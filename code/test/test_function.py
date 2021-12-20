import time

def get_string_time_diff(str1, str2):
    t_be = time.mktime(time.strptime(str1, '%Y-%m-%d %H:%M:%S'))

    t_af = time.mktime(time.strptime(str2, '%Y-%m-%d %H:%M:%S'))

    t_dif = t_af - t_be

    if t_dif > 24 * 60 * 60:
        day = t_dif // (24 * 60 * 60)
    else:
        day = 0

    if t_dif > 60 * 60:
        hour = (t_dif - (day * 24 * 60 * 60) ) // (60 * 60)
    else:
        hour = 0

    if t_dif > 60:
        min = int((t_dif - day * 24 * 60 * 60 - hour * 60 * 60)  // 60)
    else:
        min = 0

    return "{}d {}h {}m".format(day, hour, min)


start = "2021-12-14 09:32:45"
end = "2021-12-15 07:34:45"

ans = get_string_time_diff(start, end)
print(ans)