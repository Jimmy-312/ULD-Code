# Copyright 2022 William Ro. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ======-=======================================================-===============
"""References: https://download.ni.com/evaluation/pxi/Understanding%20FFTs%20and%20Windowing.pdf"""
import matplotlib.pyplot as plt
import numpy as np

from pictor.plotters import SignalViewer



p = SignalViewer.plot([], fig_size=(9, 6), show=False)
sv: SignalViewer = p.plotters[0]
sv.new_settable_attr('fs', 500.0, float, 'Sampling frequency')
sv.new_settable_attr('T', 2.0, float, 'Sampling time')
sv.new_settable_attr('phi', 0.0, float, 'Delay')
sv.new_settable_attr('phi_step', 0.001, float, 'Step for changing delay')
sv.new_settable_attr('omega', 5.0, float, 'Angular frequency')
sv.new_settable_attr('win', None, str, 'Window to use')

sv.set('slim', '-100, 0', False, verbose=False)
sv.set('max_freq', 30, False, verbose=False)

def change_phi(d=1.0):
  phi, step = sv.get('phi'), sv.get('phi_step')
  sv.set('phi', phi + d * step, verbose=False)

sv.register_a_shortcut('h', lambda: change_phi(1), 'Increase phi')
sv.register_a_shortcut('l', lambda: change_phi(-1), 'Decrease phi')

def plot_hann(fig: plt.Figure):
  """This code is based on code snippet generated by Notion AI"""
  # Get signal and its corresponding time ticks
  window = np.hanning(51)

  # (1) Plot time domain
  ax1: plt.Axes = fig.add_subplot(211)
  ax1.plot(window)
  ax1.get_xaxis().set_visible(False)
  ax1.set_title('Hann Window')
  ax1.grid(True)

  # (2) Plot spectrum
  # Perform 1D-DFT
  A = np.fft.fft(window, 2048) / 25.5
  freq = np.linspace(-0.5, 0.5, len(A))
  response = 20 * np.log10(np.abs(np.fft.fftshift(A / (abs(A).max()))) + 1e-10)

  ax2: plt.Axes = fig.add_subplot(212)
  ax2.plot(freq, response)

  # Set styles
  ax2.set_xlim(-0.5, 0.5)
  ax2.set_ylim(-120, 0)
  ax2.set_title('Frequency response of the Hann window')
  ax2.set_xlabel('Normalized magnitude [dB]')
  ax2.set_ylabel('Normalized magnitude [dB]')
  ax2.grid(True)

def sig_gen(_sv: SignalViewer):
  # Get configuration
  fs, T, phi, omega, win = [_sv.get(k) for k in (
    'fs', 'T', 'phi', 'omega', 'win')]

  t = np.arange(T * fs + 1) / fs
  x = np.sin(2 * np.pi * omega * (t + phi))

  # Apply window if specified
  if win is not None: win = win.lower()
  if win in ('hann', 'hanning'): x = np.hanning(len(x)) * x

  # Set title
  sign = '+' if phi >= 0 else ''
  _sv.pictor.title_suffix = f'y = sin(2*pi*{omega:.1f}*(t{sign}{phi:.3f}))'
  if win is not None: _sv.pictor.title_suffix += f' {win}'
  return x, t

p.objects = [sig_gen]
p.add_plotter(plot_hann)
p.show()