from pathlib import Path
from lib import plot_comp


if __name__ == "__main__":
    CURR_DIR = Path(__file__).resolve().parent
    SIMU_DIR = CURR_DIR / 'single_brace_simu'
    excel_file = CURR_DIR / 'revise.xlsx'
    OUT_DIR = CURR_DIR / 'single_brace_comp'
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    Test_names = ["Static", "Dynamic", "Fatigue"]
    LINE_Y = 1
    LINE_XS = {"Static": 5, "Dynamic": 2, "Fatigue": 8}

    width, 	height, font_size, 	label_size, linewidth = \
	6, 		4.5, 	8,			8,			0.5

    l_brace, l_ed, d_ed = 5060, 1800, 44
    
    colors = ['#66ccff', '#ff66cc', '#ccff66']
    
    for Test_name in Test_names: 
        simu_path = SIMU_DIR / f'{Test_name}.out'
        pc = plot_comp.plot_comp(simu_path, excel_file, OUT_DIR, 
                                width, height, font_size, label_size, linewidth, 
                                l_brace, l_ed, d_ed, Test_name, LINE_Y, LINE_XS[Test_name],
                                colors)
        pc.plot_comp_brace(Test_name, 
                x_min=-120, x_max=120, y_min=-200, y_max=1000, 
                x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40,
                )