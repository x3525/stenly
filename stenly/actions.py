"""Custom argument actions."""

import argparse
import pathlib


class ValidateFile(argparse.Action):
    """File validator."""

    def __call__(self, parser, ns, values, option_string=None) -> None:
        f = pathlib.Path(values).resolve()

        if not f.suffix.lower().endswith(
                (
                        '.bmp',
                        '.png',
                )
        ):
            raise argparse.ArgumentError(self, 'invalid extension')

        setattr(ns, self.dest, f)


class ValidateLSB(argparse.Action):
    """LSB validator."""

    def __call__(self, parser, ns, values, option_string=None) -> None:
        if sum(values) == 0:
            raise argparse.ArgumentError(self, 'no lsb')

        setattr(
            ns, self.dest, {c: b for c, b in enumerate(values) if b != 0}
        )


class ValidateMessage(argparse.Action):
    """Message validator."""

    def __call__(self, parser, ns, values, option_string=None) -> None:
        for v in values:
            if not v.isascii():
                break
        else:
            setattr(ns, self.dest, values)
            return

        raise argparse.ArgumentError(self, 'not ascii compatible')
