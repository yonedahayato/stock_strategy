
points = {"small": {
                "size": 20,
                "color": "blue"
                },
                "large": {
                "size": 10,
                "color": "red"
                },
        }

def draw_peak(plt, fig, ax, peak_info, peak_type="small"):
    size = points[peak_type]["size"]
    color = points[peak_type]["color"]
    ax.scatter(peak_info.peak_indexes, peak_info.peak_prices, s=size, c=color)

    return plt, fig, ax
