import os
import sys
import zipfile
import shutil
import fitz
import hashlib


def size_adaptive(origin_size):
    """
    自适应转换文件单位，初始文件单位必须为B
    :param origin_size: 原始文件大小（单位B），例如1342394
    :return: 返回文件大小的字符串，自适应地调整数值单位，使数值落在[0, 1024)上，单位为B/KB/MB/GB/TB，例如"1.3 MB"
    """
    if origin_size < 1024:
        return "%.1f B" % (origin_size / 1)
    elif origin_size < 1024 * 1024:
        return "%.1f KB" % (origin_size / 1024)
    elif origin_size < 1024 * 1024 * 1024:
        return "%.1f MB" % (origin_size / (1024 * 1024))
    elif origin_size < 1024 * 1024 * 1024 * 1024:
        return "%.1f GB" % (origin_size / (1024 * 1024 * 1024))
    else:
        return "%.1f TB" % (origin_size / (1024 * 1024 * 1024 * 1024))


def get_file_size(path_name, unit="B"):
    """
    获取指定路径的文件在指定单位下的文件大小
    :param path_name: 目标文件的相对/绝对路径，建议用绝对路径，例如"D:/Workspace/1.pdf"
    :param unit: 指定目标单位，默认值为"B"，例如"MB"
    :return: 返回一个浮点数，对应指定单位的文件大小，例如34.2912
    """
    simple_unit = 1
    if unit == "GB":
        simple_unit = 1024 * 1024 * 1024
    elif unit == "MB":
        simple_unit = 1024 * 1024
    elif unit == "KB":
        simple_unit = 1024
    elif unit == "B":
        pass
    try:
        file_size = os.path.getsize(path_name) / float(simple_unit)
    except Exception as err:
        print(err)
        return 0
    return round(file_size, 4)


def get_file_size_adaptive(path_name):
    """
    在get_file_size基础上外包一层自适应
    :param path_name: 目标文件的相对/绝对路径，建议用绝对路径，例如"D:/Workspace/1.pdf"
    :return: 返回一个完整的字符串，例如"1.3 MB"
    """
    origin_size = get_file_size(path_name)
    return size_adaptive(origin_size)


def unzip_file(input_path, output_path):
    """
    解压zip文件从指定zip文件路径到指定解压文件夹
    :param input_path: 待解压zip文件的路径
    :param output_path: 解压目标文件夹，需要保证文件夹已存在不然会报错
    :return: None
    """
    with zipfile.ZipFile(input_path, "r") as zf:
        for fn in zf.namelist():
            # print(fn)
            # fn.replace("||", "__")
            right_fn = "{0}{1}{2}".format(output_path, os.sep, fn).encode('cp437').decode('gbk').replace("\\\\\\\\", "\\\\").replace("||", "__")
            # print(right_fn)
            with open(right_fn, "wb") as output_file:  # 创建并打开新文件
                # print(fn)
                with zf.open(fn, "r") as origin_file:  # 打开原文件
                    shutil.copyfileobj(origin_file, output_file)  # 将原文件内容复制到新文件


def block_error(func):
    """
    装饰函数，用于避免mupdf的error打印（不影响程序运行）
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        sys.stderr = open(os.devnull, "w")
        results = func(*args, **kwargs)
        sys.stderr = sys.__stderr__
        return results
    return wrapper


@block_error
def pdf_count(input_filename):
    """
    数单个pdf文件的页数
    :param input_filename: pdf文件路径
    :return: 一个整数，若失败会返回0
    """
    try:
        pdf_document: fitz.fitz.Document = fitz.Document(input_filename)
        if len(pdf_document) == 0:
            print("Error in file {0}".format(input_filename))
        return len(pdf_document)
    except Exception as e:
        print("Error in file {0}:".format(input_filename), e)
        return 0


def clean_dir(path):
    """
    清空一个文件夹中的所有文件，需要保证其中都只是文件而非文件夹，否则会报错
    :param path: 待清空的文件夹路径
    :return: None
    """
    files = os.listdir(path)
    for file in files:
        full_path = "{0}{1}{2}".format(path, os.sep, file)
        if os.path.isfile(full_path):
            os.remove(full_path)


def level_print(level, name, content):
    """
    打印一个缩进字符串
    :param level: 整数，缩进级数，最小为0，每级多4个空格
    :param name: 左对齐前内容
    :param content: 左对齐后内容
    :return: None
    """
    level_content = ""
    for i in range(level):
        level_content += "    "
    level_content += "\\-- "
    level_content += name
    level_content = my_ljust(level_content, 68, " ")
    level_content += content
    print(level_content)


def sha256_part(filename):
    """
    在sha256基础上（总64位）仅显示前4位和后4位，中间56位用".."代替
    :param filename: 文件路径
    :return: 10位字符串，形如"ab41..160b"
    """
    sha256_content = sha256(filename)
    return sha256_content[:4] + ".." + sha256_content[-4:]


def sha256(filename):
    """
    对文件做sha256 Hash
    :param filename: 文件路径
    :return: 一个长度为64的sha256 Hash结果，以16进制形式显示，对应64*4个二进制位
    """
    with open(filename, "rb") as f:
        data = f.read()
    file_sha256 = hashlib.sha256(data).hexdigest()
    return file_sha256


def my_ljust(string, length, fill=" "):
    """
    由于python自带ljust对中文的宽度支持并不好，自制一个，假设中文宽度为英文字符的2倍
    :param string: 原字符串
    :param length: 左对齐位数
    :param fill: 填充内容，默认为空格
    :return: 返回ljust的结果
    """
    width = 0
    for ch in string:
        if ord(ch) < 256:
            width += 1
        else:
            width += 2
    # print(width, length)
    if width > length:
        return string
    for i in range(length - width):
        string += fill
    return string


if __name__ == "__main__":
    my_ljust("123sed./-\\我爱北京天安门", 10)
