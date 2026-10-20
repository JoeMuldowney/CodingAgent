from pathlib import Path


PROJECT_ROOT = Path("src/coding_agent").resolve()


def get_safe_path(filename: str) -> Path:
    path = (PROJECT_ROOT / filename).resolve()

    if not path.is_relative_to(PROJECT_ROOT):
        raise ValueError("File is outside the project root.")

    return path

def search_all_files() -> str:
    """
    Return a list of files in the project.

    Hidden directories and dependency/cache directories are excluded.
    """

    excluded_dirs = {
        ".venv",
        ".git",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
    }

    files = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(PROJECT_ROOT)

        if any(
            part in excluded_dirs or part.startswith(".")
            for part in relative_path.parts
        ):
            continue

        files.append(str(relative_path))

    return "\n".join(sorted(files))


def read_file(filename: str) -> str:
    path = get_safe_path(filename)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {filename}")

    return path.read_text()



def edit_file(
    filename: str,
    anchor: str,
    new_text: str,
    position: str,
) -> str:
    path = get_safe_path(filename)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {filename}")

    if not anchor:
        raise ValueError("anchor cannot be empty.")

    if position not in {"before", "after", "replace"}:
        raise ValueError(
            "position must be 'before', 'after', or 'replace'."
        )

    content = path.read_text()

    matches = content.count(anchor)

    if matches == 0:
        raise ValueError(
            "The anchor text was not found in the file."
        )

    if matches > 1:
        raise ValueError(
            f"The anchor text was found {matches} times. "
            "The anchor must be unique."
        )

    if position == "before":
        replacement = new_text + anchor

    elif position == "after":
        replacement = anchor + new_text

    else:
        replacement = new_text

    content = content.replace(anchor, replacement, 1)

    path.write_text(content)

    return f"Successfully edited {filename}"