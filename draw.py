import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# 定义坐标点和颜色
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]
colors = ['r', 'g', 'b', 'c', 'm']

# 绘制坐标点和圆形
fig, ax = plt.subplots()
for i in range(len(x)):
    ax.scatter(x[i], y[i], color=colors[i])
    circle = Circle((x[i], y[i]), 0.5, color=colors[i], alpha=0.2)
    ax.add_artist(circle)

# 设置图形标题和坐标轴标签
ax.set_title('2D Coordinate Points with Colors and Circles')
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')

# 显示图形
plt.show()