# Off-axis projection demo (Python) with pyray + rlgl
# - Define a screen plane (3 corners) and an eye.
# - Build an off-axis projection and view aligned to that plane.
# - Feed matrices to rlgl and draw a simple scene.
#
# Controls:
#   Arrow keys: move eye in X/Z
#   PageUp/PageDown: move eye in Y
import math
import pyray as pr
import pyray as rlgl
import find_eyes

def make_off_axis_pv(pa, pb, pc, pe, n, f):
    # Screen basis
    vr = pr.vector3_normalize(pr.vector3_subtract(pb, pa))                  # right
    vu = pr.vector3_normalize(pr.vector3_subtract(pc, pa))                  # up
    vn = pr.vector3_normalize(pr.vector3_cross_product(vr, vu))             # normal
    # Distance from eye to screen plane
    d = -pr.vector3_dot_product(vn, pr.vector3_subtract(pa, pe))
    if d <= 0.0:
        return None, None, False  # wrong winding or eye behind screen plane
    # Frustum bounds on the near plane
    l = pr.vector3_dot_product(vr, pr.vector3_subtract(pa, pe)) * n / d
    r = pr.vector3_dot_product(vr, pr.vector3_subtract(pb, pe)) * n / d
    b = pr.vector3_dot_product(vu, pr.vector3_subtract(pa, pe)) * n / d
    t = pr.vector3_dot_product(vu, pr.vector3_subtract(pc, pe)) * n / d
    # Projection matrix (OpenGL-style NDC z in [-1, 1], matches raylib default)
    P = pr.matrix_frustum(l, r, b, t, n, f)
    # View matrix: look from eye toward -vn (so camera looks along -Z), with up = vu
    target = pr.vector3_add(pe, pr.vector3_scale(vn, -1.0))
    V = pr.matrix_look_at(pe, target, vu)
    return P, V, True



def main():
    screen_width, screen_height = 1280, 720
    pr.init_window(screen_width, screen_height, "pyray + rlgl off-axis projection")
    pr.set_target_fps(60)
    pr.toggle_fullscreen()
    # Define a physical screen in world space
    screen_w = 1.2
    screen_h = 0.7
    screen_center = pr.Vector3(0.0, 1.0, 0.0)
    # Tilt around X (pitch) and Y (yaw)
    euler = pr.Vector3(math.radians(0.0), math.radians(0.0), 0.0)
    screen_rot = pr.matrix_rotate_xyz(euler)
    # Extract right, up, normal from rotation matrix columns
    s_right = pr.Vector3(screen_rot.m0, screen_rot.m1, screen_rot.m2)
    s_up    = pr.Vector3(screen_rot.m4, screen_rot.m5, screen_rot.m6)
    s_norm  = pr.Vector3(screen_rot.m8, screen_rot.m9, screen_rot.m10)  # points out of screen
    # Screen corners (counterclockwise as seen by the viewer): pa=LL, pb=LR, pc=UL
    pa = pr.vector3_subtract(
        pr.vector3_subtract(screen_center, pr.vector3_scale(s_right, screen_w*0.5)),
        pr.vector3_scale(s_up, screen_h*0.5)
    )
    pb = pr.vector3_add(
        pr.vector3_subtract(screen_center, pr.vector3_scale(s_up, screen_h*0.5)),
        pr.vector3_scale(s_right, screen_w*0.5)
    )
    pc = pr.vector3_add(
        pr.vector3_subtract(screen_center, pr.vector3_scale(s_right, screen_w*0.5)),
        pr.vector3_scale(s_up, screen_h*0.5)
    )
    # Eye position in front of the screen
    pe = pr.vector3_add(screen_center, pr.vector3_scale(s_norm, 0.8))
    pe.x += 0.2
    print(pe.z)
    n, f = 0.05, 100.0
    # Dummy camera for BeginMode3D (we will override matrices via rlgl)
    cam = pr.Camera3D()
    webcam = find_eyes.setup_capture_device()
    
    while not pr.window_should_close():
        # get coords from webcam
        coords = find_eyes.target_position(webcam)
        if(coords): pe.x = (-coords[0]) + 0.6
        if(coords): pe.y = (-coords[1]) + 1.2
        if(coords):
            pe.z = (1 / coords[2]) 
        # Build off-axis matrices
        P, V, ok = make_off_axis_pv(pa, pb, pc, pe, n, f)
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(cam)
        if ok:
            # Flush before changing matrices
            rlgl.rl_draw_render_batch_active()
            rlgl.rl_set_matrix_projection(P)
            rlgl.rl_set_matrix_modelview(V)
        # Draw scene
        pr.draw_cube(pr.Vector3(0.0, 1.0, -2.0), 0.5, 0.5, 0.5, pr.BLUE)
        pr.draw_grid(20, 1.0)
        pr.draw_cube_wires(pr.Vector3(0.0, 1.0, -2.0), 0.5,0.5, 0.5, pr.DARKBLUE)
        pr.end_mode_3d()
        pr.draw_text("Off-axis projection onto tilted screen plane (pyray + rlgl)", 10, 10, 18, pr.DARKGRAY)
        pr.draw_text("Projection OK" if ok else "Eye behind screen or bad winding!", 10, 34, 18, pr.DARKGREEN if ok else pr.RED)
        pr.end_drawing()
    pr.close_window()
if __name__ == "__main__":
    main()
