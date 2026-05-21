import subprocess
import sys


def run(command: list[str]) -> None:
    print("\nВыполняется:", " ".join(command))
    result = subprocess.run(command)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    run([sys.executable, "preprocess.py"])
    run([sys.executable, "train_model.py"])
    print("\nГотово. Теперь можно запускать API командой:")
    print("uvicorn main:app --reload")
