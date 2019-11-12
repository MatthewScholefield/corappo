import sys

import re
from argparse import ArgumentParser
from os.path import splitext

from corappo.cmake_target import CMakeTarget
from corappo.formatting import format_multiline


def parse_compiler_args(args):
    parser = ArgumentParser()
    parser.add_argument('-o', dest='output')
    parser.add_argument('-g', dest='debug', action='store_true')
    parser.add_argument('-c', dest='compile_only', action='store_true')
    parser.add_argument('-O', dest='optimize', type=int)
    parser.add_argument('-std', dest='standard')
    parser.add_argument('-W', dest='warn')
    parser.add_argument('-l', dest='libs', action='append')
    parser.add_argument('-I', '-isystem', '-iquote', '-idirafter', '-L', dest='include_dirs', action='append')
    parser.add_argument('-pthread', action='store_true')
    args, remaining = parser.parse_known_args(args)
    args.libs = args.libs or []
    args.libs.extend(['${CMAKE_CURRENT_LIST_DIR}/' + i for i in remaining if i.endswith('.a')])
    args.flags = [i for i in remaining if i.startswith('-')]
    args.inputs = [i for i in remaining if re.match(r'.+\.[^.]+', i) and not i.endswith('.a')]
    return args


class CMakeProject:
    def __init__(self, name=''):
        self._name = name
        self.deps = {}
        self.targets = []
        self.standards = set()
        self.include_dirs = set()
        self.other_flags = []
        self.pthread = False

    @property
    def name(self):
        if self._name:
            return self._name
        return next(iter(i.name for i in self.targets), 'project_name')

    def get_sources(self, target):
        if target not in self.deps:
            return [target]
        return sum([self.get_sources(i) for i in self.deps[target]], [])

    def ingest(self, line):
        if 'g++' in line:
            line = line.split('g++')[-1].strip()
        elif 'clang++' in line:
            line = line.split('clang++')[-1].strip()
        else:
            return
        args = parse_compiler_args(line.split(' '))
        for flag in args.flags:
            if flag not in self.other_flags:
                self.other_flags.append(flag)
        self.include_dirs.update(args.include_dirs or [])
        if args.standard:
            self.standards.add(args.standard)
        if args.compile_only:
            if args.output:
                assert len(args.inputs) == 1
                self.deps[args.output] = [args.inputs[0]]
            else:
                for filename in args.inputs:
                    self.deps[splitext(filename)[0] + '.o'] = [filename]
        else:
            exe = args.output or 'a.out'
            self.deps[exe] = args.inputs
            target = CMakeTarget(exe, self.get_sources(exe), args.libs)
            if args.pthread:
                target.libs.append('${CMAKE_THREAD_LIBS_INIT}')
                self.pthread = True
            self.targets.append(target)

    def __str__(self):
        parts = [
            'cmake_minimum_required(VERSION 2.8)',
            'project({})'.format(self.name)
        ]
        if self.standards:
            if len(self.standards) > 1:
                print('Warning: multiple c++ standards', file=sys.stderr)
            standard = max(self.standards)
            m = re.search(r'[0-9]{2}', standard)
            if m:
                parts.append('set(CMAKE_CXX_STANDARD {})'.format(m.group(0)))
            else:
                self.other_flags.append('-std=' + standard)
        if self.other_flags:
            parts.append('set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {}")'.format(' '.join(self.other_flags)))
        if self.pthread:
            parts.append('find_package(Threads)')
        if self.include_dirs:
            parts.append('include_directories({})'.format(format_multiline(sorted(self.include_dirs))))
        for target in self.targets:
            parts.append(str(target))
        return '\n\n'.join(parts)
