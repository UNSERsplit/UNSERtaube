from multiprocessing import Process, Queue
import time
from typing import Optional, List
import math
import cmapy
import hashlib
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt
from queue import Empty

class Plot:
    def __init__(self, title: str, data_names: List[str]) -> None:
        self.title = title
        self.data_names = data_names

class Debug_Thread:
    def __init__(self, name: str, plots: List[Plot], keep_samples: int) -> None:
        self.process: Optional[Process] = None
        self.queue: Optional[Queue] = None
        
        self.name = name
        self.keep_time = keep_samples
        self.plot_meta = plots

        self.i = 0
    
    @staticmethod
    def _target(queue: Queue, plot_meta: List[Plot], name: str, keep_samples: int):
        plt.ion()
        plt.rcParams["keymap.quit"] = "ctrl+w", "cmd+w", "q"

        dim = math.ceil(math.sqrt(len(plot_meta)))

        fig, _plots = plt.subplots(dim, dim)
        _plots = [x for xs in _plots for x in xs][:len(plot_meta)]
        
        fig.suptitle(name)

        plots = {}
        axes = {}
        colors = {}

        legend = {}

        for i, (plot, meta) in enumerate(zip(_plots, plot_meta)):
            plot.title.set_text(meta.title)

            for data_name in meta.data_names:
                if data_name not in plots:
                    plots[data_name] = []
                    axes[data_name] = []
                    colors[data_name] = [x / 265 for x in cmapy.color('tab20', int(hashlib.sha256(data_name.encode('utf-8')).hexdigest(), 16) % 256, rgb_order=True)]
                
                line = plot.plot([0],[0], label=data_name, color=colors[data_name])[0]
                if data_name not in legend:
                    legend[data_name] = line
                plots[data_name].append(line)
                axes[data_name].append(plot)
        
        fig.legend(legend.values(), legend.keys(), loc="upper left")


        x_data = []
        t_start = time.time()

        y_data = {}
        for name in plots.keys():
            y_data[name] = []

        plt.show(block=False)
        fig.canvas.draw_idle()
        fig.canvas.flush_events()

        while True:
            try:
                data: dict = queue.get(timeout=0.1)
                if isinstance(data, int):
                    break

                for required in y_data:
                    if required not in data:
                        raise ValueError(f"{required} is required")

                x_data.append(time.time() - t_start)
                
                for k,v in data.items():
                    y_data[k].append(v)
                
                for k,pl in plots.items():
                    for i,p in enumerate(pl):
                        p.set_xdata(x_data[-keep_samples:])
                        p.set_ydata(y_data[k][-keep_samples:])
                        axes[k][i].relim()
                        axes[k][i].autoscale_view()
            except Empty:
                pass

            fig.canvas.draw_idle()
            fig.canvas.flush_events()
        plt.close("all")

    def start(self):
        if self.process is not None or self.queue is not None:
            raise RuntimeError("already running")
        self.queue = Queue()
        self.process = Process(target=self._target, args=(self.queue, self.plot_meta, self.name, self.keep_time))
        self.process.start()
    
    def stop(self):
        if self.process is None or self.queue is None:
            raise RuntimeError("not running")
        
        self.queue.put(-1)
        self.process.join()
        self.queue.close()
        self.queue = None
        self.process = None
    
    def plot(self, data: dict):
        if self.queue is None:
            raise RuntimeError("not running")
    
        self.i += 1
        if self.i % 5 == 0:
            self.queue.put(data)

if __name__ == '__main__':
    thread = Debug_Thread(
        name="Test plot",
        keep_samples=60, # 30s
        plots=[
            Plot("Plot a/b", ["a","b"]),
            Plot("Plot a/c", ["a","c"]),
            Plot("Plot a/b/c", ["a","b", "c"]),
            Plot("Delta", ["delta"])
        ]
    )
    thread.start()
    import random
    try:
        last = None
        while True:
            if last is None:
                last = time.time()
                time.sleep(0.5)
                continue

            delta = time.time() - last
            last = time.time()
            thread.plot({
                "a": random.random() * 100,
                "b": random.random() * 200,
                "c": random.random() * 300,
                "delta": delta
            })
            time.sleep(0.5)
    except KeyboardInterrupt:
        thread.stop()