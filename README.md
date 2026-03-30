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
