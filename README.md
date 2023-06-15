# DAT4005-PRAC1

## GUIDE
Program made on Python 3.11, requires at least 3.10 due to the use of match-case statements.

All files are available within provided .zip file, below in this document, or on Github
`git clone https://github.com/victorvintorez/DAT4005-PRAC1.git`

Parse Table CSV (parse_table.csv) must be in the same folder as python file, and must not be renamed!
The file location (relative to python file) and name are hard-coded so must not be changed!

The python program must be run from command line as it requires arguments when running!
Arguments are as below:
```py
usage: Compiler [-h] [-if INFILE] [-of OUTFILE] [-sp | --showparsed | --no-showparsed]

options:
  -h, --help            show this help message and exit
  -if INFILE, --infile INFILE
                        The path to the input file
  -of OUTFILE, --outfile OUTFILE
                        The path to the output file
  -sp, --showparsed, --no-showparsed
                        Show the parsed code in the console
```

Command used for testing are below (without parser output & with parser output)
`python main.py -if test_in.txt -of test_out.txt`
`python main.py -if test_in.txt -of test_out.txt --showparsed`
