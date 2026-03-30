# de-workshop

## docker
docker container는 stateless로 컨테이너 내부에서 변경한 사항은 컨테이너 종료 후 재시작 시 저장되지 않는다.

```bash
docker rm $(docker ps -aq)
```
종료된 컨테이너는 다시 시작할 수는 있지만 권장되는 방식은 아니므로, 위의 명령어를 입력해서 모두 삭제하는 것이 좋다.

```bash
docker run -it --rm ubuntu
```
종료 시 자동으로 삭제되도록 `--rm` 옵션을 추가해 종료 시 자동으로 삭제시키는 방법도 있다.

main os에 있는 파일을 container에서도 사용하려면
```bash
docker run -it --rm -v $(pwd)/dir_name:/moved_dir_name/dir_name_ex --entrypoint=bash python:3.13.11-slim
```

## Data Pipeline

입력을 받아 출력을 생성한다.

**pyarrow** : Apache Arrow라는 기술을 파이썬에서 사용하기 위해 만든 라이브러리
- 대용량 데이터를 다룰 때 연산 속도를 끌어올리고 시스템 간 데이터 이동을 매끄럽게 만들어주는 역할
- Column형 메모리 구조 
- Zero-Copy : 공통된 메모리 포맷 사용으로 포맷 변환 맞출 필요 없이(복사 과정 없이) 데이터 넘겨줘서 병목 해결
- Parquet 파일 사용할 때, 표준처럼 쓰임
ex1) data pipeline 구축해서 매일 쌓이는 로그나 원천 데이터를 효율적인 Parquet 파일로 벼환해서 저장소에 적재할 때
ex2) Pandas로 많은 양의 데이터 다룰 때 메모리 터지거나 느려지는 현상 막고 싶을 때

### 왜 Parquet을 쓸까?
- 스토리지 비용을 줄이는 게 회사 입장에서는 중요한데, CSV 파일을 Parquet으로 변환하면 100GB짜리를 20~30GB로 줄이므로 AWS S3 같은 클라우드 환경에서는 저장 비용 절감 효과가 크다.
- 특정 컬럼만 필요한 경우, csv는 행을 한 줄씩 다 읽어야 되지만 parquet은 특정 컬럼만 바로 읽을 수 있다.
- 데이터 정합성(타입 보존) : csv는 읽어올 때마다 데이터 타입 추론 과정에서 parsing하거나 강제 변환해야 해서 에러가 잦다. parquet은 파일 자체에 meta data가 있어서 타입 추론이 필요없이 정확하게 안전하게 제공 가능하다. 

**uv** : 초고속 파이썬 패키지 및 프로젝트 관리 도구
- `pip`, `virtualenv`, `poetry` 같은 도구들을 통합하고 속도를 올린 엔진
- `un venv` : 가상환경 생성, `un pip` : 패키지 설치, `un sync` : 프로젝트 의존성 관리
- Global Cache 사용해서 한 번 다운받은 패키지는 복사 없이 링크만 걸어줘서 디스크 용량과 설치 시간 확 줄여줌
```bash
uv init --python 3.13
uv run python -V

uv run which python
# 우리가 설정한 가상환경 속 파이썬 파일 경로가 나온다.
```
설치된 파이썬 버전이 3.12여도 실행할 때는 uv로 설정한 파이썬 버전인 3.13이 실행된다. 

## Dockerfile
1번째 줄 : 출처
`FROM python:3.13.11-slim`

뭘 설치할 지(build 되는 동안 실행할 명령어)
`RUN pip install pandas pyarrow`

pipeline copy 하도록
```bash
WORKDIR /code
COPY pipeline.py .
# 1st : source file
# 2nd : destination -> 내 컴퓨터의 pipeline.py를 현재 위치인 /code로 복사 (WORKDIR 없었으면 root directory에)
```

```bash
docker build -t test:pandas .
# test : image 이름
# pandas : image의 버전이나 특징을 나타내는 tag(default : 'latest')
# . : 현재 디렉토리에 있는 Dockerfile 사용한다.
```

**`run` Options**
`-t`(tty) : 컨테이너 내부에 가상 터미널 할당
`-i`(interactive) : 사용자가 키보드로 입력을 주고 받을 수 있도록 표준 입력(stdin)을 연다.
-> `-i` 가 없으면 컨테이너로 내 키보드 입력을 보낼 수 없고 `-t`가 없으면 text data만 나오고, bash나 python interpreter같은 프로그램이 제어할 프로세스가 없다고 판단해 종료되거나 입력을 받지 못하는 상태가 된다. 
- `Ctrl + C` 눌렀는데 가상 터미널 할당 안 되어있기 때문에 중단 신호임을 알아듣지 못한다.

**`build`** Option
- `-t` : tag - 이미지의 이름 설정


Docker의 **Build Cache** 기능으로 인해 빌드 속도가 21.9초에서 0.1초로 단축됐다.
-> 빌드할 때 썼던 Dockerfile이랑 내용이 같고, 복사할 소스코드인 pipeline.py도 동일하면 pip install을 새로할 필요 없이 아까 만들어둔 Layer를 재사용 = Layer Caching

`COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin`
이미 만들어진 `uv` 전용 이미지에서 uv 실행 파일만 빼서 내 이미지의 /bin 폴더로 복사해줘.

```bash
# Dockerfile
RUN uv sync --locked
```
`pip install -r requirments.txt`와 유사
- 환경 동기화 : `project.toml` 또는 `uv.lock` 파일을 읽어 현재 프로젝트에 필요한 패키지들을 한 번에 설치
- 정리 기능 : 이전에 설치됐지만, 지금 필요 없는 패키지가 있다면 `uv sync`가 알아서 삭제
`--locked` option
- `uv.lock`에 적힌 정확한 버전과 해시값대로만 설치
- 빌드 실패 방지 : 누군가 패키지 설정 바꿨는데, `uv.lock` 업데이트 하지 않았으면 빌드 과정에서 에러를 내고 멈춘다.

사용 이유
- **재현성(Reproducibility)** : 1년 뒤에 다시 빌드해도 똑같은 환경 보장
- 속도 : uv >> pip (병렬 설치 & 캐싱 능력)
- `--locked`를 통해 배포 환경이 로컬 개발 환경과 완전히 일치