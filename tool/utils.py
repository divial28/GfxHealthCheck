from pathlib import Path
from typing import List
import subprocess
import os
import shutil
import tarfile


def run(
    cmd: List[str],
    shell: bool = False,
    check: bool = True,
    universal_newlines: bool = True,
    log_dir: str = None,
    sudo: bool = False,
    timeout: int = 5,
) -> str:
    try:
        if sudo:
            print("running '{}' with sudo".format(" ".join(cmd)))
            command = ["sudo", *cmd]
        else:
            command = cmd
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=universal_newlines,
            check=check,
            shell=shell,
            timeout=timeout,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            "Command '{}' failed with exit code {}:\n{}".format(
                " ".join(cmd), e.returncode, e.stderr.strip()
            )
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            "Command '{}' hanged for {} seconds".format(" ".join(cmd), timeout)
        ) from e

    if not log_dir is None:
        cmd_name = cmd[0].split(" ")[0] + ".log"
        file_name = os.path.join(log_dir, cmd_name)
        with open(file_name, "a") as f:
            f.write("=" * 40 + "\n")
            f.write(" ".join(cmd) + "\n")
            f.write("stdout:\n")
            f.write(result.stdout)
            f.write("stderr:\n")
            f.write(result.stderr)
            f.write("\n" + "=" * 40 + "\n")

    return result.stdout.strip()


def local_path(path: str) -> str:
    script_dir = Path(__file__).parent.resolve()
    return str(script_dir.joinpath("..", path).resolve().absolute())


def force_mkdir(path: str):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    os.makedirs(path)


def create_acrhive(src_dir: str, dest_path: str):
    with tarfile.open(dest_path, "w:gz") as tar:
        tar.add(src_dir, arcname=os.path.basename(src_dir))
