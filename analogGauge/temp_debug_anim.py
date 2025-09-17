import time
from rd1_gauge import RD1Gauge

print('Creating gauge with reset_on_start=True')
g = RD1Gauge(reset_on_start=True)

start = time.time()
# step until all animations finish or timeout
timeout = 5.0
while True:
    now = time.time()
    dt = 1/60.0
    g.update_animation(dt)
    vals = {k: round(v, 3) for k, v in g.animation_values.items()}
    print(f"t={round(now-start,3)}s vals={vals}")
    if all(g._anim_start_time[k] is None for k in g._anim_start_time):
        print('All animations finished')
        break
    if now - start > timeout:
        print('Timeout reached')
        break
    time.sleep(1/60.0)

print('Final values:', {k: v for k,v in g.animation_values.items()})
