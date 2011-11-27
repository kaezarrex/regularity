
import clutter

class TextBox(clutter.Box):
    
    def __init__(self, model):
        '''Constructs a view for managing editable text'''

        layout = clutter.BinLayout(clutter.BIN_ALIGNMENT_CENTER, clutter.BIN_ALIGNMENT_CENTER)
        super(TextBox, self).__init__(layout)

        self.layout = layout
        self.model = model

        self.background = clutter.Rectangle()
        self.background.set_reactive(True)
        self.background.set_color(clutter.color_from_string('#fff'))
        self.background.set_border_width(1)
        self.background.set_border_color(clutter.color_from_string('#000'))
        self.layout.add(self.background, clutter.BIN_ALIGNMENT_FILL, clutter.BIN_ALIGNMENT_FILL)

        self.search_field = clutter.Text()
        self.search_field.set_font_name('Arial 20')
        self.search_field.set_activatable(True)
        self.search_field.set_editable(True)
        self.search_field.set_text('Search')
        self.layout.add(self.search_field, clutter.BIN_ALIGNMENT_CENTER, clutter.BIN_ALIGNMENT_CENTER)

        self.bind_events()

    def bind_events(self):
        self.background.connect('button-press-event', self.on_button_press_event)

    def on_button_press_event(self, actor, click_event):
        stage = self.search_field.get_stage()
        stage.set_key_focus(self.search_field)
        
