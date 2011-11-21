import clutter

from navigation_box import NavigationBox
from time_period_box import TimePeriodBox

class RegularityApp(object):

    def __init__(self, model):
        '''Create the main window.

           @param model : regularity.model.Model
               the model to use'''

        self.model = model

        self.stage = clutter.Stage()
        self.stage.set_user_resizable(True)
        self.stage.connect('destroy', clutter.main_quit)

        # create the layout manager, add its actor to the stage
        self.layout = clutter.BoxLayout()
        self.layout.set_vertical(True)
        self.layout.set_pack_start(True)
        self.box = clutter.Box(self.layout)
        self.stage.add(self.box)

        # set up bindings for events, such as resize
        self.bind_events()

    def bind_events(self):
        self.stage.connect('allocation-changed', self.on_allocation_changed)

    def on_allocation_changed(self, stage, allocation, flags):
        width, height = allocation.size
        self.box.set_size(width, height)

    def main(self):
        time_period_box = TimePeriodBox(self.model)
        self.layout.pack(time_period_box, False, True, True, clutter.BOX_ALIGNMENT_CENTER, clutter.BOX_ALIGNMENT_CENTER)

        navigation_box = NavigationBox()
        self.layout.pack(navigation_box, False, True, False, clutter.BOX_ALIGNMENT_START, clutter.BOX_ALIGNMENT_START)

        self.stage.show_all()
        
        clutter.main()
