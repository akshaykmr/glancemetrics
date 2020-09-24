# misc utils
from pathlib import Path
import itertools as it
from typing import List, Callable, Any, Dict


def group_by(lizt: List[Any], key: Callable[[Any], Any]) -> Dict[Any, List[Any]]:
    sorted_list = sorted(lizt, key=key)
    return {k: list(v) for k, v in it.groupby(sorted_list, key)}


def ensure_file_exists(filepath: str) -> Path:
    path = Path(filepath).resolve()
    if not path.exists():
        print(
            f"""ERROR: file "{filepath}" not found. Please check the file path. \n
If using with Docker, you need to mount the volume
else docker would not be able to see the file.

DOCKER-TIP: if your file lies in /tmp/access.log then
easiest way is to mount the folder to /data of container like so:
docker run -v /tmp:/data glancemetrics -f /data/access.log
"""
        )
        exit(-1)
    return path
