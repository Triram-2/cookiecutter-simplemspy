import psutil

def close_chrome():
    chrome_process_names = ['chrome', 'chrome.exe', 'chromium', 'chromium-browser']
    thunderbird_name = "thunderbird"
    closed_count = 0

    for process in psutil.process_iter(['name']):
        try:
           name = process.info['name']
           if name and ('chrom' in name.lower() or 'nacl' in name.lower() or 'sandbox' in name.lower() or 'crashpad' in name.lower()):
                process.terminate()
                process.wait(timeout=3)
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"Ошибка при завершении {process.info['name']}: {e}")

    print(f"Закрыто процессов Chrome: {closed_count}")

if __name__ == "__main__":
    close_chrome()
