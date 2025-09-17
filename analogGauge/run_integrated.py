from rd1_gauge import RD1Gauge


def main():
    gauge = RD1Gauge()

    # 範例設定
    gauge.set_value("SHOTS", 2)    # 指向 "20"
    gauge.set_value("WB", 1)       # 指向 "☀"
    gauge.set_value("BATTERY", 3)  # 指向 "3/4"
    gauge.set_value("QUALITY", 1)  # 指向 "H"

    # 更新動畫幾個步驟以達到目標值
    for _ in range(120):
        gauge.update_animation()

    img = gauge.draw_integrated_rd1_display()
    out_path = "integrated_output.png"
    img.save(out_path)
    print(f"Saved integrated image to {out_path}")


if __name__ == '__main__':
    main()
