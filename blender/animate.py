# robo_master.blend: writes one Action per game move (names = what the web app expects). Re-runnable.
# Angles in degrees about rest-space world axes. Robot faces -Y, its left (.L) is +X.
#   rot X+ = lean forward, rot Y+ = tip toward +X, rot Z = turn. arm "out" = raise sideways, "fwd" = raise forward.
import bpy, math
from mathutils import Euler, Vector, Quaternion
D = bpy.data
rig = D.objects["rig_bot"]; P = rig.pose.bones
FPS = 24
sin, cos, pi, exp = math.sin, math.cos, math.pi, math.exp
def S(u, n=1, ph=0): return sin(2 * pi * n * u + ph)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def bump(u, a, b): return sin(pi * (u - a) / (b - a)) if a <= u <= b else 0.0
def damp(u, f, k): return exp(-k * u) * sin(2 * pi * f * u)

# ---- clips: name -> (frames, loop, pose(u) -> dict) ----
def idle(u):
    s = S(u)
    return dict(scale=(1 + .01 * s, 1 + .01 * s, 1 + .025 * s), head=(2 * S(u, 1, 1), 3 * s, 4 * S(u, 1, 2)),
                armL=(6 + 2 * s, 0), armR=(6 + 2 * s, 0), elbowL=8, elbowR=8)
def head_poke(u):
    w, q = damp(u, 3, 5), bump(u, 0, .25)
    return dict(head=(10 * w, 15 * w, 0), scale=(1 + .05 * q, 1 + .05 * q, 1 - .1 * q), armL=(6 + 30 * q, 0), armR=(6 + 30 * q, 0))
def belly_poke(u):
    q, g = bump(u, 0, .2), (1 - u) * (u > .15)
    return dict(scale=(1 + .07 * q, 1 + .07 * q, 1 - .15 * q), rot=(5 * S(u, 2) * g, 5 * S(u, 6, 1) * g, 8 * S(u, 6) * g),
                armL=(15, 55 * (1 - u)), armR=(15, 55 * (1 - u)), elbowL=95 * (1 - u), elbowR=95 * (1 - u))
def hop(u, h=.18, arms=40):
    j = bump(u, .15, .85); q = bump(u, 0, .15) + bump(u, .85, 1)
    return dict(loc=(0, 0, h * j), scale=(1 + .06 * q - .03 * j, 1 + .06 * q - .03 * j, 1 - .12 * q + .06 * j),
                armL=(6 + arms * j, 0), armR=(6 + arms * j, 0))
ROCKET_H = .9  # cruising height: about half way up the web app's view (the loop around the room is done in index.html)
def rocket_launch(u):  # crouch, ignite, rise and level off at cruising height
    q = bump(u, 0, .4); up = max(0.0, (u - .35) / .65)
    return dict(loc=(0, 0, ROCKET_H * (1 - (1 - up) ** 2)), scale=(1 + .08 * q, 1 + .08 * q, 1 - .15 * q),
                head=(10 * q - 6 * (up > 0), 0, 0), armL=(6 - 4 * min(up * 5, 1), 0), armR=(6 - 4 * min(up * 5, 1), 0))
def rocket_fly(u):  # loop: cruising, leaning into the flight like a superhero, arms swept back, slight bob
    s = S(u)
    return dict(loc=(0, 0, ROCKET_H + .03 * s), rot=(22 + 3 * S(u, 2), 0, 0), head=(-14, 0, 0),
                armL=(12, -35 + 5 * s), armR=(12, -35 - 5 * s))
def rocket_land(u):  # come down slowing like a lander, squash on touchdown, wobble
    d = min(u / .6, 1.0); q = bump(u, .58, .8)
    return dict(loc=(0, 0, ROCKET_H * (1 - d) ** 2 + .04 * bump(u, .8, .95)), scale=(1 + .08 * q, 1 + .08 * q, 1 - .15 * q),
                rot=(0, 4 * damp(max(u - .6, 0), 3, 6), 0), armL=(6 + 25 * (1 - d), 0), armR=(6 + 25 * (1 - d), 0))
def head_wobble(u):  # little dizzy after the head is swiped: head circles, fading out
    a, k = 2 * pi * 2.5 * u, (1 - u) ** 1.5
    return dict(head=(9 * sin(a) * k, 12 * cos(a) * k, 6 * sin(a / 2) * k), rot=(0, 3 * sin(a + 1) * k, 0),
                armL=(6 + 12 * k, 0), armR=(6 + 12 * k, 0))
def dizzy(u):
    a = 2 * pi * 2 * u
    return dict(rot=(8 * sin(a), 8 * cos(a), 0), head=(-10 * sin(a + .8), -10 * cos(a + .8), 15 * S(u)),
                armL=(30 + 10 * sin(a), 0), armR=(30 - 10 * sin(a), 0))
