# 이미지 사이즈 조정을 위한 패키지
from PIL import Image

# file split 하기 위한 패키지
import splitfolders
import os
from pathlib import Path
import shutil

# multiprocessing 용 패키지
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

# 진행률 확인 패키지
import tqdm

# 코드 실행시간 측정을 위한 패키지
import time


def resize_image_save_file(file):
    """
    이미지 파일 resize, 저장
    file(str): 읽어올 파일
    """
    if not os.path.isfile(file):
        raise Exception("File not found: {}".format(file))
    
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
    if not os.path.exists(desc_dir):
        os.makedirs(desc_dir)
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
    
    # tqdm == 진행률 확인
    with tqdm.tqdm(desc="resizing images and save", total=len(file_list)) as pbar:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                # file_list 안 file들 멀티 프로세싱으로 resize_image_save_file 실행
                executor.submit(func, file) for file in file_list
            }
            for future in as_completed(futures):
                pbar.update(1)
    

if __name__ == "__main__" :
    # 시작 시간 초기화
    start_time = time.time()
    
    # image resize
    multi_proc_file()
    
    # 실행 시간 확인
    print("resize 실행 시간(초): {}".format(time.time() - start))
    
    # direcotry split
    input_dir = os.path.join(os.getcwd(),'desc')

    # 시작 시간 초기화
    start_time = time.time()
    
    # 8:1:1 (train:valid:test) 비율로 split 진행
    splitfolders.ratio(input_dir, output="output", seed=1337, ratio=(.8, .1, .1), group_prefix=None, move=False)
    
    # 실행 시간 확인
    print("file split 실행 시간(초): {}".format(time.time() - start))