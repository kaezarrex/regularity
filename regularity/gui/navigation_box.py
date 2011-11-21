
import clutter

from text_button_view import TextButtonView

class NavigationBox(clutter.Box):

    def __init__(self):
        '''Constructs a view for navigating'''

        self.layout = clutter.BoxLayout()

        super(NavigationBox, self).__init__(self.layout)
        self.set_color(clutter.color_from_string('#ccc'))

        left_button = TextButtonView('<')
        self.layout.pack(left_button, False, False, False, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)

        right_button = TextButtonView('>')
        self.layout.pack(right_button, False, False, False, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)

        pad = clutter.Rectangle()
        pad.set_opacity(0)
        self.layout.pack(pad, True, True, True, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)

        day_button = TextButtonView('1')
        self.layout.pack(day_button, False, False, False, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)

        week_button = TextButtonView('7')
        self.layout.pack(week_button, False, False, False, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)

        month_button = TextButtonView('31')
        self.layout.pack(month_button, False, False, False, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)

        year_button = TextButtonView('365')
        self.layout.pack(year_button, False, False, False, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)
    




        
