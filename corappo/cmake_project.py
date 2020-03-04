import sys

import re
from argparse import ArgumentParser
from os.path import splitext

from corappo.cmake_target import CMakeTarget
from corappo.formatting import format_multiline


def parse_compiler_args(args):
    parser = ArgumentParser()
    parser.add_argument('-o', dest='output')
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
        self.flags = {}
        self.targets = {}
        self.cxxstandards = set()
        self.cstandards = set()
        self.include_dirs = set()
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
        if tool in ['gcc', 'clang']:
            standards = self.cstandards
        else:
            standards = self.cxxstandards
        self.include_dirs.update(args.include_dirs or [])
        if args.standard:
            standards.add(args.standard)
        if args.compile_only:
            if args.output:
                assert len(args.inputs) == 1, 'Too many inputs: ' + str(args.inputs)
                self.deps[args.output] = [args.inputs[0]]
                self.defines[args.output] = [args.defines or []]
                self.flags[args.output] = [args.flags or []]
            else:
                for filename in args.inputs:
                    obj = splitext(filename)[0] + '.o'
                    self.deps[obj] = [filename]
                    self.defines[obj] = [args.defines or []]
                    self.flags[obj] = [args.flags or []]
        else:
            exe = args.output or 'a.out'
            self.deps[exe] = args.inputs
            parts = [args.defines or []]
            for f in args.inputs:
                if f in self.defines:
                    parts += [f]
            self.defines[exe] = parts
            flags = [args.flags or []]
            for f in args.inputs:
                if f in self.flags:
                    flags += [f]
            self.flags[exe] = flags
            sources = self.get_leaves(exe, self.deps)
            defines = sum(self.get_leaves(exe, self.defines), [])
            flags = sum(self.get_leaves(exe, self.flags), [])

            disable_prefix = False
            if splitext(exe)[-1] == '.so':
                exe = splitext(exe)[0]
                disable_prefix = True

            target = CMakeTarget(exe, sources, defines, args.libs, list(set(flags)), disable_prefix)
            if args.pthread:
                target.libs.append('${CMAKE_THREAD_LIBS_INIT}')
                self.pthread = True
            self.targets[target.name] = target

    def __str__(self):
        parts = [
            'cmake_minimum_required(VERSION 2.8)',
            'project({})'.format(self.name)
        ]
        if self.cxxstandards:
            if len(self.cxxstandards) > 1:
                print('Warning: multiple c++ standards', file=sys.stderr)
            standard = max(self.cxxstandards)
            m = re.search(r'[0-9]{2}', standard)
            if m:
                parts.append('set(CMAKE_CXX_STANDARD {})'.format(m.group(0)))
            else:
                flag = '-std=' + standard
                for i in self.targets.values():
                    if flag not in i.flags:
                        i.flags.append(flag)
        if self.cstandards:
            if len(self.cstandards) > 1:
                print('Warning: multiple c standards', file=sys.stderr)
            standard = max(self.cstandards)
            m = re.search(r'[0-9]{2}', standard)
            if m:
                parts.append('set(CMAKE_C_STANDARD {})'.format(m.group(0)))
            else:
                flag = '-std=' + standard
                for i in self.targets.values():
                    if flag not in i.flags:
                        i.flags.append(flag)
        if self.pthread:
            parts.append('find_package(Threads)')
        if self.include_dirs:
            parts.append('include_directories({})'.format(format_multiline(sorted(self.include_dirs))))

        for target in self.targets.values():
            if target.is_library:
                parts.append(str(target))
        for i in sorted(self.targets):
            target = self.targets[i]
            if not target.is_library:
                parts.append(str(target))
        return '\n\n'.join(parts)
