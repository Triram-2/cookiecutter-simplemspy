import os
import pathlib
import sys

PROJECT_DIRECTORY = pathlib.Path.cwd()

def main():
    db_type = "{{ cookiecutter.db_type }}"
    sqlite_db_path_str = "{{ cookiecutter.sqlite_db_path }}"

    if db_type == "SQLITE":
        if not sqlite_db_path_str:
            print("ERROR: sqlite_db_path is not set but db_type is SQLITE.")
            sys.exit(1)

        # project_slug is the name of the directory cookiecutter creates for the project
        project_slug = "{{ cookiecutter.project_slug }}"

        # The script runs from within the root of the new project directory
        # So, PROJECT_DIRECTORY is already {{cookiecutter.project_slug}}
        # Therefore, we can resolve sqlite_db_path_str directly
        sqlite_file_path = pathlib.Path(sqlite_db_path_str)

        try:
            # Create parent directories
            sqlite_file_path.parent.mkdir(parents=True, exist_ok=True)
            # Create the file
            sqlite_file_path.touch(exist_ok=True) # exist_ok=True in case it was somehow created
            print(f"SUCCESS: Ensured SQLite file and directories exist at {sqlite_file_path}")
        except Exception as e:
            print(f"ERROR: Could not create SQLite file or directories: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
