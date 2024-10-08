import httpx
import argparse
import tqdm
import os
import zipfile
import shutil

APPDATA = os.getenv("APPDATA")
def install_chromium():
    dir = os.path.join(APPDATA, "navium_build")
    dir_file = os.path.join(APPDATA, "navium_build", "build.zip")
    extraction_path = os.path.join(dir, "build")

    if not os.path.exists(dir):
        os.mkdir(dir)
    else:
        return print("The build is already installed in <{}> skipping the process.".format(dir))

    with httpx.Client() as client:
        print("Installing Chromium...")
        with client.stream("GET", "https://commondatastorage.googleapis.com/chromium-browser-snapshots/Win_x64/1364698/chrome-win.zip") as response:
            if response.status_code == 200:
                total_size = int(response.headers.get("content-length", 0))

                with open(dir_file, "wb") as f, tqdm.tqdm(
                    desc="Downloading Chromium",
                    total=total_size,
                    unit="iB",
                    unit_scale=True,
                    unit_divisor=1024
                ) as bar:
                    for chunk in response.iter_bytes(chunk_size=1024):
                        f.write(chunk)
                        bar.update(len(chunk))

                with zipfile.ZipFile(dir_file) as z:
                    z.extractall(os.path.join(dir, "build"))

                os.remove(dir_file)
                chrome_win_dir = os.path.join(extraction_path, "chrome-win")
                for file_name in os.listdir(chrome_win_dir):
                    source_file = os.path.join(chrome_win_dir, file_name)
                    destination_file = os.path.join(extraction_path, file_name)
                    shutil.move(source_file, destination_file)

                shutil.rmtree(chrome_win_dir)

                print("Chromium has been downloaded successfully :3")
            else:
                print("Failed to download chromium: {} ({})".format(response.text, response.status_code))

def main():
    parser = argparse.ArgumentParser(description="Navium CLI")
    subparser = parser.add_subparsers(dest="command")

    install_parser = subparser.add_parser('install', help="Installs the necessary files required to run navium.")
    args = parser.parse_args()

    if args.command == "install":
        install_chromium()

if __name__ == "__main__":
    main()