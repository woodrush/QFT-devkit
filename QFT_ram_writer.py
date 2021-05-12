import golly as g
from qftramheader import *

def write_initial_ram():
    write_bytes_filepath = g.opendialog("Open CSV for the Initial RAM Values", "CSV files (*.csv)|*.csv")

    if write_bytes_filepath:
        with open(write_bytes_filepath, "rt") as f:
            write_bytes = [map(int, line.split(",")) for line in f.readlines()]

        g.show("Writing initial RAM bytes...")
        for t in write_bytes:
            write_byte_at(*t)
        g.show("Done.")
        g.note("Wrote {} initial RAM bytes.".format(len(write_bytes)))
    else:
        g.note("Skipped writing initial RAM bytes.")

def write_stdin_buffer():
    stdin_string_filepath = g.opendialog("Open the text file to write to the stdin buffer")

    if stdin_string_filepath:
        with open(stdin_string_filepath, "rt") as f:
            stdin_string = f.read()
        write_ram(stdin_string)
        g.note("Wrote into the stdin buffer.\nFilepath:\n{}\nContent:\n{}".format(stdin_string_filepath, stdin_string))
    else:
        g.note("Skipped writing the stdin buffer.")


write_initial_ram()
write_stdin_buffer()
show_raw_ram_region()
show_registers()
show_stdio()
