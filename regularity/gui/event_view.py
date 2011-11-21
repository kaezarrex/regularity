from itertools import izip

import clutter

class EventView(clutter.Group):

    def __init__(self, model, events, start, end):
        super(EventView, self).__init__()

        self.model = model
        self.events = events
        self.start = start
        self.end = end

        self.rectangles = list()
        self.rectangle_params = list()
        total_seconds = (self.end - self.start).total_seconds()
        for event in self.events:
            offset_seconds = (event['start'] - self.start).total_seconds()
            duration_seconds = (event['end'] - event['start']).total_seconds()

            normalized_offset = offset_seconds / total_seconds
            normalized_duration = duration_seconds / total_seconds

            rectangle = clutter.Rectangle()
            rectangle.set_color(clutter.color_from_string('#0f07'))
            rectangle.set_border_width(1)
            rectangle.set_border_color(clutter.color_from_string('#0f0'))

            rectangle.set_height(10)
            self.rectangles.append(rectangle)

            self.add(rectangle)

            self.rectangle_params.append(dict(
                normalized_offset=normalized_offset,
                normalized_duration=normalized_duration
            ))

        self.bind_events()


    def bind_events(self):
        self.connect('paint', self.on_paint)

    def on_paint(self, event_view):
        width, height = self.get_size()
        self.layout(width, height)

    def layout(self, available_width, available_height):

        for event, rectangle, params in izip(self.events, self.rectangles, self.rectangle_params):
            x = max(0, available_width * params['normalized_offset'])
            y = 0

            width = available_width * params['normalized_duration']
            if x + width > available_width:
                width = available_width - x
            height = 10

            rectangle.set_position(x, y)
            #rectangle.set_size(width, height)
            rectangle.set_width(width)

