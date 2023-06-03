import os
import threading
import requests
import tarfile
import zipfile
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

def download_file(url, local_filename, queue):
    # Stream download to handle big files
    r = requests.get(url, stream=True)
    r.raise_for_status()

    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024 # 1 KByte

    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(local_filename, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    
    # Put file into the queue for extraction
    queue.put(local_filename)

def extract_file(queue, path_to_extract):
    while True:
        filename = queue.get()
        if filename is None:
            break
        if filename.endswith('.tar.gz'):
            with tarfile.open(filename, 'r:gz') as tar:
                for member in tar.getmembers():
                    tar.extract(member, path=path_to_extract)
                    print(f'Extracted: {member.name}')
        elif filename.endswith('.whl') or filename.endswith('.zip'):
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    zip_ref.extract(member, path=path_to_extract)
                    print(f'Extracted: {member}')
        # Delete the file after extraction
        os.remove(filename)
        print(f'Deleted: {filename}')
        queue.task_done()

def delete_dist_info_dirs(path):
    for dirpath, dirnames, _ in os.walk(path):
        for dirname in dirnames:
            if dirname.endswith('dist-info'):
                shutil.rmtree(os.path.join(dirpath, dirname))
                print(f'Deleted directory: {dirname}')

# Take package name as input
package_name = input("Enter the package name: ")

# Get package information from PyPi
response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
data = response.json()

# Ensure the directory for the downloads exists
package_dir = os.path.join('downloads', package_name)
os.makedirs(package_dir, exist_ok=True)

# Prepare list for download tasks
download_tasks = []

# Prepare each download task
for version, files in data['releases'].items():
    for file_info in files:
        # Only handle .whl or .tar.gz files
        if file_info['packagetype'] in ['bdist_wheel', 'sdist']:
            url = file_info['url']
            filename = os.path.join(package_dir, url.split('/')[-1])
            download_tasks.append((url, filename))

queue = Queue()

# Start a thread for extraction
extractor_thread = threading.Thread(target=extract_file, args=(queue, package_dir))
extractor_thread.start()

# Run download tasks in a thread pool
with ThreadPoolExecutor(max_workers=5) as executor:
    for url, filename in download_tasks:
        executor.submit(download_file, url, filename, queue)

# Block until all tasks are done
queue.join()

# Stop the extractor thread
queue.put(None)
extractor_thread.join()

# Delete dist-info directories
delete_dist_info_dirs(package_dir)