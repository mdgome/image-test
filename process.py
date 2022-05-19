import os
from pathlib import Path

# 이미지 사이즈 조정을 위한 패키지
from PIL import Image

# file split 하기 위한 패키지
import random
import shutil
import numpy as np

# multiprocessing 용 패키지
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

# 진행률 확인 패키지
import tqdm

# 코드 실행시간 측정을 위한 패키지
import time

def make_dir(_dir):
    if not os.path.exists(_dir):
        os.makedirs(_dir)

def resize_image_save_file(file: str):
    """
    이미지 파일 resize, 저장
    file(str): 읽어올 파일
    """
    
    # image 파일 size 지정
    size = 416,416
    
    # 이미지 파일 상위 디렉토리
    src_dir = os.path.join(os.getcwd(), 'src')
    # 이미지 처리
    img = Image.open(os.path.join(src_dir,file))

    img_resize = img.resize(size)
    img.close()
    
    # 처리 완료된 이미지 파일 저장할 위치 지정
    desc_dir = os.path.join(os.getcwd(),'desc')
    make_dir(desc_dir)
    desc_file = os.path.join(desc_dir,file)
    # 처리 완료된 이미지 파일 저장
    img_resize.save(desc_file)
    
    if not os.path.isfile(desc_file):
        raise Exception("File Save Error: {}".format(desc_file))
    
    img_resize.close()
    
def multi_proc_file():
    """
    image 파일 resize 멀티 프로세싱
    func(functools.partial) resize, 저장 기능 함수
    """
    # 쓰레드에서 사용하기 위한 함수
    func = partial(resize_image_save_file)
    # 처리할 파일 전체 리스트
    file_list = os.listdir('./src')
    
    # tqdm == 진행률 확인
    with tqdm.tqdm(desc="resizing images and save", total=len(file_list)) as pbar:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                # file_list 안 file들 멀티 프로세싱으로 resize_image_save_file 실행
                executor.submit(func, file) for file in file_list
            }
            for future in as_completed(futures):
                pbar.update(1)
def single_proc_file():
    """
    단일 프로세싱 image 파일 resize
    """
    start_time = time.time()
    
    file_list = os.listdir('./src')
    
    with tqdm.tqdm(desc="resizing images and save", total=len(file_list)) as pbar:
           for file in file_list:
                resize_image_save_file(file)
                pbar.update(1)
    print("실행 시간(초): {}".format(time.time() - start))
    
def split_file(path: str):
    """
    train, valid, test split 
    8:1:1(train:valid:test) 
    path = image file 위치
    
    path(str): iamge 파일이 위치한 절대 경로
    """
    
    val_ratio = 0.1
    test_ratio = 0.1
    
    file_list = os.listdir(path)
    np.random.shuffle(file_list)
    train_filenames, val_filenames, test_filenames = np.split(np.array(file_list),
                                                          [int(len(file_list)* (1 - (val_ratio + test_ratio))), 
                                                           int(len(file_list)* (1 - test_ratio))])
    train_filenames = [os.path.join(path, file) for file in train_filenames.tolist()]
    val_filenames = [os.path.join(path, file) for file in val_filenames.tolist()]
    test_filenames = [os.path.join(path, file) for file in test_filenames.tolist()]
    
    return train_filenames, val_filenames, test_filenames

def copy_files(src_file: str, dest_file: str):
    shutil.copy(src_file, dest_file)

def multi_proc_split():
    """
    image 파일 resize 멀티 프로세싱
    func(functools.partial) resize, 저장 기능 함수
    """
    # 쓰레드에서 사용하기 위한 함수
    func = partial(copy_files)
    
    # target directory
    root_path = os.path.join(os.getcwd(), 'result')
    
    make_dir(root_path)
    
    train_dir = os.path.join(root_path, 'train')
    val_dir = os.path.join(root_path, 'valid')
    test_dir = os.path.join(root_path, 'test')
    
    make_dir(train_dir)
    make_dir(val_dir)
    make_dir(test_dir)
    
    train_filenames = []
    val_filenames = []
    test_filenames = []
    
    path = os.path.join(os.getcwd(), 'desc')
    train_filenames, val_filenames, test_filenames = split_file(path)
    
    # tqdm == 진행률 확인
    # train dir
    with tqdm.tqdm(desc="train split", total=len(train_filenames)) as pbar:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                # filenames 안 file들 멀티 프로세싱으로 copy 실행
                executor.submit(func,dest_file=train_dir, src_file=file)for file in train_filenames
            }
            for future in as_completed(futures):
                pbar.update(1)
    del(train_filenames)
    del(train_dir)
    # valid dir
    with tqdm.tqdm(desc="valid split", total=len(val_filenames)) as pbar:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                # filenames 안 file들 멀티 프로세싱으로 copy 실행
                executor.submit(func,dest_file=val_dir, src_file=file) for file in val_filenames
            }
            for future in as_completed(futures):
                pbar.update(1)
    del(val_filenames)
    del(val_dir)
    # test dir
    with tqdm.tqdm(desc="test split", total=len(test_filenames)) as pbar:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                # filenames 안 file들 멀티 프로세싱으로 copy 실행
                executor.submit(func,dest_file=test_dir, src_file=file) for file in test_filenames
            }
            for future in as_completed(futures):
                pbar.update(1)

if __name__ == "__main__" :
    # desc 안 파일 개수 확인
    print("desc 디렉토리 안 파일 개수: {}".format(len(os.listdir('./desc'))))
    # 시작 시간 초기화
    start_time = time.time()
    
    # image resize
    multi_proc_file()
    
    # 실행 시간 확인
    print("resize multi processing 실행 시간(초): {}".format(time.time() - start_time))
    
    # desc 안 파일 개수 확인
    print("desc 디렉토리 안 파일 개수: {}".format(len(os.listdir('./desc'))))
    
    # direcotry split
    input_dir = os.path.join(os.getcwd(),'desc')

    # 시작 시간 초기화
    start_time = time.time()
    
    # 8:1:1 (train:valid:test) 비율로 split 진행
    multi_proc_split()
    
    # 실행 시간 확인
    print("file split 실행 시간(초): {}".format(time.time() - start_time))
    
