from pathlib import Path
import subprocess
import os
import shutil

COMMAND_TIMEOUT = 5


def run(
    cmd: list[str],
    shell: bool = False,
    check: bool = True,
    universal_newlines: bool = True,
    log_dir: str = None,
) -> str:
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=universal_newlines,
            check=check,
            shell=shell,
            timeout=COMMAND_TIMEOUT,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            "Command '{}' failed with exit code {}:\n{}".format(
                " ".join(cmd), e.returncode, e.stderr.strip()
            )
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            "Command '{}' hanged for '{}'".format(" ".join(cmd), COMMAND_TIMEOUT)
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


def local_path(path: str) -> Path:
    script_dir = Path(__file__).parent.resolve()
    return script_dir.joinpath("..", path).resolve().absolute()


def force_mkdir(path: str):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    os.makedirs(path)
