from pathlib import Path
from lib import plot_test

if __name__ == "__main__":
	excel_file = "revise.xlsx"
	pic_path = Path(__file__).resolve().parent / "single_brace_test"
	pic_path.mkdir(parents=True, exist_ok=True)
	Test_names = ["Static", "Dynamic", "Fatigue"]
	LINE_Y = 1
	LINE_XS = {"Static": 5, "Dynamic": 2, "Fatigue": 8}

	width, 	height, font_size, 	label_size, linewidth = \
	4.5, 		4.5, 	8,			6,			0.5
	
	# colors = ['#66ccff', '#ff66cc', '#ccff66']  # 预定义颜色列表
	colors = ['#1f77b4', '#b22222', '#1a1a1a']

	# Tests
	for Test_name in Test_names:
		pt = plot_test.plot_test(excel_file, pic_path, width, height, 
						  	 font_size, label_size, linewidth, colors,
						     Test_name, LINE_Y, LINE_XS[Test_name])
	
		pt.plot_sheet(f"{Test_name}.png",
				x_min=-120, x_max=120, y_min=-200, y_max=1000, 
				x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40,
				)
	