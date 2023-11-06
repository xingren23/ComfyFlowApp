
import shutil
import os
import sys
import re
import pygit2
import subprocess

re_requirement = re.compile(r"\s*([-_a-zA-Z0-9]+)\s*(?:==\s*([-+_.a-zA-Z0-9]+))?\s*")


python = sys.executable
default_command_live = (os.environ.get('LAUNCH_LIVE_OUTPUT') == "1")
index_url = os.environ.get('INDEX_URL', "")

modules_path = os.path.dirname(os.path.realpath(__file__))
script_path = os.path.dirname(modules_path)
dir_repos = "repositories"

REINSTALL_ALL = False

def git_clone(url, dir, name, hash=None):
    try:
        try:
            repo = pygit2.Repository(dir)
            print(f'{name} exists.')
        except:
            if os.path.exists(dir):
                shutil.rmtree(dir, ignore_errors=True)
            os.makedirs(dir, exist_ok=True)
            repo = pygit2.clone_repository(url, dir)
            print(f'{name} cloned.')

        remote = repo.remotes['origin']
        remote.fetch()

        commit = repo.get(hash)

        repo.checkout_tree(commit, strategy=pygit2.GIT_CHECKOUT_FORCE)
        print(f'{name} checkout finished.')
    except Exception as e:
        print(f'Git clone failed for {name}: {str(e)}')

def repo_dir(name):
    return os.path.join(script_path, dir_repos, name)


def requirements_met(requirements_file):
    """
    Does a simple parse of a requirements.txt file to determine if all rerqirements in it
    are already installed. Returns True if so, False if not installed or parsing fails.
    """

    import importlib.metadata
    import packaging.version

    with open(requirements_file, "r", encoding="utf8") as file:
        for line in file:
            if line.strip() == "":
                continue

            m = re.match(re_requirement, line)
            if m is None:
                return False

            package = m.group(1).strip()
            version_required = (m.group(2) or "").strip()

            if version_required == "":
                continue

            try:
                version_installed = importlib.metadata.version(package)
            except Exception:
                return False

            if packaging.version.parse(version_required) != packaging.version.parse(version_installed):
                return False

    return True

def run(command, desc=None, errdesc=None, custom_env=None, live: bool = default_command_live) -> str:
    if desc is not None:
        print(desc)

    run_kwargs = {
        "args": command,
        "shell": True,
        "env": os.environ if custom_env is None else custom_env,
        "encoding": 'utf8',
        "errors": 'ignore',
    }

    if not live:
        run_kwargs["stdout"] = run_kwargs["stderr"] = subprocess.PIPE

    result = subprocess.run(**run_kwargs)

    if result.returncode != 0:
        error_bits = [
            f"{errdesc or 'Error running command'}.",
            f"Command: {command}",
            f"Error code: {result.returncode}",
        ]
        if result.stdout:
            error_bits.append(f"stdout: {result.stdout}")
        if result.stderr:
            error_bits.append(f"stderr: {result.stderr}")
        raise RuntimeError("\n".join(error_bits))

    return (result.stdout or "")


def run_pip(command, desc=None, live=default_command_live):
    try:
        index_url_line = f' --index-url {index_url}' if index_url != '' else ''
        return run(f'"{python}" -m pip {command} --prefer-binary{index_url_line}', desc=f"Installing {desc}",
                   errdesc=f"Couldn't install {desc}", live=live)
    except Exception as e:
        print(e)
        print(f'CMD Failed {desc}: {command}')
        return None

def prepare_environment():
    print(f"Python {sys.version}")

    requirements_file = os.environ.get('REQS_FILE', "requirements.txt")

    comfy_repo = os.environ.get('COMFY_REPO', "https://github.com/xingren23/ComfyUI")
    comfy_commit_hash = os.environ.get('COMFY_COMMIT_HASH', "2a134bfab9788b6a0a70aea3172d8e3fc904b414")

    comfyui_name = 'ComfyUI'
    # git_clone(comfy_repo, repo_dir(comfyui_name), "ComfyUI Engine", comfy_commit_hash)
    sys.path.append(os.path.join(script_path, dir_repos, comfyui_name))

    if REINSTALL_ALL or not requirements_met(requirements_file):
        run_pip(f"install -r \"{requirements_file}\"", "requirements")

def prepare_comfyui_path():
    comfyui_path = os.path.join(os.path.dirname(__file__), '..', 'repositories', 'ComfyUI')
    if comfyui_path not in sys.path:
        print(f"add comfyui path {comfyui_path}")
        sys.path.append(comfyui_path)
    return comfyui_path