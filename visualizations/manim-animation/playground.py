from math import floor
from matplotlib import cm
from manim import *
from manim.typing import Vector3D
from numpy.lib.stride_tricks import sliding_window_view
from numpy.ma.core import anomalies
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
config["background_color"] = WHITE

def pre():
    values = np.load("values.npy")
    values = values[:20_000]

    windows = sliding_window_view(values, window_shape=2000)
    projected = PCA(n_components=2).fit_transform(windows)
    scores = []
    for point in projected:
        scores.append(np.linalg.norm(point))
    scores_norm = MinMaxScaler().fit_transform(np.array(scores).reshape(-1, 1))[:, 0]

    projected = MinMaxScaler().fit_transform(projected)
    values = MinMaxScaler().fit_transform(values.reshape(-1, 1)).reshape(1, -1)[0]
    colors = cm.get_cmap('turbo')(scores_norm)
    return values, projected, colors

class ContinuousMotion(Scene):
    def construct(self):
        func = lambda pos: np.sin(pos[0] / 2) * UR + np.cos(pos[1] / 2) * LEFT
        stream_lines = StreamLines(func, stroke_width=2, max_anchors_per_line=30)
        self.add(stream_lines)
        stream_lines.start_animation(warm_up=False, flow_speed=1.5)
        self.wait(stream_lines.virtual_time / stream_lines.flow_speed)

class Example1(Scene):
    def timeseries(self, values, t):
        index = min(len(values) - 1, floor(len(values) * t))
        x = -6-1/9 + t * 12
        return x, values[index] + 2, 0

    def projected_to_scene(self, p):
        x = (p[0] - 0.5) * 5
        y = (p[1] - 0.5) * 5 - 1
        return np.array((x, y, 0.0))

    def line_start_end(self, t, values, projected):
        index_p = min(len(projected) - 1, floor(len(projected) * t))
        start = self.timeseries(values, t)
        end = self.projected_to_scene(projected[index_p])
        return start, end



    def construct(self):
        values, projected, colors = pre()
        func = ParametricFunction(lambda t: self.timeseries(values, t), t_range=(0, 1, 0.0001), fill_opacity=0).set_color(BLACK)
        self.add(func.scale(1))
        dots = VGroup(*[Dot(point=self.projected_to_scene(p), radius=0.01, color=BLACK) for p in projected])
        self.add(dots)

        t_values = np.arange(0, 1, 0.001)
        arcs = []
        for t in t_values:
            start, end = self.line_start_end(t, values, projected)
            index_p = min(len(projected) - 1, floor(len(projected) * t))
            arc = Line(start=start, end=end, stroke_color=ManimColor(colors[index_p]), path_arc=1)
            arcs.append(arc)
        arcs = VGroup(*arcs)

        animations = []
        for arc in arcs:
            animations.append(Succession(Create(arc), FadeOut(arc)))

        self.play(LaggedStart(*animations, lag_ratio=0.03, run_time=30))




if __name__ == '__main__':
    pre()