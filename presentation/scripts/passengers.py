import pandas as pd
from dateutil import parser
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.axisartist import SubplotZero

df = pd.read_csv('AirPassengers.csv')
passengers = df["Passengers"].to_numpy()
months = [parser.parse(m) for m in df["Month"].tolist()]

fig = plt.figure(figsize=(20, 8))
ax = SubplotZero(fig, 111)
fig.add_subplot(ax)
for direction in ["right", "top"]:
    ax.axis[direction].set_visible(False)
ax.axis["bottom"].set_axisline_style("-|>")
ax.axis["left"].set_axisline_style("-|>")
plt.xlabel("Time")
plt.ylabel("Passengers")
plt.plot(months, passengers, color="black")
plt.axis('off')
plt.savefig('passengers.png', dpi=300, bbox_inches='tight')
