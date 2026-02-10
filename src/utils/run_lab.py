from pathlib import Path
from utils import analyze_text_file

result_1 = analyze_text_file(Path("text/transcript.txt"))
print('SOURCE', result_1)

result_2 = analyze_text_file(Path("text/summary.txt"))
print('SUMMARY', result_2)
