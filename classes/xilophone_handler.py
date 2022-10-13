from . import settings
from .xilophone import Xilophone
import time


class XilophoneHandler():
    def __init__(self, image_path, max_channels, outport):
        self.image_path = image_path
        self.max_channels = max_channels
        self.outport = outport
        self.xilo_threads = []
        for i in range(self.max_channels):
            xilo = Xilophone(
                i,
                int(settings.params[f"CHANNEL-{i}"]) - 1,
                settings.params["IMAGE"],
                settings.params[f"SCALE-{i}"],
                int(settings.params[f"ROOT-{i}"]),
                int(settings.params[f"OCTAVES-{i}"]),
                self.outport,
                note_length=int(settings.params[f"DURATION-{i}"]),
                separation=int(settings.params[f"SEPARATION-{i}"]),
                uncompressed=settings.uncompressed[i],
                x_axis_direction=settings.params[f"DIRECTION-{i}"],
                intervals=settings.params[f"INPUTSCALE-{i}"]
            )
            xilo.start()
            self.xilo_threads.append(xilo)

    def xilo_lifecycle(self):
        current_n_people = 0
        while settings.keep_playing:
            initial_n_people = min(self.max_channels, settings.people_counter)

            # we only change the current n of xilos if the n of people changed
            # for more than 1 secs
            time.sleep(1)
            final_n_people = min(self.max_channels, settings.people_counter)

            if initial_n_people == final_n_people:
                if final_n_people != current_n_people:
                    # silence all xilos
                    for xilo in self.xilo_threads[final_n_people:]:
                        xilo.stop_thread()
                    for i in range(final_n_people):
                        self.xilo_threads[i].resume_thread()
                    current_n_people = final_n_people
        for xilo in self.xilo_threads:
            # xilo.stop_thread()
            xilo.join()
