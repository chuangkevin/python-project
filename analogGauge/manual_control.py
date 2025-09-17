import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
try:
    # When imported as package: analogGauge.manual_control
    from .rd1_gauge import RD1Gauge
except Exception:
    # When run as a script from the analogGauge directory
    from rd1_gauge import RD1Gauge
import time

class ManualControlApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("RD-1 Gauge Manual Control")

        # Left frame: controls
        ctrl_frame = ttk.Frame(root)
        ctrl_frame.grid(row=0, column=0, sticky="ns", padx=8, pady=8)

        # Reset on start option (controls whether gauge does start->reset animation)
        self.reset_var = tk.BooleanVar(value=True)
        reset_chk = ttk.Checkbutton(ctrl_frame, text="Reset on start", variable=self.reset_var)
        reset_chk.grid(row=0, column=0, sticky="w", pady=(0, 6))

        # Gauge (constructed after the reset option so we can pass the flag)
        self.gauge = RD1Gauge(reset_on_start=self.reset_var.get())

        # Keep the gauge updated when the checkbox toggles (live binding)
        try:
            # modern tkinter
            self.reset_var.trace_add("write", lambda *a: setattr(self.gauge, "reset_on_start", self.reset_var.get()))
        except Exception:
            # fallback
            def _on_reset_var(*args):
                setattr(self.gauge, "reset_on_start", self.reset_var.get())
            self.reset_var.trace("w", _on_reset_var)

        # SHOTS
        shots_max = len(self.gauge.GAUGE_CONFIGS["SHOTS"]["values"]) - 1
        ttk.Label(ctrl_frame, text="SHOTS").grid(row=1, column=0)
        self.shots_var = tk.IntVar(value=0)
        shots_scale = ttk.Scale(ctrl_frame, from_=0, to=shots_max, orient="horizontal",
                                command=self._on_shots_change, variable=self.shots_var)
        shots_scale.grid(row=2, column=0, sticky="we")

        # WB
        wb_max = len(self.gauge.GAUGE_CONFIGS["WB"]["values"]) - 1
        ttk.Label(ctrl_frame, text="WB").grid(row=3, column=0)
        self.wb_var = tk.IntVar(value=0)
        wb_scale = ttk.Scale(ctrl_frame, from_=0, to=wb_max, orient="horizontal",
                             command=self._on_wb_change, variable=self.wb_var)
        wb_scale.grid(row=4, column=0, sticky="we")

        # BATTERY
        bat_max = len(self.gauge.GAUGE_CONFIGS["BATTERY"]["values"]) - 1
        ttk.Label(ctrl_frame, text="BATTERY").grid(row=5, column=0)
        self.bat_var = tk.IntVar(value=bat_max)
        bat_scale = ttk.Scale(ctrl_frame, from_=0, to=bat_max, orient="horizontal",
                              command=self._on_bat_change, variable=self.bat_var)
        bat_scale.grid(row=6, column=0, sticky="we")

        # QUALITY
        q_max = len(self.gauge.GAUGE_CONFIGS["QUALITY"]["values"]) - 1
        ttk.Label(ctrl_frame, text="QUALITY").grid(row=7, column=0)
        self.q_var = tk.IntVar(value=0)
        q_scale = ttk.Scale(ctrl_frame, from_=0, to=q_max, orient="horizontal",
                            command=self._on_q_change, variable=self.q_var)
        q_scale.grid(row=8, column=0, sticky="we")

        # Buttons
        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.grid(row=9, column=0, pady=(8, 0))
        ttk.Button(btn_frame, text="Save Image", command=self._save_image).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Toggle Labels", command=self._toggle_labels).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text="Reset", command=lambda: self.gauge.reset()).grid(row=0, column=2, padx=4)

        # Right frame: display
        disp_frame = ttk.Frame(root)
        disp_frame.grid(row=0, column=1, padx=8, pady=8)

        self.canvas_size = 400
        self.canvas = tk.Canvas(disp_frame, width=self.canvas_size, height=self.canvas_size)
        self.canvas.grid(row=0, column=0)

        self.tk_image = None
        self._last_update = time.time()

        # Ensure initial values set
        self.gauge.set_value("SHOTS", int(0))
        self.gauge.set_value("WB", int(0))
        self.gauge.set_value("BATTERY", int(bat_max))
        self.gauge.set_value("QUALITY", int(0))

        # Prepare initial image on canvas and start update loop
        init_img = self.gauge.draw_integrated_rd1_display()
        self.tk_image = ImageTk.PhotoImage(init_img)
        # create a single canvas image item and reuse it
        self._canvas_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        self._running = True
        self._update_loop()

        # Close handling
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_shots_change(self, val):
        try:
            self.gauge.set_value("SHOTS", int(float(val)))
        except Exception:
            pass

    def _on_wb_change(self, val):
        try:
            self.gauge.set_value("WB", int(float(val)))
        except Exception:
            pass

    def _on_bat_change(self, val):
        try:
            self.gauge.set_value("BATTERY", int(float(val)))
        except Exception:
            pass

    def _on_q_change(self, val):
        try:
            self.gauge.set_value("QUALITY", int(float(val)))
        except Exception:
            pass

    def _toggle_labels(self):
        self.gauge.set_label_visibility(not self.gauge.get_label_visibility())

    def _save_image(self):
        img = self.gauge.draw_integrated_rd1_display()
        path = "manual_control_output.png"
        img.save(path)
        print(f"Saved image to {path}")

    def _update_loop(self):
        if not self._running:
            return
        # calculate dt based on real time so animation is time-consistent
        now = time.time()
        dt = now - self._last_update if self._last_update else (1.0/120.0)
        self._last_update = now

        # update animation and render (pass dt for time-based smoothing)
        try:
            self.gauge.update_animation(dt)
        except TypeError:
            # backward compatibility: some versions may not accept dt
            self.gauge.update_animation()
        img = self.gauge.draw_integrated_rd1_display()

        # convert to PhotoImage and update existing canvas image
        self.tk_image = ImageTk.PhotoImage(img)
        # update the existing canvas image to avoid creating many items
        try:
            self.canvas.itemconfig(self._canvas_image_id, image=self.tk_image)
        except Exception:
            # fallback: create image if item not present
            self._canvas_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # schedule next frame (~120fps => 8ms)
        # Note: Windows timer resolution and Tkinter scheduling may limit actual FPS.
        self.root.after(8, self._update_loop)

    def _on_close(self):
        self._running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ManualControlApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
