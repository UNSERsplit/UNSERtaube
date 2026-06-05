from multiprocessing import Process, Queue
import time
from typing import Optional
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
from queue import Empty

class Debug_Thread:
    def __init__(self) -> None:
        self.process: Optional[Process] = None
        self.queue: Optional[Queue] = None
    
    @staticmethod
    def _target(queue: Queue):
        plt.ion()
        print("Target", 1)
        plt.rcParams["keymap.quit"] = "ctrl+w", "cmd+w", "q"
        print("Target", 2)
        fig, ((err_roll, err_throttle), (err_pitch, err_yaw)) = plt.subplots(2,2)
        print("Target", 3)
        fig.suptitle('PID-Errors')
        print("Target", 4)

        err_roll.title.set_text("Roll")
        plt_roll = err_roll.plot([0],[0], label="error")[0]

        err_throttle.title.set_text("Throttle")
        plt_throttle = err_throttle.plot([0],[0], label="error")[0]

        err_pitch.title.set_text("Pitch")
        plt_pitch = err_pitch.plot([0],[0], label="error")[0]

        err_yaw.title.set_text("Yaw")
        plt_yaw = err_yaw.plot([0],[0], label="error")[0]

        x_data = []
        t_start = time.time()

        r = []
        t = []
        p = []
        y = []

        print("Target", 5)

        plt.show(block=False)
        print("Target", 6)

        while True:
            try:
                data = queue.get(timeout=0.1)

                roll, throttle, pitch, yaw = data
                x_data.append(time.time() - t_start)

                plt_roll.set_xdata(x_data)
                plt_throttle.set_xdata(x_data)
                plt_pitch.set_xdata(x_data)
                plt_yaw.set_xdata(x_data)

                r.append(roll)
                t.append(throttle)
                p.append(pitch)
                y.append(yaw)

                plt_roll.set_ydata(r)
                plt_throttle.set_ydata(t)
                plt_pitch.set_ydata(p)
                plt_yaw.set_ydata(y)

                err_roll.relim()
                err_roll.autoscale_view()
                err_throttle.relim()
                err_throttle.autoscale_view()
                err_pitch.relim()
                err_pitch.autoscale_view()
                err_yaw.relim()
                err_yaw.autoscale_view()
            except Empty:
                pass
            except TypeError:
                break

            fig.canvas.draw_idle()
            fig.canvas.flush_events()
        plt.close()

    def start(self):
        if self.process is not None or self.queue is not None:
            raise RuntimeError("already running")
        self.queue = Queue()
        self.process = Process(target=self._target, args=(self.queue,))
        self.process.start()
    
    def stop(self):
        if self.process is None or self.queue is None:
            raise RuntimeError("not running")
        
        self.queue.put(-1)
        self.process.join()
        self.queue.close()
    
    def plot(self, roll, throttle, pitch, yaw):
        if self.queue is None:
            raise RuntimeError("not running")
        self.queue.put((roll, throttle, pitch, yaw))

if __name__ == '__main__':
    thread = Debug_Thread()
    thread.start()
    import random
    try:
        while True:
            thread.plot(random.random() * 10, random.random() * 10, random.random() * 10, random.random() * 10)
            time.sleep(0.5)
    except KeyboardInterrupt:
        thread.stop()