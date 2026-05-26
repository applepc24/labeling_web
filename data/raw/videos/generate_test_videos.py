"""테스트용 합성 영상 생성 스크립트 (T-11)
실행: python data/raw/videos/generate_test_videos.py
"""
import cv2
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent
FPS = 15
DURATION_SEC = 5
W, H = 640, 480


def _rand_color():
    return tuple(int(x) for x in np.random.randint(50, 230, 3))


def make_video(name: str, num_objects: int = 3) -> Path:
    out_path = OUTPUT_DIR / name
    writer = cv2.VideoWriter(
        str(out_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (W, H),
    )

    rng = np.random.default_rng(seed=hash(name) % 2**32)
    # 각 오브젝트: [x, y, dx, dy, w, h, color]
    objects = []
    for _ in range(num_objects):
        ow, oh = rng.integers(40, 120), rng.integers(40, 100)
        x = int(rng.integers(0, W - ow))
        y = int(rng.integers(0, H - oh))
        dx = int(rng.integers(2, 6)) * rng.choice([-1, 1])
        dy = int(rng.integers(2, 5)) * rng.choice([-1, 1])
        color = tuple(int(v) for v in rng.integers(60, 220, 3))
        objects.append([x, y, dx, dy, ow, oh, color])

    for _ in range(FPS * DURATION_SEC):
        frame = np.full((H, W, 3), 30, dtype=np.uint8)

        for obj in objects:
            x, y, dx, dy, ow, oh, color = obj
            cv2.rectangle(frame, (x, y), (x + ow, y + oh), color, -1)
            # 벽 바운스
            if x + dx < 0 or x + ow + dx > W:
                obj[2] *= -1
            if y + dy < 0 or y + oh + dy > H:
                obj[3] *= -1
            obj[0] += obj[2]
            obj[1] += obj[3]

        writer.write(frame)

    writer.release()
    print(f"생성 완료: {out_path} ({FPS * DURATION_SEC}프레임)")
    return out_path


if __name__ == "__main__":
    make_video("test_sample_01.mp4", num_objects=3)
    make_video("test_sample_02.mp4", num_objects=5)
    make_video("test_sample_03.mp4", num_objects=2)
    print("테스트 영상 3개 생성 완료.")
