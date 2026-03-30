from pathlib import Path

current_dir = Path.cwd()
# Path(__file__) : 현재 실행 중인 python script file의 절대 경로
# .name : 경로를 제외한 현재 파일명만 추출
current_file = Path(__file__).name

print(f"Files in {current_dir}:")

# iterdir() : iterate directory - current_dir 내부를 반복(순회)하는 함수
for filepath in current_dir.iterdir():
    if filepath.name == current_file:
        continue
    
    print(f" - {filepath.name}")

    if filepath.is_file():
        content = filepath.read_text(encoding='utf-8')
        print(f" Content: {content}")