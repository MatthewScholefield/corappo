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
    parser.add_argument('-D', dest='defines', action='append')
    parser.add_argument('-std', dest='standard')
    parser.add_argument('-W', dest='warn')
    parser.add_argument('-l', dest='libs', action='append')
    parser.add_argument('-I', '-isystem', '-iquote', '-idirafter', '-L', dest='include_dirs', action='append')
    parser.add_argument('-pthread', action='store_true')
    args, remaining = parser.parse_known_args(args)
    args.libs = args.libs or []
    args.libs.extend(['${CMAKE_CURRENT_LIST_DIR}/' + i for i in remaining if i.endswith('.a')])
    args.flags = [i for i in remaining if i.startswith('-')]
    args.inputs = [i for i in remaining if re.match(r'.+\.[^.]+', i) and not i.endswith('.a') and not i.startswith('-')]
    return args


class CMakeProject:
    def __init__(self, name=''):
        self._name = name
        self.deps = {}
        self.defines = {}
        self.targets = {}
        self.standards = set()
        self.include_dirs = set()
        self.other_flags = []
        self.pthread = False

    @property
    def name(self):
        if self._name:
            return self._name
        return next(iter(self.targets), 'project_name')

    def get_leaves(self, target, source):
        if not isinstance(target, str) or target not in source:
            return [target]
        return sum([self.get_leaves(i, source) for i in source[target]], [])

    def ingest(self, line):
        for tool in ['g++', 'gcc', 'clang++', 'clang']:
            if tool in line:
                line = line.split(tool)[-1].strip()
                break
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
                assert len(args.inputs) == 1, 'Too many inputs: ' + str(args.inputs)
                self.deps[args.output] = [args.inputs[0]]
                self.defines[args.output] = [args.defines or []]
            else:
                for filename in args.inputs:
                    obj = splitext(filename)[0] + '.o'
                    self.deps[obj] = [filename]
                    self.defines[obj] = [args.defines or []]
        else:
            exe = args.output or 'a.out'
            self.deps[exe] = args.inputs
            parts = [args.defines or []]
            for f in args.inputs:
                if f in self.defines:
                    parts += [f]
            self.defines[exe] = parts
            sources = self.get_leaves(exe, self.deps)
            defines = sum(self.get_leaves(exe, self.defines), [])
            target = CMakeTarget(exe, sources, defines, args.libs)
            if args.pthread:
                target.libs.append('${CMAKE_THREAD_LIBS_INIT}')
                self.pthread = True
            self.targets[target.name] = target

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
        for target in self.targets.values():
            parts.append(str(target))
        return '\n\n'.join(parts)
