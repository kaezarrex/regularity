
import clutter

class StatsBox(clutter.Box):
    
    def __init__(self, model):
        '''Constructs a view for managing editable text'''

        layout = clutter.BoxLayout()
        super(StatsBox, self).__init__(layout)
        self.set_color(clutter.color_from_string('#f00'))

        self.layout = layout
        self.model = model

        self.background = clutter.Rectangle()
        self.layout.pack(self.background, False, True, True, clutter.BOX_ALIGNMENT_START, clutter.BOX_ALIGNMENT_START)

        
