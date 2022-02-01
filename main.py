# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from append_files import ManageStatistics
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.cm as cm

# No of data points used
N = 51
#escra 100
data1 = [290.828,
300.698,
287.737,
322.716,
269.271,
314.823,
319.046,
283.599,
294.767,
283.656,
325.903,
286.636,
332.124,
286.793,
316.917,
294.614,
276.417,
301.993,
296.222,
329.859,
282.676,
328.816,
279.831,
310.771,
338.103,
278.535,
315.011,
292.659,
277.554,
280.816,
320.786,
304.829,
299.679,
284.692,
279.762,
305.917,
285.662,
292.821,
328.185,
294.888,
284.517,
311.702,
312.611,
288.766,
293.994,
336.872,
324.661,
296.691,
279.92,
305.593,
285.579]
#ow
data2 = [309.997,
277.892,
344.066,
283.863,
288.979,
327.061,
283.936,
284.932,
337.127,
332.121,
308.917,
283.118,
342.262,
285.946,
279.795,
316.183,
278.898,
271.999,
271.91,
291.032,
331.113,
290.973,
333.233,
354.257,
299.001,
296.002,
287.936,
278.968,
299.994,
271.78,
270.866,
338.2,
328.119,
282.84,
292.89,
279.817,
288.01,
319.056,
292.569,
333.79,
284.487,
295.274,
288.59,
333.749,
274.347,
349.821,
280.381,
277.671,
287.565,
303.629,
286.199]
#escra 80%
data3=[286.333,
309.638,
316.347,
292.816,
295.001,
274.967,
329.769,
335.257,
331.046,
320.887,
278.658,
316.966,
285.704,
317.825,
280.829,
300.962,
319.187,
281.717,
302.908,
293.964,
301.958,
296.899,
326.864,
289.918,
285.706,
321.401,
287.716,
325.042,
288.8,
317.925,
288.659,
300.026,
305.552,
293.693,
286.869,
324.043,
337.932,
289.751,
290.896,
323.202,
284.668,
325.117,
287.89,
285.645,
320.546,
300.325,
289.252,
322.414,
291.23,
332.515,
286.302]
print("[info] average latency of Escra: ", sum(data1)/len(data1))
print("[info] average latency of Native OW: ", sum(data2)/len(data2))
print("[info] average latency of Escra 80%: ", sum(data3)/len(data3))

# sort the data in ascending order
x1 = np.sort(data1)
x2 = np.sort(data2)
x3 = np.sort(data3)
# get the cdf values of y
y = np.arange(N) / float(N)
# plotting

fig, ax = plt.subplots(figsize=(5,2.2))

plt.xlabel('Latency (Sec)')
plt.ylabel('CDF')

ax.plot(x1, y, color='tab:orange', linestyle='--', label='Escra-OpenWhisk', zorder=10)
ax.plot(x2, y, color='tab:blue', linestyle='-', label='OpenWhisk', zorder=0)
ax.plot(x3, y, color='tab:green', linestyle=':', label='Escra-OpenWhisk \n(20% Fewer \nCores/MiB)', zorder=5)
# ax.xlim(200, 400)
#
# ratio = .8
# ax.set_xlim([200,400])
# #get x and y limits
# x_left, x_right = ax.get_xlim()
# y_low, y_high = ax.get_ylim()
#
# #set aspect ratio
# ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)


ax.legend(loc='lower right', prop={'size': 8.5})
ax.grid(color='grey', linestyle='--')
plt.subplots_adjust(bottom=0.22, top=.96, left=.13, right=.96)
# plt.tight_layout()

fig.savefig('GS_Latency.pdf', bbox_inches='tight')
fig.show()