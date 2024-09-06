import matplotlib.pyplot as plt
import numpy as np

# Sample data: dates and corresponding admissions/discharges
dates = ['2024-09-01', '2024-09-02', '2024-09-03', '2024-09-04', '2024-09-05']
admissions = [30, 45, 35, 50, 40]  # Positive values for admissions
discharges = [-20, -35, -25, -30, -28]  # Negative values for discharges

# Convert dates into a numpy array to handle the x axis
x = np.arange(len(dates))

# Create the plot
fig, ax = plt.subplots()

# Plot admissions and discharges
ax.bar(x, admissions, width=0.4, color='green', label='Admissions', align='center')
ax.bar(x, discharges, width=0.4, color='red', label='Discharges', align='center')

# Add labels, title, and legend
ax.set_xticks(x)
ax.set_xticklabels(dates)
ax.set_xlabel('Date')
ax.set_ylabel('Number of Patients')
ax.set_title('Patient Admissions and Discharges Over Time')
ax.legend()

# Show the plot
plt.savefig("patient-delta.png")