LIE = 85
def lying(th, kind="side"):
    ax, lift = {"side": ((0, 1, 0), .135), "back": ((-1, 0, 0), .16), "front": ((1, 0, 0), .16)}[kind]
    d = dict(rot=tuple(a * th for a in ax), loc=(0, 0, lift * sin(math.radians(th))))
    if kind == "side": d.update(armL=(6, 0), armR=(6 + .9 * th, 0), head=(0, .12 * th, 0))   # down-side arm tucked
    elif kind == "back": d.update(armL=(6 + .7 * th, 0), armR=(6 + .7 * th, 0), head=(-.15 * th, 0, 0))
    else: d.update(armL=(6 + .8 * th, 0), armR=(6 + .8 * th, 0), head=(-.2 * th, 0, 0))     # faceplant, head lifted
    return d
def fall(u, kind="side"): return lying(LIE * ease(u / .6) ** 1.5 - 6 * damp(max(u - .6, 0), 3, 8) * (u > .6), kind)
def get_up(u, kind="side"): return lying(LIE * (1 - ease(u / .7)) - 8 * damp(max(u - .7, 0) * 1.5, 2, 6) * (u > .7), kind)
def apart(th, s, e, b=0.0):
    # lying on back; s: head flight 0..1 (ballistic arc + spin), e: arms slide-off 0..1, b: head landing bounce
    d = lying(th, "back")
    if s > 0:
        d["head_w"] = (.22 * s, .3 * s, 1.4 * s * (1 - s) - .1 * s + .04 * b)
        h = d["head"]; d["head"] = (h[0] + 120 * s, h[1], h[2] + 200 * s)
    if e > 0: d["armL_w"], d["armR_w"] = (.15 * e, .05 * e, -.04 * e), (-.15 * e, .05 * e, -.04 * e)
    return d
def fall_apart(u):
    th = LIE * ease(u / .35) ** 1.5
    return apart(th, ease((u - .35) / .4) if u > .35 else 0, ease((u - .35) / .3) if u > .35 else 0, bump(u, .75, .9))
def reassemble(u):
    if u < .5: s = 1 - ease(u / .5); return apart(LIE, s, s)
    return get_up((u - .5) / .5, "back")
def fart(u):
    sq = ease(u / .3) * (u < .3) + (1 - ease((u - .3) / .1)) * (.3 <= u < .4)
    p = bump(u, .3, .5)
    return dict(scale=(1 + .08 * sq, 1 + .08 * sq, 1 - .15 * sq), loc=(0, -.04 * p, .08 * p),
                rot=(12 * damp(max(u - .3, 0), 2, 5) * (u > .3), 0, 0), armL=(6 + 50 * p, 0), armR=(6 + 50 * p, 0), head=(-8 * p, 0, 0))
def sneeze(u):
    b = ease(u / .55) if u < .55 else 0
    s = damp(u - .55, 1.5, 6) if u >= .55 else 0
    return dict(head=(-20 * b + 30 * s, 0, 0), rot=(-8 * b + 14 * s, 0, 0), armL=(6 + 15 * b, 10 * b), armR=(6 + 15 * b, 10 * b))
def eat(u):
    e = bump(u, 0, 1) ** .5
    return dict(rot=(10 * e, 0, 0), head=(10 * abs(S(u, 3)) * e, 0, 0), armL=(10, 40 * e), armR=(10, 40 * e), elbowL=70 * e, elbowR=70 * e)
def drink(u):  # right hand (holding the cup in the web app) to the mouth, head back, three gulps
    up = ease(u / .25) * (1 - ease((u - .8) / .2))
    gulp = sin(2 * pi * 3 * max(u - .3, 0) / .5) * (.3 < u < .8)
    return dict(armR=(DRINK['out'] * up, DRINK['fwd'] * up), elbowR=DRINK['elbow'] * up, swingR=DRINK['swing'] * up, curlR=.45 * up, twistR=DRINK['twist'] * up,
                head=((-18 + 4 * gulp) * up, 0, 0), rot=(-5 * up, 0, 0), armL=(6 + 8 * up, 0))
DRINK = dict(out=30, fwd=150, elbow=0, swing=-30, twist=.5)  # from blender/drink_check.py: hand at the mouth, palm sideways, thumb up
def hug(u):  # teddy held against the chest (placed by index.html), arms wrapped round it, swaying with love
    e = ease(u / .2) * (1 - ease((u - .85) / .15)); s = S(u, 2)
    return dict(armL=(10 * e, 65 * e), armR=(10 * e, 65 * e), elbowL=55 * e, elbowR=55 * e, swingL=-35 * e, swingR=-35 * e,
                rot=(4 * e, 7 * s * e, 0), head=(6 * e, 10 * s * e, 0))
