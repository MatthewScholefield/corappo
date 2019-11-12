def format_multiline(parts: list) -> str:
    if len(parts) > 1:
        return '\n    {}\n'.format('\n    '.join(parts))
    return (parts or [''])[0]
