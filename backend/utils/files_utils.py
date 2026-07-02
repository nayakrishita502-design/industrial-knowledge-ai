import os

ALLOWED_EXTENSIONS = {
    "pdf",
    "txt",
    "csv",
    "xlsx",
    "docx"
}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_file_size(filepath):
    size = os.path.getsize(filepath)

    if size < 1024:
        return f"{size} Bytes"

    elif size < 1024 * 1024:
        return f"{round(size / 1024,2)} KB"

    return f"{round(size / (1024*1024),2)} MB"