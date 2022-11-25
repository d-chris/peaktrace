from urllib.request import urlretrieve
from pathlib import Path
import hashlib
import re

links = [
    (
        'PEAK_LIN_LTRC_File_Format.pdf',
        'https://www.peak-system.com/produktcd/Pdf/English/PEAK_LIN_LTRC_File_Format.pdf'
    ),
    (
        'PEAK_CAN_TRC_File_Format.pdf',
        'https://www.peak-system.com/quick/DOC-TRC-CAN'
    )
]


def parse_hashfile(filename: str) -> dict:
    ''' read hash-file into a dict '''
    with open(filename, mode='rt', encoding='utf-8') as f:
        content = f.read()

    hashes = dict()
    for match in re.finditer(r"(?P<hash>[0-9a-z]{8,}) \*(?P<file>.*?)$", content, re.MULTILINE | re.IGNORECASE):
        hashes[match.group('file')] = match.group('hash')

    return hashes


if __name__ == '__main__':

    try:
        hashes = parse_hashfile(Path(__file__).with_suffix('.md5'))
    except FileNotFoundError as e:
        raise FileNotFoundError(f'Aborted script, hashfile does not exist')


    for file, url in links:
        if Path(file).is_file() == False:
            f, http = urlretrieve(url, file)

            print(f"'{file}' has type '{http.get_content_type()}'")

        if hashes[file] != hashlib.md5(Path(file).read_bytes()).hexdigest():
            print(f"==> '{file}' has the wrong hash, be carefull")
