#!/usr/bin/env python3
"""swing_prep.py — 一個指令完成揮桿影片前處理（MediaPipe 骨架追蹤手腕）
用法: python3 swing_prep.py OUT_DIR [--putt|--full] video1 [video2 ...]
      不加參數時自動判斷：手的上下移動很小 → 推桿模式；否則 → 全揮桿模式（木桿／鐵桿）
輸出: OUT_DIR/key_positions.jpg  五個關鍵位置對照圖（每支影片一列）
      OUT_DIR/dense_<name>.jpg    揮桿區間每 0.1 秒一格
      OUT_DIR/swing_metrics.json  桿型模式、各位置時間點、脊椎前傾角（推桿另有節奏與擺幅比）
需要: pip install --break-system-packages mediapipe==0.10.14 opencv-python-headless
"""
import sys, os, json, math
import cv2
import numpy as np
import mediapipe as mp

LABELS = ["Setup", "Top", "Transition", "Impact", "Finish"]
PUTT_LABELS = ["Setup", "Back", "Impact", "Through", "Finish"]
P = mp.solutions.pose.PoseLandmark


def track(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    pose = mp.solutions.pose.Pose(model_complexity=1, min_detection_confidence=0.5)
    L = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        r = pose.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        L.append([(p.x, p.y, p.visibility) for p in r.pose_landmarks.landmark] if r.pose_landmarks else None)
    cap.release()
    return fps, L


def fill(arr):
    arr = np.array(arr, dtype=float)
    ok = ~np.isnan(arr)
    if ok.sum() < 2:
        return arr
    return np.interp(np.arange(len(arr)), np.where(ok)[0], arr[ok])


def smooth(a, k=3):
    return np.convolve(np.pad(a, k // 2, mode="edge"), np.ones(k) / k, mode="valid")


def pt(L, i, lm):
    return np.array(L[i][lm][:2]) if L[i] else None


def spine_tilt(L, i):
    s = (pt(L, i, P.LEFT_SHOULDER) + pt(L, i, P.RIGHT_SHOULDER)) / 2
    h = (pt(L, i, P.LEFT_HIP) + pt(L, i, P.RIGHT_HIP)) / 2
    return round(abs(math.degrees(math.atan2(s[0] - h[0], h[1] - s[1]))))


def detect(fps, L):
    hy = fill([(l[P.LEFT_WRIST][1] + l[P.RIGHT_WRIST][1]) / 2 if l else np.nan for l in L])
    hx = fill([(l[P.LEFT_WRIST][0] + l[P.RIGHT_WRIST][0]) / 2 if l else np.nan for l in L])
    hy, hx = smooth(hy), smooth(hx)
    n = len(hy)
    top = int(np.argmin(hy))                       # 手最高點 = 上桿頂點（先找全片最高）
    # 若最高點其實是收桿，改找它之前、手先回到低點再上去的那一段
    if top > n * 0.6 and hy[:top].size:
        before = hy[:top]
        low_i = int(np.argmax(before))
        if low_i > 0 and np.min(hy[:low_i]) < hy[low_i] - 0.15:
            top = int(np.argmin(hy[:low_i]))
    addr_y = np.median(hy[: max(3, int(0.5 * fps))])
    # 起桿：頂點往回找，手的位置回到站位附近
    start = top
    while start > 0 and (abs(hy[start] - addr_y) > 0.02 or abs(hx[start] - np.median(hx[: max(3, int(0.5 * fps))])) > 0.02):
        start -= 1
    # 擊球：頂點之後，手第一次回到最低點（接近站位高度）
    seg = hy[top:]
    impact = top + int(np.argmax(seg[: max(2, int(1.0 * fps))]))
    # 收桿：擊球後手的最高點，再多 0.2 秒
    fin_seg = hy[impact:]
    finish = min(n - 1, impact + int(np.argmin(fin_seg)) + int(0.2 * fps)) if fin_seg.size else n - 1
    trans = top + (impact - top) // 2
    setup = max(0, start - int(0.1 * fps))
    return [setup, top, trans, impact, finish], start


def body_height(L, i):
    sh = (pt(L, i, P.LEFT_SHOULDER) + pt(L, i, P.RIGHT_SHOULDER)) / 2
    an = (pt(L, i, P.LEFT_ANKLE) + pt(L, i, P.RIGHT_ANKLE)) / 2
    return float(np.linalg.norm(sh - an)) + 1e-9


def hands(L):
    hy = smooth(fill([(l[P.LEFT_WRIST][1] + l[P.RIGHT_WRIST][1]) / 2 if l else np.nan for l in L]))
    hx = smooth(fill([(l[P.LEFT_WRIST][0] + l[P.RIGHT_WRIST][0]) / 2 if l else np.nan for l in L]))
    return hx, hy


def is_putt(L):
    """手的上下移動量 < 身高（肩到腳踝）的 25% → 推桿"""
    hx, hy = hands(L)
    ref = next(i for i, l in enumerate(L) if l)
    return (np.max(hy) - np.min(hy)) / body_height(L, ref) < 0.25


def detect_putt(fps, L):
    """推桿：用手的水平位移（有正負號）找後擺最遠點、擊球（回到站位）、前送最遠點。需正面機位。"""
    hx, hy = hands(L)
    n = len(hx)
    dx = hx - np.median(hx[: max(3, int(0.5 * fps))])
    thr = 0.15 * np.max(np.abs(dx))
    start = int(np.argmax(np.abs(dx) > thr))              # 第一次明顯離開站位 = 開始後擺
    sgn = np.sign(dx[start])
    back = start
    while back + 1 < n and np.sign(dx[back + 1]) == sgn:  # 同一方向走到最遠
        back += 1
    seg = dx[start:back + 1] * sgn
    back = start + int(np.argmax(seg))
    impact = back
    while impact + 1 < n and np.sign(dx[impact]) == sgn:  # 回到站位（位移換號）= 擊球
        impact += 1
    win = -sgn * dx[impact: min(n, impact + int(1.0 * fps))]
    through = impact + int(np.argmax(win))                 # 反方向最遠 = 前送
    finish = min(n - 1, through + int(0.3 * fps))
    setup = max(0, start - int(0.2 * fps))
    while start > 0 and abs(dx[start - 1]) > 0.1 * thr:   # 往回修正真正起動點
        start -= 1
    bh = body_height(L, setup)
    amp_back, amp_thru = abs(dx[back]) / bh, abs(dx[through]) / bh
    extra = {
        "backstroke_s": round((back - start) / fps, 2),
        "forward_to_impact_s": round((impact - back) / fps, 2),
        "tempo_ratio_approx": round((back - start) / max(1, impact - back), 1),
        "through_to_back_ratio": round(float(amp_thru / (amp_back + 1e-9)), 1),
    }
    return [setup, back, impact, through, finish], extra


def metrics(fps, L, idx, labels):
    """只輸出可信的數字：各位置時間點＋脊椎前傾角（只在飛行線後方機位有意義）"""
    m = {"positions_s": dict(zip(labels, [round(i / fps, 2) for i in idx]))}
    try:
        m["spine_tilt_deg"] = {labels[k].lower(): spine_tilt(L, idx[k]) for k in (0, 1, 3 if labels is LABELS else 2)}
    except Exception as e:
        m["metric_error"] = str(e)
    return m


def grab(path, ids, width):
    cap, out = cv2.VideoCapture(path), {}
    for i in sorted(set(ids)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, f = cap.read()
        if ok:
            h, w = f.shape[:2]
            out[i] = cv2.resize(f, (width, int(h * width / w)))
    cap.release()
    return out


def label(img, text):
    cv2.rectangle(img, (0, 0), (17 * len(text) + 20, 40), (168, 90, 30), -1)
    cv2.putText(img, text, (10, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    return img


def grid(tiles, cols=5):
    h = min(t.shape[0] for t in tiles)
    tiles = [t[:h] for t in tiles]
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    return np.vstack([np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)])


def main():
    args = sys.argv[1:]
    force = "putt" if "--putt" in args else "full" if "--full" in args else None
    args = [a for a in args if a not in ("--putt", "--full")]
    out_dir, videos = args[0], args[1:]
    os.makedirs(out_dir, exist_ok=True)
    rows, report = [], {}
    for v in videos:
        name = os.path.splitext(os.path.basename(v))[0]
        fps, L = track(v)
        mode = force or ("putt" if is_putt(L) else "full")
        if mode == "putt":
            idx, extra = detect_putt(fps, L)
            labels = PUTT_LABELS
        else:
            idx, _ = detect(fps, L)
            extra, labels = {}, LABELS
        report[name] = {"fps": round(fps, 1), "stroke_type": mode,
                        "pose_detected_ratio": round(sum(l is not None for l in L) / len(L), 2),
                        **metrics(fps, L, idx, labels), **extra}
        fr = grab(v, idx, 360)
        rows.append(grid([label(fr[i].copy(), l) for i, l in zip(idx, labels)]))
        step = max(1, round(fps * 0.1))
        ids = list(range(idx[0], idx[4] + 1, step))[:30]
        fd = grab(v, ids, 300)
        cv2.imwrite(os.path.join(out_dir, f"dense_{name}.jpg"),
                    grid([label(fd[i].copy(), f"{i / fps:.1f}s") for i in ids if i in fd]),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
    w = min(r.shape[1] for r in rows)
    cv2.imwrite(os.path.join(out_dir, "key_positions.jpg"), np.vstack([r[:, :w] for r in rows]),
                [cv2.IMWRITE_JPEG_QUALITY, 88])
    with open(os.path.join(out_dir, "swing_metrics.json"), "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
