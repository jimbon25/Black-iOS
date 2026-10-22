import io
import os
import sys
import urllib.request
import zipfile

def main():
    dest_path = os.path.join("assets", "default.xbe")
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000000:
        print(f"{dest_path} already exists ({os.path.getsize(dest_path)} bytes).")
        return 0

    os.makedirs("assets", exist_ok=True)
    archive_url = "https://archive.org/download/HDDReadyXboxGames/Black.zip"
    print(f"Resolving {archive_url}...")

    req_head = urllib.request.Request(archive_url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req_head, timeout=20) as resp:
            total_size = int(resp.headers["Content-Length"])
            final_url = resp.geturl()
    except Exception as e:
        print(f"Error resolving HEAD for archive: {e}")
        return 1

    print(f"Archive size: {total_size} bytes. Downloading central directory via HTTP range...")

    class RangeReader(io.RawIOBase):
        def __init__(self, url, size):
            self.url = url
            self.size = size
            self.pos = 0

        def readable(self):
            return True

        def seekable(self):
            return True

        def seek(self, offset, whence=0):
            if whence == 0:
                self.pos = offset
            elif whence == 1:
                self.pos += offset
            elif whence == 2:
                self.pos = self.size + offset
            return self.pos

        def tell(self):
            return self.pos

        def readinto(self, b):
            req_len = len(b)
            if self.pos >= self.size:
                return 0
            end = min(self.pos + req_len - 1, self.size - 1)
            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={self.pos}-{end}"},
            )
            data = urllib.request.urlopen(req, timeout=30).read()
            b[:len(data)] = data
            self.pos += len(data)
            return len(data)

    try:
        reader = io.BufferedReader(RangeReader(final_url, total_size))
        with zipfile.ZipFile(reader) as zf:
            print("Locating Black/default.xbe in zip index...")
            xbe_data = zf.read("Black/default.xbe")
            with open(dest_path, "wb") as f:
                f.write(xbe_data)
            print(f"Successfully extracted {dest_path} ({len(xbe_data)} bytes).")
            return 0
    except Exception as e:
        print(f"Error extracting XBE via range requests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
