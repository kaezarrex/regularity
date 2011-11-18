
import clutter

class TimelineList(clutter.Group):

    def __init__(self, model):
        super(clutter.Group, self).__init__()
    
        self.model = model

        text = clutter.Text()
        text.set_font_name('Sans 18')
        text.set_text('Timelines')
        text.set_color(clutter.color_from_string('#000'))

        self.add(text)



