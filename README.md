# Uniform and random sampling on SAT formulae : Application on the Linux Kernel

# Échantillonnage aléatoire, uniforme sur des formules SAT : Application au kernel Linux

## Comparison 

Program that compares the features of a dimacs file and a csv file of
all options (generated with [this
tool](https://github.com/TuxML/Kanalyser/)).

### Usage

Move the the directory containing the program then type
```
python comparison.py -h
```
to show help.
```
usage: comparison.py [-h] -dimacs DIMACS -csv CSV

optional arguments:
  -h, --help      show this help message and exit
  -dimacs DIMACS  path (including the file) to the dimacs file
  -csv CSV        path (including the file) to the csv file


```

### Example

You can find an example of the output (with the [Linux kernel version
4.14.152](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tag/?h=v4.14.152)
on x86 architecture) [here](examples/outputx86.4.14.152).

The dimacs file was generated by myself with
[kconfigreader](https://github.com/ckaestne/kconfigreader) (with some
workaround you can find
[here](https://github.com/ckaestne/kconfigreader/issues/2#issuecomment-164312936)).

You can find the generated "all-options" csv file
[here](examples/alloptions-x86.4.14.152.csv).

If you want to test the program in this directory, you can type the
command below:

```bash
python comparison.py -dimacs examples/out.dimacs -csv examples/alloptions-x86.4.14.152.csv
```

## Extractor

The `extractor.py` program tests the validity of a dimacs formula by
adding each options of a "valid" linux kernel configuration file
(`.config`) as a clause according to our understanding of its
representation made by kconfigreader.

We assume the configuration to be valid because the `.config` file is
generated by some tools written by the linux kernel developers. The
list of configurations generated are: __tinyconfig__, __randconfig__,
__defconfig__, __allnoconfig__, __allyesconfig__, __allmodconfig__,
__alldefconfig__ (as listed
[here](https://github.com/torvalds/linux/blob/dbab40bdb42c03ab12096d4aaf2dbef3fb55282c/scripts/kconfig/Makefile#L121)).


For more details about kconfig:
* https://www.kernel.org/doc/Documentation/kbuild/kconfig-language.txt;
* https://dl.acm.org/doi/10.1145/2936314.2814222.

### Usage

Just type
```
python extractor.py -h
```
to have this :
```
usage: extractor.py [-h] [--cdir CDIR] [--dimacs DIMACS] [--csv CSV] [-n N]
                    [--verbose]

optional arguments:
  -h, --help       show this help message and exit
  --cdir CDIR      local directory of linux source code (to launch the Makefile)
  --dimacs DIMACS  dimacs file name
  --csv CSV        all options csv file
  -n N             nb of iteration
  --verbose, -v
```

The _nb of iteration_ parameter is __required__. If the other
parameters are not specified, the program will run with the path
defined as constants in the source code which are the path on my
computer.

If you want to test only with few "type" of configuration
(e. g. __tinyconfig__ etc ...), feel free to edit the list `CONF` of
the source code :p.

This program will show you what is happening during the whole process
(with `--verbose`)while writing a csv file named
`extractor_out.csv`. If you want to keep the trace, just redirect the
output into a like so:
```
python extractor.py --cdir linux-kernel/path --dimacs dimacs/file --csv csv/file --verbose >> my_trace
```
