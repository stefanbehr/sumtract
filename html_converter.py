"""
Converts passed input file to html file. Writes to new
file labeled with .html.

"""

import argparse, sys, re

args = argparse.ArgumentParser()
args.add_argument('input', help='file to convert to html')

infile = sys.argv[1]
outfile = infile+'.html'

output = '<html>\n<head>\n<title>' + outfile + '</title>\n</head>\n<body bgcolor="white">'
    
body = open(infile).read()
body = re.sub(r'\n', r' ', body)
body = body.strip()
body = body.split('.')
index = 1
    
for line in body:
    id = str(index)
    output += '<a name="' + id + '">[' + id + ']</a> <a href="#' + id + '" id=' + id + '>' + line + '</a>\n'
    index += 1

output += '</body>\n</html>'

open(outfile, 'w').write(output)
