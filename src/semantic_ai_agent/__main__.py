from multiprocessing import Process

from .api import run_api


def main() -> None:
    api_process = Process(target=run_api)

    api_process.start()

if __name__ == "__main__":
    main()
