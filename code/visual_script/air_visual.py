# coding:utf-8
# This is the script of visual model for airstudio.
# Author: Zhiqiang Yuan

import os, pickle
import shutil
from functools import wraps

from torch.utils.tensorboard import SummaryWriter

_init_visual_global = False
_writer_global = None
_savepath_global = "/data/log/visual"

################## SCHEDULE ###############################

def create_file(save_path):
    src_path = os.path.abspath(save_path)
    if not os.path.exists(src_path):
        os.makedirs(src_path)
    os.system("touch {}".format(save_path))

def log_schedule(schedule, params, save_path="/data/log/schedule.pkl"):
    # save schedule, loss, accuracy to save_path
    schedule = float(schedule)

    # check
    if schedule<0 or schedule>1:
        return False, "the range of schedule is [0, 1]."

    # if not exist
    if not os.path.exists(save_path):
        create_file(save_path)
        data = {}
    else:
        with open(save_path,'rb') as f:
            data = pickle.load(f)

        # if schedule has cache
        if max(data.keys()) > schedule:
            data = {}

    data[schedule] = params

    with open(save_path,'wb') as f:
        pickle.dump(data, f)
    return True, "save schedule successfully."

# 加载schedule
def load_schedule(save_path):
    with open(save_path, 'rb') as f:
        data = pickle.load(f)
    return data


################## VISUAL ###############################

# wrapper
def check_codetype(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        # check code type
        if "code_type" in kwargs.keys():
            code_type = kwargs['code_type']
        else:
            code_type = args[0]

        if code_type in ["pytorch", "tensorflow"]:
            global _init_visual_global
            global _writer_global
            if not _init_visual_global:
                visual_init(code_type)
                _init_visual_global = True

            kwargs['writer'] = _writer_global
            ans = func(*args, **kwargs)
            return ans
        else:
            return "no implementation of {}, only support: pytorch, tensorflow.".format(code_type)

    return decorator

# set work path
def set_savepath(savepath):
    global _savepath_global
    _savepath_global = savepath

# visual init
def visual_init(code_type):
    save_path = _savepath_global

    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    os.mkdir(save_path)
    writer = SummaryWriter(log_dir=save_path)

    global _init_visual_global
    global _writer_global
    _init_visual_global = True
    _writer_global = writer

    return writer

def visual_close(code_type):
    if code_type == "pytorch":
        global _writer_global
        _writer_global.close()
    else:
        print("No implement.")

@check_codetype
def add_scalad(code_type, tag, scalar_value, global_step=None, walltime=None, writer=_writer_global):
    if code_type == "pytorch":
        writer.add_scalar(tag=tag, scalar_value=scalar_value, global_step=global_step, walltime=walltime)
    else:
        print("No implement.")

@check_codetype
def add_histogram(code_type, tag, values, global_step=None, bins='tensorflow', walltime=None, max_bins=None, writer=_writer_global):
    if code_type == "pytorch":
        writer.add_histogram(tag, values, global_step=global_step, bins=bins, walltime=walltime, max_bins=max_bins)
    else:
        print("No implement.")

@check_codetype
def add_image(code_type, tag, img_tensor, global_step=None, walltime=None, dataformats='CHW', writer=_writer_global):
    if code_type == "pytorch":
        writer.add_image(tag, img_tensor, global_step=global_step, walltime=walltime, dataformats=dataformats)
    else:
        print("No implement.")

@check_codetype
def add_images(code_type, tag, img_tensor, global_step=None, walltime=None, dataformats='NCHW', writer=_writer_global):
    if code_type == "pytorch":
        writer.add_images(tag, img_tensor, global_step=global_step, walltime=walltime, dataformats=dataformats)
    else:
        print("No implement.")

@check_codetype
def add_figure(code_type, tag, figure, global_step=None, close=True, walltime=None, writer=_writer_global):
    if code_type == "pytorch":
        writer.add_figure(tag, figure, global_step=global_step, close=close, walltime=walltime)
    else:
        print("No implement.")

@check_codetype
def add_video(code_type, tag, vid_tensor, global_step=None, fps=4, walltime=None, writer=_writer_global):
    if code_type == "pytorch":
        writer.add_video(tag, vid_tensor, global_step=global_step, fps=fps, walltime=walltime)
    else:
        print("No implement.")

@check_codetype
def add_text(code_type, tag, text_string, global_step=None, walltime=None, writer=_writer_global):
    if code_type == "pytorch":
        writer.add_text(tag, text_string, global_step=global_step, walltime=walltime)
    else:
        print("No implement.")

@check_codetype
def add_graph(code_type, model, input_to_model=None, verbose=False, use_strict_trace=True, writer=_writer_global):
    if code_type == "pytorch":
        writer.add_graph(model, input_to_model=input_to_model, verbose=verbose, use_strict_trace=use_strict_trace)
    else:
        print("No implement.")

if __name__=="__main__":

    # Use schedule

    #schedule = 0.3

    #loss = 0.1
    #acc = 0.9
    #save_path = "air.pkl"
    #log_schedule(schedule, loss, acc, save_path)

    #data = load_schedule(save_path)
    #print(data)

    # Use airvisual

    # set_savepath("visual1")
    # add_scalad(code_type="pytorch", tag="test", scalar_value=3)

    # writer = SummaryWriter(log_dir="visual_air")
    # writer.add_scalar(tag="tag", scalar_value=2)
    # writer.close()

    save_path = "data/log/schedule.pkl"
    create_file(save_path)