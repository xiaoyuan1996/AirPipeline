# coding:utf-8
# This is test script of visual model for airstudio.
# Author: Zhiqiang Yuan

import air_visual as av

# Use schedule
schedule = 0.4
params = {
    "loss": 0.1,
    "acc": 0.8
}
save_path = "air.pkl"
av.log_schedule(schedule, params, save_path)

data = av.load_schedule(save_path)
print(data)

# Use visual
av.set_savepath("visual3")
av.add_scalad(code_type="pytorch", tag="test", scalar_value=4)
av.add_text(code_type="pytorch", tag="text", text_string="aaa")
av.visual_close(code_type="pytorch")
