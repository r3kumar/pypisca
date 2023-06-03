import os
import requests

def download_file(url, local_filename):
    # Stream download to handle big files
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

# Take package name as input
package_name = input("Enter the package name: ")

# Get package information from PyPi
response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
data = response.json()

# Ensure the directory for the downloads exists
os.makedirs('downloads', exist_ok=True)

# Download each file
for version, files in data['releases'].items():
    for file_info in files:
        # Only download .whl or .tar.gz files
        if file_info['packagetype'] in ['bdist_wheel', 'sdist']:
            url = file_info['url']
            filename = os.path.join('downloads', url.split('/')[-1])
            print(f'Downloading {url} to {filename}')
            download_file(url, filename)