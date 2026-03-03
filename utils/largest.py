#!/data/data/com.termux/files/usr/bin/python3
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET = "/data/data/com.termux"
TOP_N = 10
CANDIDATE_POOL = 50   # fetch top 50 largest files first
HASH_CHUNK = 1024*100  # first 100KB + last 100KB

def human_readable(size):
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"

def partial_hash(path):
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            start = f.read(HASH_CHUNK)
            if size > HASH_CHUNK:
                f.seek(-HASH_CHUNK, os.SEEK_END)
                end = f.read(HASH_CHUNK)
            else:
                end = b""
        h = hashlib.sha256()
        h.update(start + end)
        return h.hexdigest(), size
    except Exception:
        return None, None

def full_hash(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

# 1. Find all files and their sizes
all_files = []
for root, dirs, filenames in os.walk(TARGET):
    for name in filenames:
        path = os.path.join(root, name)
        try:
            size = os.path.getsize(path)
            all_files.append((size, path))
        except Exception:
            continue

# 2. Get top 50 largest candidates
top_candidates = sorted(all_files, key=lambda x: x[0], reverse=True)[:CANDIDATE_POOL]

# 3. Partial hash in parallel
partial_hashes = {}
with ThreadPoolExecutor() as executor:
    futures = {executor.submit(partial_hash, path): path for _, path in top_candidates}
    for future in as_completed(futures):
        path = futures[future]
        h, size = future.result()
        if h:
            if h not in partial_hashes:
                partial_hashes[h] = (size, path)
            else:
                # If hash matches, keep first entry for speed
                existing = partial_hashes[h]
                partial_hashes[h] = existing  # keep first for speed

# 4. Get top 10 by size
final_top = sorted(partial_hashes.values(), key=lambda x: x[0], reverse=True)[:TOP_N]

# 5. Print results
for size, path in final_top:
    print(f"{human_readable(size):>8}\t{path}")

