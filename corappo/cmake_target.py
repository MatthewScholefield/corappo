from corappo.formatting import format_multiline


class CMakeTarget:
    def __init__(self, name, sources=None, libs=None):
        self.name = name
        self.sources = sources or []
        self.libs = libs or []

    def __str__(self):
        parts = ['add_executable({})'.format(format_multiline([self.name] + self.sources))]
        if self.libs:
            parts.append('target_link_libraries({})'.format(format_multiline([self.name] + self.libs)))
        return '\n\n'.join(parts)
