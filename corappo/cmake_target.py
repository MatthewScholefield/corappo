from corappo.formatting import format_multiline


class CMakeTarget:
    def __init__(self, name, sources=None, defines=None, libs=None, flags=None):
        self.name = name
        self.sources = sources or []
        self.defines = defines or []
        self.libs = libs or []
        self.flags = flags or []

    def __str__(self):
        parts = ['add_executable({})'.format(format_multiline([self.name] + self.sources))]
        if self.libs:
            parts += ['target_link_libraries({})'.format(format_multiline([self.name] + self.libs))]
        if self.defines:
            args = [self.name] + ['PUBLIC'] + self.defines
            parts += ['target_compile_definitions({})'.format(format_multiline(args))]
        if self.flags:
            parts += ['target_compile_options({})'.format(format_multiline([i + ';' for i in self.flags]))]
        return '\n\n'.join(parts)
