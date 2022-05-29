"""
From https://github.com/shmulya/webmtogif/blob/dev/app/modules/converter.py
"""
import os.path
import subprocess
import requests

from typing import Optional, IO, Union
from pathlib import Path
from os import getcwd, remove


class ConverterError(Exception):
    pass


class Converter:
    workdir: Path
    log: IO

    def __init__(self,
                 workdir: Optional[Union[str, Path]] = None,
                 log_file: Optional[Union[str, Path]] = None):
        self.workdir = Path(workdir or getcwd())
        self.log = open(log_file or 'ffmpeg_error.log', 'a')

    def fetch(self, url: str, name: Optional[str] = None) -> str:
        """
        Download source video from _url_
        :param name: filename
        :param url: source video url
        :return: status dict
        """
        filename = os.path.split(url)[-1]
        ext = os.path.splitext(filename)[-1]
        if ext not in ['.webm']:
            raise ConverterError('wrong extension')

        try:
            req = requests.get(url)
            if 200 <= req.status_code < 400:
                source = req.content
            else:
                raise ConverterError(f'request code {req.status_code}')
        except Exception as e:
            raise e

        if name is not None:
            filename = str(name)

        filepath = self.workdir / 'files' / filename
        if not filepath.parent.exists():
            os.makedirs(filepath.parent)
        file = open(filepath, 'wb')
        file.write(source)
        file.close()
        return filepath

    def to_gif(self, filepath: str) -> str:
        """
        Convert source file to GIF
        :param filepath: source file path
        :return:
        """
        filename_gif = str(filepath) + '.gif'
        command = f"/usr/bin/ffmpeg -i {filepath} -y " \
                  "-filter_complex " \
                  "'fps=10,scale=320:-1:flags=lanczos,split [o1] [o2];[o1] " \
                  f"palettegen [p]; [o2] fifo [o3];[o3] [p] paletteuse' {filename_gif}"
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL,
                           stderr=self.log)
        except Exception as e:
            raise e
        return filename_gif

    def to_mp4(self, filepath: str) -> str:
        """
        Convert source file to MP4
        :param filepath: source file path
        :return: path
        """
        filename_mp4 = str(filepath) + '.mp4'
        command = f"/usr/bin/ffmpeg -i {filepath} -y -pix_fmt yuv420p -vcodec libx264 -profile:v main " \
                  f"-crf 25 -strict -2 -movflags faststart {filename_mp4}"
        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL,
                           stderr=self.log)
        except Exception as e:
            raise e
        return filename_mp4

    def delete(self, path: Union[str, Path]) -> None:
        """
        Delete file path
        :param path: file path
        :return: None
        """
        remove(path)


def test_convert_to_mp4():
    link = 'https://cs14.pikabu.ru/video/2022/05/26/1653597715219655492_480x460.webm'
    c = Converter(
        workdir='/tmp/',
        log_file='/tmp/ffmpeg_error.log'
    )
    filepath = Path(c.fetch(link))
    assert filepath.exists()
    assert filepath.is_absolute()
    mp4_filepath = Path(c.to_mp4(filepath))
    assert mp4_filepath.exists()
    assert mp4_filepath.is_absolute()
