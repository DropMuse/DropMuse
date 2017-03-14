def format_duration(seconds):
    if not seconds:
        return "0:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    formatted = "%d:%02d" % (m, s)
    if h:
        formatted = ("%d:" % h) + formatted
    return formatted
