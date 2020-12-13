import matplotlib.pyplot as plt  # directory for saving
import os
import re
import math
import json
import csv
import png
import numpy as np
from scipy.signal import hilbert
import matplotlib


def final(file, val, pref):
    max_data = max(map(max, val))
    min_data = min(map(min, val))
    data_color = [[int(255 * (x - min_data) / (max_data - min_data)) for x in l] for l in val]
    with open(file + pref, 'wb') as fpng:
        w = png.Writer(len(val[0]), len(val), greyscale=True)
        w.write(fpng, data_color)


def interpolate(v1, v2, factor):
    return v1 * (1 - factor) + v2 * factor


class Result:
    def __init__(self, dir='data/baseline/Sensor{}', conf='res/config.json'):
        # directory for final files,by sensors
        with open(conf) as jf:
            configuration = json.load(jf)
            self.window = configuration['WINDOW']  # Reading config
            self.number_of_sensors = configuration['NUMBER_OF_SENSORS']
            self.csv_root1 = configuration['ROOTS']['CSV_ROOT1']
            self.csv_root2 = configuration['ROOTS']['CSV_ROOT2']
            self.png_spectrum_root = configuration['ROOTS']['SPECTRUM']
            self.prehilb_root = configuration['ROOTS']['PREHILB']
            self.second_hilb = configuration['ROOTS']['SECOND_HILB']
            self.input_data = configuration['ROOTS']['INPUT']
            self.output_data = configuration['ROOTS']['OUTPUT']
        self.dir = dir
        self.cnt = 0
        self.raw_data = self.getRaw()

    def getRaw(self):
        file_names = []
        for i in range(self.number_of_sensors):
            file_name = os.listdir(self.dir.format(i))
            file_names.append(file_name)
        raws = []
        for dr in file_names:
            for i in dr:
                if re.match(r'^raw\d+.csv$', i):
                    raws.append(i)
        return raws

    def hilbert(self):
        for one_file in self.raw_data:
            with open(self.dir.format(self.cnt) + '/' + one_file) as fi:
                with open(self.dir.format(self.cnt) + self.csv_root1, 'w') as fo:
                    vals_init = [[float(x) for x in l.split()] for l in fi.readlines()]
                    vals = list(zip(*vals_init))  # Narrowband filtering + Hilbert transformation
                    res_fft = []
                    maxf = 0
                    for i, row in enumerate(vals):
                        fft = np.fft.rfft(row)  # this is to check the spectrum and find the carrying freauency
                        plt.plot(np.abs(fft)[10:])
                        maxf += np.abs(fft)[10:].argmax()
                    mid = maxf / len(vals)

                    for i, row in enumerate(vals):
                        fft = np.fft.rfft(row)
                        for j, freq in enumerate(fft):
                            if not (mid - self.window / 2.0 <= j <= mid + self.window / 2.0):
                                fft[j] = 0
                        res_fft.append(np.abs(hilbert(np.fft.irfft(fft))))
                    print(mid)
                    # saving spectrum
                    plt.savefig(self.dir.format(self.cnt) + self.png_spectrum_root)
                    res = list(zip(*res_fft))

                    max_data = max(map(max, res))
                    min_data = min(map(min, res))

                    for r in res:
                        stri = ""
                        for t in r:
                            stri += str(round((t - min_data) / (max_data - min_data), 2))
                            stri += " "
                        print(stri, file=fo)

                    with open(self.dir.format(self.cnt) + self.csv_root2, 'w') as fu:
                        for r in vals_init:
                            stri = ""
                            for t in r:
                                stri += str(round(t, 2))
                                stri += " "
                            print(stri, file=fu)

                    final(file=self.dir.format(self.cnt), val=vals_init, pref=self.prehilb_root)
                    final(file=self.dir.format(self.cnt), val=res, pref=self.second_hilb)
                    # writing final graphics
            self.cnt += 1  # plussing to copy next files in another folder

    def sectorize(self):
        with open(self.input_data) as ff:
            data = np.array([[abs(float(x)) for x in line.split()] for line in ff.readlines()])

            height = float(data.shape[0])
            width = float(data.shape[1])

            angle_rad = math.pi / 2

            r = height / angle_rad / 2.0
            R = r + width
            q = r * math.cos(angle_rad / 2.0)

            nh = math.ceil(R - q)
            nw = math.ceil(2 * R * math.sin(angle_rad / 2))

            new_data = [[0 for x in range(nw + 1)] for y in range(nh + 1)]

            cx = nw / 2.0
            cy = q

            for i in range(nh):
                for j in range(nw):
                    x = j + 0.5
                    y = i + 0.5
                    dx = x - cx
                    dy = cy + y

                    d = (dx ** 2 + dy ** 2) ** 0.5 - r

                    d1 = math.floor(d)
                    d2 = math.ceil(d)

                    a = (0.5 + math.atan2(dx, dy) / angle_rad) * height

                    ray1 = math.floor(a)
                    ray2 = math.ceil(a)
                    ray0 = ray1 - 1
                    ray3 = ray2 + 1

                    if all([0 <= d1 < width, 0 <= d2 < width, 0 <= ray1 < height, 0 <= ray2 < height,
                            0 <= ray0 < height, 0 <= ray3 < height]):
                        r1v = interpolate(data[ray1][d1], data[ray1][d2], math.modf(d)[0])
                        r2v = interpolate(data[ray2][d1], data[ray2][d2], math.modf(d)[0])
                        v = interpolate(r1v, r2v, math.modf(a)[0])
                        z = v * v * v
                        new_data[i][j] = z
                    else:
                        new_data[i][j] = -1
            max_data = max(map(max, new_data))

            for i in range(nh):
                for j in range(nw):
                    if (new_data[i][j] == -1):
                        new_data[i][j] = max_data

            min_data = min(map(min, new_data))
            data_color = [[int(255 * (x - min_data) / (max_data - min_data)) for x in l] for l in new_data]
            with open(self.output_data, 'wb') as fff:
                w = png.Writer(nw + 1, nh + 1, greyscale=True)
                w.write(fff, data_color)


result = Result()
result.hilbert()
result.sectorize()
