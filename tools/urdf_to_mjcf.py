from pathlib import Path
import sys
import mujoco

src = Path(sys.argv[1]).resolve()
dst = Path(sys.argv[2]).resolve()

spec = mujoco.MjSpec.from_file(str(src))
spec.compile()

dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(spec.to_xml(), encoding="utf-8")

print(f"Saved MJCF to: {dst}")