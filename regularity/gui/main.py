import clutter

from timeline_list import TimelineList

class RegularityWindow(object):

    def __init__(self, model):
        '''Create the main window.

           @param model : regularity.model.Model
               the model to use'''

        self.model = model
        self.stage = clutter.Stage()

        self.stage.add(TimelineList(self.model))

    def main(self):
        self.stage.set_size(1024, 650)
        self.stage.show_all()
        
        clutter.main()
