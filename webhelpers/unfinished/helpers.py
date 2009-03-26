"""\
A series of useful helper functions which aren't found in other libraries.
"""


def divide(a,b):
    """\
    Divides the fisrt argument by the second, returning an integer if possible, a float otherwise.

    For example::

        >>> divide(3,2)
        1.5
        >>> divide(3,1)
        3
    """
    if a%b:
        return a/float(b)
    else:
        return a/b

def size_to_human(
    size, 
    format='binary', 
    units=['B','KB','MB','GB','TB','PB','EB'], 
    digits = 4
):
    """\
    Converts an size in bytes to a human-readable format.  The following
    website outlines some of the issues involved with sizes:
    http://www.t1shopper.com/tools/calculate/

    ``size``

        The size as a number of bytes

    ``format``

        Whether you want to count 1000 bytes in a kilobyte like hard drive
        manufactures do ("decimal") or 1024 bytes in a kilobyte like everyone
        else does ("binary"). The default is "binary".

    ``units``

        The units you wish to use a list starting with the units for bytes and
        going up in factors of 1000 as far as you like. The defaults are
        sensible but this option allows you to use the new IEC units if you
        wish.

    ``digits``

        The number of digits to display in the result if there is a decimal.
        For example if the result was 522.67 KB this would become 522.7 KB if
        ``digits`` was 4. If ``digits`` was 3 it would be 523 KB.

        Set to ``0`` to display the whole result without formatting.

    Here are some examples:

        >>> size_to_human(534)
        '534 B'
        >>> size_to_human(534813)
        '522.3 KB'
        >>> size_to_human(534813000)
        '510 MB'
        >>> size_to_human(534813, format='decimal')
        '534.8 KB'
        >>> size_to_human(534813, digits=3)
        '522 KB'
        >>> size_to_human(1024**5, digits=0)
        '1 PB'
        >>> size_to_human(1024**6, digits=0)
        '1 EB'
        >>> size_to_human(1024**7, digits=0)
        '1024 EB'
        >>> size_to_human(534813, units=['B','KiB','MiB','GiB','TiB','PiB','EiB'])
        '522.3 KB'

    >>> size_to_human(534813)
    '522.3 KB'
    >>> size_to_human(534813, format='decimal')
    '534.8 KB'
    """
    if format == 'binary':  
        format = 1024
    elif format == 'decimal':
        format = 1000
    else:
        raise Exception('Can only convert sizes in binary or decimal format, not %r'%format)
    size=int(size)
    units=['B','KB','MB','GB','TB','PB','EB']
    counter = 0
    while (size>=format and counter<len(units)-1):
        size = divide(size, format)
        counter += 1
    if digits:
        size_ = str(size)
        if ('.' in size_) and (len(size_) > digits+1):
            number_of_digits_after_decimal = len(size_.split('.')[-1])
            number_of_digits_too_many = len(size_)-digits-1
            round_to = number_of_digits_after_decimal - number_of_digits_too_many
            size = round(size, round_to)

    if size == long(size):
        size = long(size)
    return "%s %s"%(size, units[counter])

if __name__ == '__main__':
    import doctest
    doctest.testmod()

