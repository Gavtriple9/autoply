import argparse


def get_parser():
    """
    Get the parser for the autoply command line interface.

    :return: The parser for the autoply command line interface.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    # subparsers = parser.add_subparsers(required=False, dest="prog")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable verbose mode",
        default=False,
    )
    parser.add_argument(
        "-l", "--log_level", type=str, help="set log level", default="INFO"
    )

    return parser
