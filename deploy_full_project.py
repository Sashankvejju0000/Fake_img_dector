from pathlib import Path
import shutil
import subprocess
import os
import stat
import time

root = Path(__file__).resolve().parent
src = root
dst = root.parent / f'Fake_img_dect_full_push_{int(time.time())}'

print('Source:', src)
print('Destination:', dst)

if dst.exists():
    print('Removing existing destination', dst)

    def on_rm_error(func, path, exc_info):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print('Error removing', path, type(e).__name__, e)
            raise

    shutil.rmtree(dst, onerror=on_rm_error)

print('Cloning repo into destination')
subprocess.run(['git', 'clone', 'https://github.com/Sashankvejju0000/Fake_img_dector.git', str(dst)], check=True)

for item in src.iterdir():
    if item.name == '.git':
        continue
    dest = dst / item.name
    if item.is_dir():
        print('Copying directory', item.name)
        shutil.copytree(item, dest, dirs_exist_ok=True)
    else:
        print('Copying file', item.name)
        shutil.copy2(item, dest)

print('Finished copying files')

print('Running git status in destination')
subprocess.run(['git', '-C', str(dst), 'status', '--short'], check=True)
subprocess.run(['git', '-C', str(dst), 'add', '-A'], check=True)
result = subprocess.run(['git', '-C', str(dst), 'diff', '--cached', '--quiet'])
if result.returncode != 0:
    print('Changes detected, committing')
    subprocess.run(['git', '-C', str(dst), 'commit', '-m', 'Deploy full project from workspace'], check=True)
else:
    print('No changes to commit')

print('Pushing to GitHub')
subprocess.run(['git', '-C', str(dst), 'push', '-u', 'origin', 'main'], check=True)
print('Push complete')
