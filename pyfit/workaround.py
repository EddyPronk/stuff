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

def parse_xml(xml):
    fixes = [ fix1, fix2 ]
    done = False
    prev_error = (0, 0)

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
                open('error', 'w').write(xml)
                print last_error
                print lines[lineno]
                done = True
                prev_error = last_error
    return doc
    
