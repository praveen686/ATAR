def next_path(path_pattern):
    import os

    """
    Finds the next free path in an sequentially named list of files

    e.g. path_pattern = 'file-%s.txt':

    file-1.txt
    file-2.txt
    file-3.txt

    Runs in log(n) time where n is the number of existing files in sequence
    """
    i = 1

    # First do an exponential search
    while os.path.exists(path_pattern % i):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2  # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b

def load_pf_file(pickle_file_path):
    from vectorbtpro import Portfolio
    return Portfolio.load(pickle_file_path)

def save_record_to_file(df, path_to_file, write_mode='w'):
    from os import path
    if path.exists(path_to_file) and write_mode == 'a':
        df.to_csv(path_to_file, mode=write_mode, header=False)
    else:
        df.to_csv(path_to_file)

