def call_counter(func):
    def wrapped(*args, **kwargs):
        wrapped.call_count += 1
        return func(*args, **kwargs)

    setattr(wrapped, 'call_count', 0)
    return wrapped
