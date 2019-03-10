
points = {"small": {
                "size": 20,
                "color": "blue"
                },
                "large": {
                "size": 10,
                "color": "red"
                },
        }

FLAG_DRAW_INDEX = False
FLAG_DRAW_INDEX_IN_PEAK = False

def draw_peak(plt, fig, ax, peak_info, peak_type="small"):
    if peak_type not in ["small", "large"]:
        logger.error("peak type is invalid.")

    size = points[peak_type]["size"]
    color = points[peak_type]["color"]
    ax.scatter(peak_info.peak_indexes, peak_info.peak_prices, s=size, c=color)

    if FLAG_DRAW_INDEX_IN_PEAK and peak_type == "small":
        for cnt, (index, price) in enumerate(zip(peak_info.peak_indexes, peak_info.peak_prices)):
            ax.annotate(str(cnt), (index, price))

    elif FLAG_DRAW_INDEX:
        for index, price in zip(peak_info.peak_indexes, peak_info.peak_prices):
            ax.annotate(str(index), (index, price))

    return plt, fig, ax
