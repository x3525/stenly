"""LSB-based image steganography tool."""

import io
import itertools
import math
import random
import signal
import sys
import warnings

import numpy as np
from PIL import Image
from PIL.Image import DecompressionBombError, DecompressionBombWarning

from stenly.cli import parser
from stenly.consts import B, MIN_PIXELS, RGB, SUFFIX


def start() -> None:
    """Start the program."""
    signal.signal(signal.SIGINT, stop)

    opts, _ = parser.parse_known_args()

    try:
        with Image.open(opts.file) as image:
            if image.mode not in (
                    'RGB',
                    'RGBA',
            ):
                raise SystemExit('invalid image mode', image.mode)

            px = math.prod(size := image.size)

            if px < MIN_PIXELS:
                raise SystemExit('need more pixels', MIN_PIXELS - px)

            imgdata = np.array(image.getdata())
    except (
            OSError, DecompressionBombError, DecompressionBombWarning
    ) as err:
        raise SystemExit(repr(err)) from err

    pixels = list(range(px))

    if seed := opts.seed:
        random.seed(seed)
        random.shuffle(pixels)

    # Create a stego-object
    if opts.msg:
        limit = ((px * sum(opts.lsb.values())) // B) - len(SUFFIX)

        overflow = len(opts.msg) - limit

        if overflow > 0:
            raise SystemExit('character overflow', overflow)

        if SUFFIX in opts.msg:
            raise SystemExit('message contains the suffix', SUFFIX)

        msg = opts.msg + SUFFIX

        # Character -> Bit
        bits = ''.join(format(ord(char), f'0{B}b') for char in msg)

        i = 0

        for p, (c, b) in itertools.product(pixels, tuple(opts.lsb.items())):
            if i >= len(bits):
                break

            val = format(imgdata[p][c], f'0{B}b')

            pack = val[:B - b] + (_ := bits[i:i + b]) + val[B - b + len(_):]

            # Bit -> File
            imgdata[p][c] = int(pack, 2)

            i += b

        array = imgdata.reshape(*size[::-1], imgdata.shape[1]).astype(np.uint8)

        with io.BytesIO() as stream:
            Image.fromarray(array).save(stream, opts.file.suffix.lstrip('.'))

            stream.seek(0)

            sys.stdout.buffer.write(stream.read())
            sys.stdout.buffer.flush()
    # Extract an embedded message from a stego-object
    else:
        if not opts.brute:
            possibilities = [tuple(opts.lsb.items())]
        else:
            cartesian = itertools.product(range(B + 1), repeat=RGB)

            possibilities = [
                tuple(itertools.compress(enumerate(t), t)) for t in cartesian
            ]

        for bb in possibilities:
            bits, msg = '', ''

            for p, (c, b) in itertools.product(pixels, bb):
                if msg.endswith(SUFFIX):  # No need to go any further
                    break

                # File -> Bit
                bits += format(imgdata[p][c], f'0{B}b')[-b:]

                if len(bits) >= B:
                    # Bit -> Character
                    character = chr(int(bits[:B], 2))

                    if not character.isascii():
                        break

                    msg += character

                    bits = bits[B:]

            if msg.endswith(SUFFIX):
                break
        else:
            raise SystemExit('no embedded message found')

        msg = msg.removesuffix(SUFFIX)

        sys.stdout.write(msg)
        sys.stdout.flush()


def stop(*args):
    """Stop the program."""
    sys.exit(-1)


def main() -> None:
    """Entry point."""
    warnings.simplefilter('error', DecompressionBombWarning)

    start()


if __name__ == '__main__':
    main()
