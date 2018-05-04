# Audicor Reader
Python script for reading EKG or heart-sounds files from Audicor.

## Dependency
* python3
  * [numpy](http://www.numpy.org/)
  * [matplotlib](https://matplotlib.org/)
  * [tqdm](https://github.com/tqdm/tqdm)

Install dependency by [pip3](https://pypi.org/project/pip/):
```
pip3 install --user -r requirements.txt
```

## Usage
### Script
```
$ python3 reader.py -h                                    
usage: reader.py [-h] [-o OUTPUT_FILENAME] [-sx SIZE_X] [-sy SIZE_Y] filename

Produce ekg and heart_sound figure.

positional arguments:
  filename              Filename to read. Must be *.bin or *.raw (case-
                        insensitive).

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILENAME, --output OUTPUT_FILENAME
                        Filename of saved figure. (default: output.png)
  -sx SIZE_X, --size-x SIZE_X
                        X-axis size of saved figure. (default: 20)
  -sy SIZE_Y, --size-y SIZE_Y
                        Y-axis size of saved figure. (default: 20)
```
#### Example
* EKG
  * `python3 reader.py some_ekg.bin -o ekg.png`
* Heart sounds
  * `python3 reader.py some_heart_sounds.raw -o heart_sounds.png`

### Module
```python3
from reader import get_ekg, get_heart_sounds

if __name__ == '__main__':
    ekg_filename = '/somewhere/to/ekg/file.bin'
    heart_sounds_filename = '/somewhere/to/heart_sounds/file.raw'

    ekg_data = get_ekg(ekg_filename)
    heart_sounds_data = get_heart_sounds(heart_sounds_filename)
```
