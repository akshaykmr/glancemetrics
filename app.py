from pathlib import Path
from glancemetrics.argsparser import parser


def _validate_file_path(filepath: str) -> Path:
    path = Path(filepath).resolve()
    if not path.exists():
        print(f"""ERROR: file "{filepath}" not found. Please check the file path. \n
If using with Docker, you need to mount the volume
else docker would not be able to see the file.

DOCKER-TIP: if your file lies in /tmp/access.log then
easiest way is to mount the folder to /data of container like so:
docker run -v /tmp:/data glancemetrics -f /data/access.log
""")
        exit(-1)
    return path

args = parser.parse_args()

_validate_file_path(args.file)
