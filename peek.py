# -*- coding: utf-8 -*-
import os.path

from tools import *


def count_one_zip(path, level):
    """
    递归地去求一个zip文件中的层级结构
    :param path: zip文件的路径
    :param level: 当前缩进层级，最小为0
    :return: count, count_dic: count为该zip中总页数，count_dic为一个dict，对应各种类型文件各自的数量与页数
    """
    tmp_count = 0
    while os.path.exists("tmp_%d" % tmp_count):
        tmp_count += 1
    tmp_path = "tmp_%d" % tmp_count
    os.mkdir(tmp_path)
    unzip_file(path, tmp_path)
    count = 0
    files = os.listdir(tmp_path)
    count_dic = dict()
    for one_type in ["png", "jpg", "jpeg", "pdf", "pdf_count"]:
        count_dic[one_type] = 0
    for one_file in files:
        file_type = one_file.split(".")[-1]
        one_file_full_path = "{0}{1}{2}".format(tmp_path, os.sep, one_file)
        if file_type.lower() in ["png", "jpg", "jpeg"]:
            count += 1
            count_dic[file_type.lower()] += 1
            level_print(level, one_file, "共 1  页  {0}  {1}".format(get_file_size_adaptive(one_file_full_path).rjust(9), sha256_part(one_file_full_path)))
        elif file_type.lower() == "pdf":
            tmp = pdf_count(one_file_full_path)
            count += tmp
            count_dic["pdf"] += 1
            count_dic["pdf_count"] += tmp
            level_print(level, one_file, "共{0}页  {1}  {2}".format(str(tmp).center(4), get_file_size_adaptive(one_file_full_path).rjust(9), sha256_part(one_file_full_path)))
        elif file_type.lower() == "zip":
            level_print(level, one_file, "          {0}  {1}".format(get_file_size_adaptive(one_file_full_path).rjust(9), sha256_part(one_file_full_path)))
            count_tmp, count_dic_tmp = count_one_zip(one_file_full_path, level + 1)
            count += count_tmp
            for one_type in ["png", "jpg", "jpeg", "pdf", "pdf_count"]:
                count_dic[one_type] += count_dic_tmp[one_type]
        else:
            print("Bad file type: {0}. Skipped it.".format(file_type))

    clean_dir(tmp_path)
    os.removedirs(tmp_path)
    return count, count_dic


def peek_one_company(path, company_name):
    """
    检索一家企业的层级结构
    :param path: 该企业的文件夹路径
    :param company_name: 该企业名
    :return: None
    """
    count_path = "{0}{1}{2}".format(path, os.sep, "count.txt")
    if os.path.exists(count_path):
        with open(count_path, "r") as f:
            real_zips_count = int(f.readline().split()[0])
    else:
        real_zips_count = 0
    # print("real_zips_count:", real_zips_count)
    files = os.listdir(path)
    files = [file for file in files if file.split(".")[-1] == "zip"]
    if len(files) == 0:
        print("company_name: {0} Empty Warning! Skipped it.".format(company_name))
        return
    sample_zips_count = len(files)
    sample_pages = 0
    count_dic = dict()
    print("")
    level_print(0, company_name, "")
    for one_type in ["png", "jpg", "jpeg", "pdf", "pdf_count"]:
        count_dic[one_type] = 0
    for one_file in files:
        one_file_full_path = "{0}{1}{2}".format(path, os.sep, one_file)
        level_print(1, one_file, "          {0}  {1}".format(get_file_size_adaptive(one_file_full_path).rjust(9), sha256_part(one_file_full_path)))
        count_tmp, count_dic_tmp = count_one_zip(one_file_full_path, 2)
        sample_pages += count_tmp
        for one_type in ["png", "jpg", "jpeg", "pdf", "pdf_count"]:
            count_dic[one_type] += count_dic_tmp[one_type]
    print("company_name: {0} sample_zips_count: {1} sample_pages: {2}['pdf': {5}({6}), 'png': {7}({7}), 'jpg': {8}({8}), 'jpeg': {9}({9})] real_zips_count: {3}, real_pages_estimated: {4:.2f}".format(
        company_name,
        sample_zips_count,
        sample_pages,
        real_zips_count,
        sample_pages / sample_zips_count * real_zips_count,
        count_dic.get("pdf"),
        count_dic.get("pdf_count"),
        count_dic.get("png"),
        count_dic.get("jpg"),
        count_dic.get("jpeg")
    ))


def peek(path, company_name_given=None):
    """
    检索顶层文件夹（如"data/test"）中所有企业文件夹的层级结构
    :param path: 顶层文件夹的路径
    :param company_name_given: 可以指定只要检索哪一家企业，不指定则默认为全部
    :return: None
    """
    companies = os.listdir(path)
    print("\nFolder {0}:".format(path), companies)
    if company_name_given:
        companies = [item for item in companies if item == company_name_given]
    print("Choose:", companies)
    for one_company in companies:
        peek_one_company("{0}{1}{2}".format(path, os.sep, one_company), one_company)


if __name__ == "__main__":
    data_path = "data"
    # 第1个参数是顶级文件夹名(必选, 必须在data目录下), 第2个参数是指定单家公司(可选)
    if len(sys.argv) >= 3:
        peek(os.path.join(data_path, sys.argv[1]), sys.argv[2])
    elif len(sys.argv) >= 2:
        peek(os.path.join(data_path, sys.argv[1]))
    elif os.path.exists(os.path.join(data_path, "test")):
        peek(os.path.join(data_path, "test"))
    else:
        print("Please choose an existing folder!")
