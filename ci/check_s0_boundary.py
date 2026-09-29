"""Reject product source added before its CI commands exist at S0."""

import argparse
from pathlib import Path


ALLOWED = {
    "java": ("backend/java", {"InfraPlaceholder.java", "Dockerfile"}),
    "web": ("clients/web", set()),
    "desktop": ("clients/desktop", set()),
    "mobile": ("clients/mobile", set()),
}


def unexpected_files(root, profile):
    relative_dir, allowed = ALLOWED[profile]
    directory = root / relative_dir
    if directory.is_symlink():
        return [directory.name]
    if not directory.is_dir():
        return []
    unexpected = []
    for path in directory.rglob("*"):
        if path.is_dir() and not path.is_symlink():
            continue
        relative = path.relative_to(directory).as_posix()
        if path.is_symlink():
            unexpected.append(relative)
            continue
        if relative in allowed:
            continue
        if (path.name == ".gitkeep" and path.is_file() and not path.is_symlink()
                and path.read_bytes() in (b"", b"\n", b"\r\n")):
            continue
        unexpected.append(relative)
    return sorted(unexpected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=ALLOWED)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    unexpected = unexpected_files(root, args.profile)
    if unexpected:
        parser.exit(1, f"{args.profile} source grew; add its CI commands: {', '.join(unexpected)}\n")


if __name__ == "__main__":
    main()
