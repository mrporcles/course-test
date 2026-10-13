"""Worked examples: python3 example.py <outdir>   (renders 3 sample images)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spring_theme import *

out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)

# 1. Box-and-arrow diagram
render(diagram(1000, 330,
    box("Transfer<br>Service", 130, 0, 246, 120, "primary") +
    box("Transfer<br>Repository", 500, 0, 246, 120, "dark") +
    box("Account<br>Repository", 130, 210, 246, 120, "dark"),
    line(10, 60, 128, 60) + line(376, 60, 498, 60) + line(252, 120, 252, 208)), f"{out}/example-diagram.png")

# 2. Code card with highlighted term + callout + arrow
src = """public class TransferServiceImpl implements TransferService {
    public TransferServiceImpl([[AccountRepository ar]]) {
        this.accountRepository = ar;
    }
}"""
render(code(src, [("Dependency: needed to perform<br>money transfers", X(34), Y(2) + 30, 370)],
            [(X(34) + 60, Y(2) + 30, X(37), Y(1) + LH + 3)])
       + note("You do not have to use <i>interfaces</i>, but it is good practice."), f"{out}/example-code.png")

# 3. Bullet list
render(bullets("Spring separates configuration from application objects",
               ("Spring manages your objects", ["Creating them in dependency order", "Fully initializing them before use"])),
       f"{out}/example-bullets.png")
