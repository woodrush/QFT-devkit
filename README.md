# QFT Devlopment Kit
This repository is a development kit for the computer from [The Quest for Tetris](https://github.com/QuestForTetris/QFT) (QFT), a programmable computer that works on Conway's Game of Life.

## Contents
- `QFT_15bit_rom_14bit_ram_blank.mc`:
  - A modified version of `Tetris8.mc` from [the original QFT repo](https://github.com/QuestForTetris/QFT) where the ROM and RAM demultiplexers are extended to 15 bits and 14 bits, respectively (the original pattern has a 9-bit ROM and 7-bit RAM architecture). Both the ROM and RAM slots are left blank so that new programs can be written in to the pattern.
  - As a side effect of the modification, the `SL` instruction behaves strangely in the new architecture. This can be worked around by using consecutive `ADD`s instead of the `SL` instruction.
- `QFT_prep_rom_ram.py`:
  - A script to write a QFTASM program and prepare a RAM module with a specified size in `QFT_15bit_rom_14bit_ram_blank.mc`.
- `QFT_ram_reader_writer.py`:
  - A tool to monitor values of registers and stdio, and also to write values to stdin.
- `MetafierV3.py`:
  - A modified version of `MetafierV2.py` from [the original QFT repo](https://github.com/QuestForTetris/QFT), made to be capable of handling very large patterns that contain thousands of ROM and RAM slots.
  - `MetafierV3.py` assumes that the width of the pattern is less than or equal to 2048, made to fit `QFT_15bit_rom_14bit_ram_blank.mc`. The size limit can be modified by hand if desired.
- `requirements.txt`:
  - A list of Python package requirements for this repository.
- `Varlife.rule`:
  - Copied from [the original QFT repo](https://github.com/QuestForTetris/QFT). Required to run Varlife patterns on Golly. Varlife is a cellular automaton rule made for designing the computer; please see the [Stack Exchange post for QFT](https://codegolf.stackexchange.com/questions/11880/build-a-working-game-of-tetris-in-conways-game-of-life).
- `metatemplate11.mc`:
  - Copied from [the original QFT repo](https://github.com/QuestForTetris/QFT). Required for running `MetafierV3.py`.


## Preparation
### Install Python Requirements
This devkit requires the pyparsing package (`pyparsing>=2.3.1`), used by `QFT_ram_reader_writer.py`.

### Install the Varlife Rule to Golly
In a Linux or Mac environment, add `Varlife.rule` to `~/.golly/Rules`.


## Usage
1. Prepare a QFTASM program.

2. Open `QFT_15bit_rom_14bit_ram_blank.mc` in Golly.

3. Copy the QFTASM program to your clipboard. On Golly, change the file view to this directory, and click on `QFT_prep_rom_ram.py` to execute it. A dialog prompting for the RAM size will appear, so enter the maximum RAM address used in the code (i.e. the number 1 less than the RAM size). This script will tile the ROM patterns and the RAM module to create a usable computer.

4. On Golly, use `QFT_ram_reader_writer.py` to write the standard input to the RAM. Specify the offsets for stdin and stdout by manually editing the script. A dialog prompting for the stdin string value will appear. The resulting pattern will be runnable on the Varlife rule. `QFT_ram_reader_writer.py` can be used to monitor the RAM values of a running pattern.

5. To convert the Varlife pattern to a Conway's Game of Life pattern, first press Ctrl + A (or Command + A on a Mac) in the editing screen on Golly to select the entire Varlife pattern, and execute `MetafierV3.py`. This will generate a file named `Output.mc` in this directory (or the same directory as `MetafierV3.py`, if the file is moved somewhere else) containing the output pattern.


## References
- The original QFT repository: https://github.com/QuestForTetris/QFT
- Stack Exchange post for QFT: https://codegolf.stackexchange.com/questions/11880/build-a-working-game-of-tetris-in-conways-game-of-life

