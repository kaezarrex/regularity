
import clutter

class TextButtonView(clutter.Box):

    COLOR = clutter.color_from_string('#aaa')
    HOVER_COLOR = clutter.color_from_string('#999')

    def __init__(self, string):
        '''Constructs a view for navigating'''

        self.layout = clutter.BoxLayout()

        super(TextButtonView, self).__init__(self.layout)
        self.set_size(50, 50)
        self.set_color(self.COLOR)

        text = clutter.Text()
        text.set_font_name('Arial 20')
        text.set_text(string)
        text.set_color(clutter.color_from_string('#000'))

        pad_left = clutter.Rectangle()
        pad_left.set_opacity(0)
        pad_right = clutter.Rectangle()
        pad_right.set_opacity(0)

        self.layout.pack(pad_left, True, True, True, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)
        self.layout.pack(text, False, False, False, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)
        self.layout.pack(pad_right, True, True, True, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)

        self.bind_events()
        
    def bind_events(self):
        self.set_reactive(True)
        self.connect('enter-event', self.on_enter)
        self.connect('leave-event', self.on_leave)

    def on_enter(self, clutter_event, *args, **kwargs):
        self.set_color(self.HOVER_COLOR)

    def on_leave(self, clutter_event, *args, **kwargs):
        self.set_color(self.COLOR)
