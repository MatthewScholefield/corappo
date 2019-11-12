import sys

from argparse import ArgumentParser

from corappo.cmake_project import CMakeProject


def main():
    parser = ArgumentParser(description='A tool to automatically generate CMake projects')
    parser.add_argument('build_output', nargs='?', help='Terminal output from running make. Otherwise read from stdin.')
    parser.add_argument('-n', '--name', help='Project name')
    args = parser.parse_args()
    if not args.build_output and sys.stdin.isatty():
        parser.error('Please specify a build output file or pipe via stdin')

    proj = CMakeProject()
    if args.build_output:
        with open(args.build_output) as f:
            for line in f:
                proj.ingest(line)
    else:
        for line in sys.stdin:
            proj.ingest(line)

    print(str(proj))


if __name__ == '__main__':
    main()
