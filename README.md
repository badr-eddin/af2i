# AF2I
usage: AF2I [-h] [-f FILENAME] [-t TEXT] [-p] [-s] [-o OUTFILE] [-w] [-r] [-i] [-u] [-v] [-a] [-b] [-c {r,g,b}]

Convert text file content or text into png image ! This version does not contain converting non ascii letters ! add '@ig' flag in case you want to obfuscate a file
path, because (content | file path, -t, --text) reads from a file path if it is exists when you read from an Image, you can get specific characters by adding '@n' flag
to (-p --print -s --save), where n represents printed or saved content length

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
  -t TEXT, --text TEXT  content to be converted, set only one filename or text, filename is preferred !
  -p, --print           print retrieved data, preferred .
  -s, --save            save retrieved data, not preferred .
  -o OUTFILE, --outfile OUTFILE
                        output file. PNG in case of writing, otherwise any text-file !
  -w, --write
  -r, --read
  -i, --install
  -u, --uninstall
  -v, --version
  -a, --author
  -b, --bin             bin for binary-file
  -c {r,g,b}, --color {r,g,b}
                        main color of generated image .

check ou my new pentesting tool at [predator](https://predatorc.netlify.app)
## overview
basically it converts file bytes into 0s and 1s, then save it with opencv as png, it still has many issues.
![overview af2i](https://github.com/badr-eddin/af2i/blob/main/1689519768944.jpg?raw=true)
## Download
| Download | version | platform |
| ---------| ------- | ---------|
|[af2i primary version](https://github.com/badr-eddin/af2i/raw/main/version@0.0.1/af2i) | 0.0.1| linux |




