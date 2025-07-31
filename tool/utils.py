import subprocess

COMMAND_TIMEOUT = 5


def run(
    cmd: list[str],
    shell: bool = False,
    check: bool = True,
    universal_newlines: bool = True,
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

    return result.stdout.strip()
