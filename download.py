import os
import requests
import tarfile
import zipfile
from tqdm import tqdm

def download_file(url, local_filename):
    # Stream download to handle big files
    r = requests.get(url, stream=True)
    r.raise_for_status()

    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024 # 1 KByte

    t=tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(local_filename, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    return local_filename

def extract_file(filename, path_to_extract):
    if filename.endswith('.tar.gz'):
        with tarfile.open(filename, 'r:gz') as tar:
            for member in tar.getmembers():
                tar.extract(member, path=path_to_extract)
                print(f'Extracted: {member.name}')
    elif filename.endswith('.whl') or filename.endswith('.zip'):
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            for member in zip_ref.namelist():
                zip_ref.extract(member, path_to_extract)
                print(f'Extracted: {member}')

# Take package name as input
package_name = input("Enter the package name: ")

# Get package information from PyPi
response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
data = response.json()

# Ensure the directory for the downloads exists
package_dir = os.path.join('downloads', package_name)
os.makedirs(package_dir, exist_ok=True)

# Download each file
for version, files in data['releases'].items():
    for file_info in files:
        # Only download .whl or .tar.gz files
        if file_info['packagetype'] in ['bdist_wheel', 'sdist']:
            url = file_info['url']
            filename = os.path.join(package_dir, url.split('/')[-1])
            print(f'Downloading {url} to {filename}')
            download_file(url, filename)
            extract_path = os.path.join(package_dir, filename.split('/')[-1].split('.')[0])
            os.makedirs(extract_path, exist_ok=True)
            print(f'Extracting {filename} to {extract_path}')
            extract_file(filename, extract_path)