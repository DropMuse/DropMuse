def format_duration(seconds):
    if not seconds:
        return "0:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    fmt = "%02d:%02d" if h > 0 else "%d:%02d"
    formatted = fmt % (m, s)
    if h:
        formatted = ("%d:" % h) + formatted
    return formatted
