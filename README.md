# 가상환경은 python venv로 진행
```bash
python3 -m venv .venv
source .venv/bin/activate
```

# 관련 패키지 설치
```bash
python3 -m pip install -U pip
python3 -m pip install boto3
python3 -m pip install image
python3 -m pip install tqdm
python3 -m pip install pathlib
python3 -m pip install split-folder
python3 -m pip install numpy
```

# S3 연결을 위한 설정 
```bash
mkdir config
sudo cat << EOF | sudo tee -a config/config.ini
# 아래 내용 기입
[S3]
S3_BUCKET_NAME={버킷 이름}
S3_PREFIX={접근할 파일 디렉토리 경로}
AWS_ACCESS_KEY_ID={Access key}}
AWS_SECRET_ACCESS_KEY={Secret access key}
EOF
```

# run command
```bash
python3 -m process
```