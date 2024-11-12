"""Command-line interface."""

import argparse

import stenly
from stenly.actions import ValidateFile, ValidateLSB, ValidateMessage
from stenly.consts import B, RGB

parser = argparse.ArgumentParser(
    prog='stenly',
    description='%(prog)s - lsb-based image steganography tool',
    epilog='examples:'
           '\n\t%(prog)s cover.png -l 0 1 2 -m secret > stego.png'
           '\n\t%(prog)s stego.png -l 0 1 2',
    formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument('file', action=ValidateFile, help='a cover/stego object')

parser.add_argument(
    '-b',
    action='store_true',
    help='use brute force technique to extract',
    dest='brute',
)
parser.add_argument(
    '-l',
    action=ValidateLSB,
    nargs=RGB,
    type=int,
    choices=range(B + 1),
    required=True,
    help='least significant bits for each color channel (from: %(choices)s)',
    metavar=('R', 'G', 'B'),
    dest='lsb',
)
parser.add_argument(
    '-m',
    action=ValidateMessage,
    help='use %(metavar)s for embedding',
    metavar='MESSAGE',
    dest='msg',
)
parser.add_argument(
    '-s',
    help='use %(metavar)s as pseudo-random number generator seed',
    metavar='SEED',
    dest='seed',
)
parser.add_argument(
    '-V',
    action='version',
    help='show program version and exit',
    version=stenly.VERSION,
)
