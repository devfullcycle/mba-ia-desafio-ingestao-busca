import argparse

from config import load_get_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PDF ingestion and semantic search.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    ingest = subparsers.add_parser('ingest', help='Ingest a PDF into pgvector.')
    ingest.add_argument('pdf_name', help='The name of the PDF file.')

    subparsers.add_parser('chat', help='Start the interactive chat.')

    return parser.parse_args()


def main():
    load_get_config()

    args = parse_args()
    if args.command == 'ingest':
        pass
    elif args.command == 'chat':
        pass


if __name__ == '__main__':
    main()
