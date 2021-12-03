import json
import time, os
import shutil
import zipfile, pickle
import rarfile
import tarfile


# 得到上一级路径
def get_super_dir(path):
    return os.path.split(path)[0]


def uncompress(src_file, dest_dir):
    file_name, file_type = os.path.splitext(src_file)
    # try:
    if file_type == '.tgz' or file_type == '.tar' or file_type == '.gz':
        tar = tarfile.open(src_file)
        tar.extractall(dest_dir)
        # for name in tar.getnames():
        #     tar.extract(name, dest_dir)
        tar.close()
    elif file_type == '.zip':
        zip_file = zipfile.ZipFile(src_file)
        for names in zip_file.namelist():
            zip_file.extract(names, dest_dir)
        zip_file.close()
    # elif file_type == '.rar':
    #     rar = rarfile.RarFile(src_file)
    #     rar.extractall(dest_dir)
    #     rar.close()
    else:
        return False, '文件格式不支持或者不是压缩文件'
    # except Exception as ex:
    #     return False, str(ex)
    # return True, 'success'


# 拷贝压缩文件到文件夹
def copy_compress_to_dir(compress_file, out_dir):
    tmp_name = get_super_dir(out_dir)
    tmp_name = os.path.join(tmp_name, compress_file.split("/")[-1])

    if compress_file != tmp_name:
        shutil.copy(compress_file, tmp_name)

    uncompress(tmp_name, out_dir)
    os.remove(tmp_name)

    # 如果压缩文件夹中只有一个文件，则再往下去一级
    all_files = [f for f in os.listdir(out_dir) if f[0] != "."]
    if len(all_files) == 1:
        os.system("mv {}/* {}".format(
            os.path.join(out_dir, all_files[0]),
            out_dir
        ))
        os.system("rm -rf {}".format(os.path.join(out_dir, all_files[0])))


if __name__ == "__main__":
    copy_compress_to_dir(
        "./code.zip",
        "./dst"
    )