def read(u):  # book held open in front of the chest (placed by index.html), looking down at it, nodding along
    e = ease(u / .2) * (1 - ease((u - .85) / .15))
    return dict(armL=(12 * e, 50 * e), armR=(12 * e, 50 * e), elbowL=75 * e, elbowR=75 * e, swingL=-20 * e, swingR=-20 * e,
                head=((18 + 5 * abs(S(u, 3))) * e, 4 * S(u, 1) * e, 0))
def dance_wiggle(u):
    s = S(u)
    return dict(rot=(0, 12 * s, 4 * S(u, 2)), loc=(.03 * s, 0, .02 * abs(s)), head=(0, -8 * s, 0),
                armL=(40 + 40 * s, 0), armR=(40 - 40 * s, 0), elbowL=60, elbowR=60)
def dance_spin(u):
    return dict(rot=(0, 0, 360 * ease(u)), loc=(0, 0, .05 * bump(u, 0, 1)), armL=(80 * bump(u, 0, 1), 0), armR=(80 * bump(u, 0, 1), 0))
def dance_jump(u):
    d = hop(u, .15, 150); return d
def sleep(u):
    s = S(u)
    return dict(rot=(6, 0, 0), head=(25 + 2 * s, 8, 0), scale=(1 + .015 * s, 1 + .015 * s, 1 + .03 * s), armL=(3, 0), armR=(3, 0))
def fly(u):
    s = S(u)
    return dict(loc=(0, 0, .35 + .04 * s), rot=(12 + 3 * S(u, 1, 1), 3 * S(u, 1, 2), 0), armL=(25, -30 + 5 * s), armR=(25, -30 - 5 * s))
def wave(u):
    up = ease(u / .2) * (1 - ease((u - .85) / .15))
    return dict(armL=(6 + 95 * up, 15 * up), swingL=(35 + 20 * S(u, 3)) * up, elbowL=25 * up, twistL=up, head=(0, 6 * S(u, 1), 0))
def thumbs_up(u):
    e = ease(u / .3); p = 6 * bump(u, .5, .75)
    return dict(armR=(70 * e, 10 * e + p), swingR=100 * e, twistR=e, curlR=e, thumbR=(20 * e, 0, 70 * e), head=(0, -6 * e, 0))

CLIPS = {"Idle": (48, True, idle), "HeadPoke": (24, False, head_poke), "BellyPoke": (36, False, belly_poke),
         "FootPoke": (24, False, hop), "Dizzy": (48, True, dizzy), "HeadWobble": (36, False, head_wobble),
         "RocketLaunch": (48, False, rocket_launch), "RocketFly": (24, True, rocket_fly), "RocketLand": (40, False, rocket_land), "Fall": (30, False, fall), "GetUp": (30, False, get_up),
         "FallBack": (30, False, lambda u: fall(u, "back")), "GetUpBack": (30, False, lambda u: get_up(u, "back")),
         "FallFront": (30, False, lambda u: fall(u, "front")), "GetUpFront": (30, False, lambda u: get_up(u, "front")),
         "FallApart": (48, False, fall_apart), "Reassemble": (48, False, reassemble),
         "Fart": (36, False, fart), "Sneeze": (36, False, sneeze), "Eat": (48, False, eat), "Drink": (56, False, drink), "Hug": (72, False, hug), "Read": (80, False, read),
         "DanceWiggle": (24, True, dance_wiggle), "DanceSpin": (36, False, dance_spin), "DanceJump": (24, True, dance_jump),
         "Sleep": (72, True, sleep), "Fly": (48, True, fly), "Wave": (48, False, wave), "ThumbsUp": (36, False, thumbs_up)}

# ---- apply ----
def q_world(bone, rx, ry, rz):
    r = bone.bone.matrix_local.to_quaternion()
    return r.inverted() @ Euler([math.radians(a) for a in (rx, ry, rz)]).to_quaternion() @ r
def v_local(bone, v): return bone.bone.matrix_local.to_3x3().inverted() @ Vector(v)
def scale_local(bone, s):
    m = bone.bone.matrix_local.to_3x3()
    return [s[max(range(3), key=lambda w: abs(m[w][i]))] for i in range(3)]
FINGERS = tuple(f"{f}.{k}" for f in ("f_index", "f_middle", "f_pinky") for k in ("01", "02", "03")) + ("thumb.01_master",)
KEYED = ["Body", "Head", "Antenna_Spring"] + [f"{b}.{s}" for s in "LR" for b in ("upper_arm_fk", "forearm_fk") + FINGERS]
def detach(bone, w, q_body):  # world-space offset for a part that came off the (rotated) body
    P[bone].location = v_local(P[bone], q_body.inverted() @ Vector(w))

