from pathlib import Path
from lib import plot_comp


if __name__ == "__main__":
    CURR_DIR = Path(__file__).resolve().parent
    SIMU_DIR = CURR_DIR / 'single_brace_simu'
    excel_file = CURR_DIR / 'revise.xlsx'
    OUT_DIR = CURR_DIR / 'single_brace_comp'

    line_y = 1
    line_xs = {"e": 2, "1": 5, "2": 6, "a": 7, "r": 8}

    width, 	height, font_size, 	label_size, linewidth = \
	6, 		4.5, 	8,			8,			0.5

    l_brace, l_ed, d_ed = 5060, 1800, 44
    
    colors = ['#66ccff', '#ff66cc', '#ccff66']

    m_static = "1"
    m_fatigue = "r"
    m_dynamic = "e"

    pc = plot_comp.plot_comp(SIMU_DIR, excel_file, OUT_DIR, 
                             width, height, font_size, label_size, linewidth, 
                             l_brace, l_ed, d_ed, line_y, line_xs, 
                             colors)
    pc.plot_comp(m_static, "Static", "Static", 
              x_min=-120, x_max=120, y_min=-200, y_max=1000, 
              x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40,
			 )
    # get_value(m_dynamic, "Dynamic", "Dynamic", 
    #           x_min=-120, x_max=120, y_min=-200, y_max=1000, 
    #           x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40,
	# 		 )
    pc.plot_comp(m_fatigue, "Fatigue", "Fatigue", 
              x_min=-120, x_max=120, y_min=-200, y_max=1000, 
              x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40,
			 )