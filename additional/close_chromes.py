import psutil
from typing import List, Iterator


def close_processes(process_names: List[str]) -> None:
    """
    Terminates processes that match any of the names in the process_names list
    or contain specific keywords related to browsers.
    """
    closed_count: int = 0
    # Fetch 'name' and 'pid' for each process. 'pid' is useful for logging.
    # psutil.process_iter returns an Iterator[psutil.Process]
    process_iterator: Iterator[psutil.Process] = psutil.process_iter(
        attrs=["name", "pid"]
    )

    for process in process_iterator:
        try:
            proc_name: str = process.info.get("name", "") 
            proc_pid: int = process.info.get("pid", 0)

            if not proc_name: # Skip if name could not be retrieved
                continue

            # Check if the process name exactly matches any in the list
            # or contains browser-related keywords.
            should_terminate = False
            for p_name in process_names:
                if p_name.lower() == proc_name.lower():
                    should_terminate = True
                    break
            
            if not should_terminate:
                # Broader check for browser-related processes
                browser_keywords = ["chrom", "nacl", "sandbox", "crashpad", "firefox", "edge", "opera", "safari", "msedge"]
                for keyword in browser_keywords:
                    if keyword in proc_name.lower():
                        should_terminate = True
                        break
            
            if should_terminate:
                print(f"Попытка завершения процесса: {proc_name} (PID: {proc_pid})")
                process.terminate()
                process.wait(timeout=3)  # Wait for the process to terminate
                closed_count += 1
                print(f"Процесс {proc_name} (PID: {proc_pid}) успешно завершен.")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            # process.info might be None if the process terminated unexpectedly
            pid_for_log = proc_pid if 'proc_pid' in locals() else process.pid
            name_for_log = proc_name if 'proc_name' in locals() and proc_name else "Неизвестное имя"
            print(f"Ошибка при завершении процесса (PID: {pid_for_log}, Имя: {name_for_log}): {e}")
        except Exception as e: # Catch any other unexpected errors
            pid_for_log = proc_pid if 'proc_pid' in locals() else process.pid
            name_for_log = proc_name if 'proc_name' in locals() and proc_name else "Неизвестное имя"
            print(f"Неожиданная ошибка при обработке процесса (PID: {pid_for_log}, Имя: {name_for_log}): {e}")


    print(f"Всего завершено процессов: {closed_count}")


def main() -> None:
    """
    Main function to define target process names and initiate closing.
    """
    # Define specific process names to target for closing.
    # This list can be expanded or modified as needed.
    chrome_process_names: List[str] = [
        "chrome",
        "chrome.exe",
        "chromium",
        "chromium-browser",
        # Add other browser main executable names if needed, e.g., "firefox.exe", "msedge.exe"
    ]
    # The close_processes function also checks for keywords like "chrom", "firefox", etc.
    # so this list is for specific main process names.
    
    print("Запуск скрипта для закрытия процессов браузеров...")
    close_processes(chrome_process_names)
    print("Скрипт завершил работу.")


if __name__ == "__main__":
    main()
