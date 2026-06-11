from pathlib import Path
from lib import plot_test

if __name__ == "__main__":
	excel_file = "revise.xlsx"
	pic_path = Path(__file__).resolve().parent / "single_brace_test"
	pic_path.mkdir(parents=True, exist_ok=True)

	LINE_Y = 1
	LINE_XS = {"e": 2, "1": 5, "2": 6, "a": 7, "r": 8}

	width, 	height, font_size, 	label_size, linewidth = \
	6, 		4.5, 	8,			8,			0.5
	
	colors = ['#66ccff', '#ff66cc', '#ccff66']  # 预定义颜色列表

	m_static = "1"
	m_fatigue = "r"
	m_dynamic = "e"

	# # Tests
	pt = plot_test.plot_test(excel_file, pic_path, width, height, 
						  	 font_size, label_size, linewidth, colors,
						     LINE_Y, LINE_XS)
	
	Test_names = ["Static", "Dynamic", "Fatigue"]
	pt.plot_sheet(m_static, [Test_names[0]], "Static.4.png",
			   x_min=-120, x_max=120, y_min=-200, y_max=1000, 
               x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40,
			   )
	
	pt.plot_sheet(m_dynamic, [Test_names[1]], "Dynamic.4.png",
			   x_min=-120, x_max=120, y_min=-200, y_max=1000, 
               x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40,
			   )
	
	# 分级 Fatigue
	Fati_names = ["Cycle 1-25", "Cycle 26-30"]
	pt.plot_sheet(m_fatigue, Fati_names, "Fatigue.4.png",
			   x_min=-120, x_max=120, y_min=-200, y_max=1000, 
               x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40,
			   )