def apply(d, ant):
    sgn = {"L": -1, "R": 1}
    for b in KEYED: P[b].location = (0, 0, 0); P[b].rotation_quaternion = (1, 0, 0, 0); P[b].scale = (1, 1, 1)
    P["Body"].rotation_quaternion = q_world(P["Body"], *d.get("rot", (0, 0, 0)))
    P["Body"].location = v_local(P["Body"], d.get("loc", (0, 0, 0)))
    P["Body"].scale = scale_local(P["Body"], d.get("scale", (1, 1, 1)))
    P["Head"].rotation_quaternion = q_world(P["Head"], *d.get("head", (0, 0, 0)))
    qb = Euler([math.radians(a) for a in d.get("rot", (0, 0, 0))]).to_quaternion()
    if "head_w" in d: detach("Head", d["head_w"], qb)
    for s in "LR":
        if f"arm{s}_w" in d: detach(f"upper_arm_fk.{s}", d[f"arm{s}_w"], qb)
    P["Antenna_Spring"].rotation_quaternion = q_world(P["Antenna_Spring"], ant[0], ant[1], 0)
    for s in "LR":
        out, fwd = d.get("arm" + s, (6, 0))
        P[f"upper_arm_fk.{s}"].rotation_quaternion = q_world(P[f"upper_arm_fk.{s}"], -fwd, sgn[s] * out, 0)
        # twist: palm toward camera at +1 (L and R mirror); curl: fist at 1; thumb: master euler (local) in degrees
        P[f"forearm_fk.{s}"].rotation_quaternion = (q_world(P[f"forearm_fk.{s}"], -d.get("elbow" + s, 0), sgn[s] * d.get("swing" + s, 0), 0)
                                                    @ Quaternion((0, 1, 0), math.radians(sgn[s] * 90 * d.get("twist" + s, 0))))
        for f in FINGERS[:-1]: P[f"{f}.{s}"].rotation_quaternion = Euler((math.radians(85 * d.get("curl" + s, 0)), 0, 0)).to_quaternion()
        P[f"thumb.01_master.{s}"].rotation_quaternion = Euler([math.radians(a) for a in d.get("thumb" + s, (0, 0, 0))]).to_quaternion()

def antenna_track(n, loop, pose):
    # damped spring: antenna (in world) lags behind the head's tilt; output = lag in head space, exaggerated
    def tilt(i):
        d = pose(i / n); r = d.get("rot", (0, 0, 0)); h = d.get("head", (0, 0, 0)); l = d.get("loc", (0, 0, 0))
        return [r[0] + h[0] - 0 * l[1], r[1] + h[1]], l
    w0, z, sub, dt = 2 * pi * 3, .15, 8, 1 / FPS
    phi, vel, out = [0.0, 0.0], [0.0, 0.0], []
    for rep in range(2 if loop else 1):
        out = []
        for i in range(n + 1):
            (tx, ty), l = tilt(i)
            _, lp = tilt(max(i - 1, 0)); _, lpp = tilt(max(i - 2, 0))
            ax = (l[0] - 2 * lp[0] + lpp[0]) / dt ** 2; az = (l[2] - 2 * lp[2] + lpp[2]) / dt ** 2
            tgt = [tx - 2 * az, ty - 25 * ax]          # sideways/vertical acceleration kicks the antenna
            for _ in range(sub):
                for k in (0, 1):
                    vel[k] += (w0 ** 2 * (tgt[k] - phi[k]) - 2 * z * w0 * vel[k]) * dt / sub
                    phi[k] += vel[k] * dt / sub
            out.append([1.5 * (phi[k] - (tx, ty)[k]) for k in (0, 1)])
    return out

# fresh start: drop pack's pose-library actions and any previous run
rig.animation_data_create(); rig.animation_data.action = None
for t in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(t)
for a in list(D.actions): D.actions.remove(a)
for s in "LR": P[f"upper_arm_parent.{s}"]["IK_FK"] = 1.0   # Rigify: 1 = FK
for pb in P:  # clear leftover pack poses on bones we don't key
    pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
for b in KEYED: P[b].rotation_mode = 'QUATERNION'
bpy.context.scene.render.fps = FPS

for name, (n, loop, pose) in CLIPS.items():
    act = D.actions.new(name); act.use_fake_user = True
    rig.animation_data.action = act
    ant = antenna_track(n, loop, pose)
    for i in range(n + 1):
        apply(pose(i / n), ant[i])
        for b in KEYED:
            for path in ("location", "rotation_quaternion", "scale"): P[b].keyframe_insert(path, frame=i + 1, group=b)
    act["loop"] = loop
    print("ACTION", name, n + 1, "frames")
rig.animation_data.action = D.actions["Idle"]
bpy.ops.wm.save_mainfile()
