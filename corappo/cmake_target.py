from corappo.formatting import format_multiline


class CMakeTarget:
    def __init__(self, name, sources=None, defines=None, libs=None, flags=None, disable_prefix=False):
        self.name = name
        self.sources = sources or []
        self.defines = defines or []
        self.libs = libs or []
        self.flags = flags or []
        self.disable_prefix = disable_prefix

    @property
    def is_library(self):
        return '-shared' in self.flags

    def __str__(self):
        flags = list(self.flags)
        parts = []
        if '-shared' in flags:
            flags.remove('-shared')
            parts += ['add_library({})'.format(format_multiline([self.name] + ['SHARED'] + self.sources))]
            if self.disable_prefix:
                parts += ['set_target_properties({} PROPERTIES PREFIX "")'.format(self.name)]
        else:
            parts += ['add_executable({})'.format(format_multiline([self.name] + self.sources))]
        if self.libs:
            parts += ['target_link_libraries({})'.format(format_multiline([self.name] + self.libs))]
        if self.defines:
            args = [self.name] + ['PUBLIC'] + self.defines
            parts += ['target_compile_definitions({})'.format(format_multiline(args))]
        if flags:
            args = [self.name] + ['PRIVATE'] + [i + ';' for i in flags]
            parts += ['target_compile_options({})'.format(format_multiline(args))]
        return '\n\n'.join(parts)
