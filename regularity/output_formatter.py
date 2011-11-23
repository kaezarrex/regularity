
from itertools import imap, izip

class OutputFormatter(object):

    def __init__(self, *args):
        '''Create an OutputFormatter, an object for printing tabular, formatted
           data in a good way.

           @param args : positional arguments
               a list of objects that can be formatted using str.format()'''

        if not args:
            raise ValueError('at least one row must be supplied')

        self.data = args
        self.n_columns = len(args[0])
        self.formats = list('{:}' for i in xrange(self.n_columns))
        self.pads = list(False for i in xrange(self.n_columns))
    
    def set_column_format(self, column, format_):
        '''Sets the format string for a column.

           @param column : int
               the index of the column
           @param format : str
               the format string'''
        
        if column < 0 or column > self.n_columns - 1:
            raise ValueError('column is out of range')

        self.formats[column] = format_
    
    def set_column_pad_left(self, column, pad_left):
        '''Sets the format string for a column.

           @param column : int
               the index of the column
           @param pad_left : bool
               if True, pad this column on the left, otherwise, pad on the right'''
        
        if column < 0 or column > self.n_columns - 1:
            raise ValueError('column is out of range')

        self.pads[column] = pad_left

    def iformat_row(self, row):
        '''Return an iterator over row, after it has been formatted.

           @param row : iterable
               a iterable of objects to be formatted'''

        for format_, column in izip(self.formats, row):
            if isinstance(column, (list, tuple)):
                yield format_.format(*column)
            else:
                yield format_.format(column)

    def iformat_rows(self):
        '''Return an iterator over the formatted rows.'''

        for row in self.data:
            yield self.iformat_row(row)
        
    def column_widths(self):
        '''Return the widths of the columns, the length of the longest
           formatted element in each column'''
        
        idata = self.iformat_rows()

        row = idata.next()
        widths = imap(len, row)
        for row in idata:
            _widths = imap(len, row)
            widths = imap(max, izip(widths, _widths))
        
        widths = list(widths)
        return widths

    def pad(self, s, width, pad_character=' ', pad_left=False):
        '''Pad a string with whitespace to be as long as width.

           @param s : str
               the string to pad
           @param width : int
               the desired width
           @param pad_character : str
               a single character used to pad strings
           @param pad_left : optional, bool
               if True, pad on the left, otherwise, pad on the right'''

        s_len = len(s)

        if s_len > width:
            raise ValueError('string is longer than allowed width')

        if len(pad_character) != 1:
            raise ValueError('pad_character must be exactly one character')

        pad_string = pad_character * (width - s_len)

        if pad_left:
            return pad_string + s

        return s + pad_string


    def output(self, row_joiner='\n', column_joiner=' ', pad_character=' '):
        '''Print out the formatted data.

           @param row_joiner : optional, str
               what to use to join rows together
           @param column_joiner : optional, str
               what to use to join columns together
           @param pad_character : str
               a single character used to pad strings'''
        
        widths = self.column_widths()

        formatted_rows = list()
        for row in self.iformat_rows():
            formatted_row = list()

            for column, w, pad_left in izip(row, widths, self.pads):
                formatted_row.append(self.pad(column, w, pad_character=pad_character, pad_left=pad_left))

            formatted_rows.append(column_joiner.join(formatted_row))

        print row_joiner.join(formatted_rows)
            
            

