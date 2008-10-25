from xml.dom import minidom, Node
import re
import sys

def fix1(lines, lineno, column):
    print 'fix1'
    line = lines[lineno]
    sequence = '&nbsp;'
    res = re.search(sequence, line)
    if res is not None:
        print 'found `%s`' % sequence
        print line
        line = line.replace(sequence, '')
        lines[lineno] = line
        return True
    else:
        return False

def fix2(lines, lineno, column):
    print 'fix2'
    line = lines[lineno]
    line = line.replace('.SetUp?edit&redirectToReferer=true&redirectAction=', '')
    lines[lineno] = line

def fix3(lines, lineno, column):
    print 'fix3'
    line = lines[lineno]
    line = line.replace('gif">', 'gif"/>')
    lines[lineno] = line

def fix4(lines, lineno, column):
    print 'fix4'
    line = lines[lineno]
    line = line.replace('jpg">', 'jpg"/>')
    lines[lineno] = line

def parse_xml(html):

    xml = '<?xml version="1.0"?>' \
        '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">' + html
    return minidom.parseString(xml)

def parse_xml2(html):
    fixes = [ ]
    done = False
    prev_error = (0, 0)

    xml = '<?xml version="1.0"?>' \
        '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">' + html

    while done is False:
        try:
            error = False
            doc = minidom.parseString(xml)
            done = True
        except Exception, inst:
            print inst
            error = True

        if error:
            print 'there was an error'
            res = re.search('line (\d+), column (\d+)', str(inst))
            if res is not None:
                lineno = int(res.group(1)) - 1
                column = int(res.group(2))
                print 'line = %s; column = %s' % (lineno, column)

            lines = xml.split('\n')
            for fix in fixes:
                if fix(lines, lineno, column):
                    print 'fix applied'
                    break
                else:
                    print 'no fix applied'

            xml = '\n'.join(lines)

            last_error = (lineno, column)
            if last_error == prev_error:
                print 'same error as last time. Giving up.'
                print last_error
                print lines[lineno]
                done = True
                prev_error = last_error
    return doc
    
