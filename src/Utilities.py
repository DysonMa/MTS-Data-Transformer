import os


def linear_regression(x, a, b):
    return a * x + b


def get_file_path(folder_path, file_name):
    return os.path.join(folder_path, file_name)


def get_folder_path(folder_name):
    return os.path.realpath(f"../{folder_name}")
