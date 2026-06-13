from pathlib import Path
from lib import plot_comp

if __name__ == '__main__':
    CURR_DIR = Path(__file__).resolve().parent
    SIMU_DIR = CURR_DIR / 'single_brace_simu'
    excel_file = "revise.xlsx"
    OUT_DIR = CURR_DIR / 'single_brace_comp'
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    Test_names = ["Static", "Dynamic", "Fatigue"]
    LINE_Y = 1
    LINE_XS = {"Static": 5, "Dynamic": 2, "Fatigue": 8}
    
    ratchet_mark_row = {"Static": (1, 14), "Dynamic": (49, 64), "Fatigue": (16, 46)}
    slip: float = -1.5
    l_brace, l_ed, d_ed = 5060, 1800, 44

    width, 	height, font_size, 	label_size, linewidth = \
    6, 		4.5, 	8,			8,			0.5

    colors = ['#66ccff', '#ff66cc', '#ccff66']  # 预定义颜色列表

    x_mins =            [-400,  -600,   -800    ]
    x_maxs =            [25,    50,     50      ]
    y_mins =            [0,     0,      0       ]
    y_maxs =            [1000,  1000,   1000    ]
    x_major_locators =  [100,   200,    200     ]
    x_minor_locators =  [25,    50,     50      ]
    y_major_locators =  [200,   200,    200     ]
    y_minor_locators =  [50,    50,     50      ]

    for i, Test_name in enumerate(Test_names):
        simu_path = SIMU_DIR / f'{Test_name}.out'
        pc = plot_comp.plot_comp(simu_path, excel_file, OUT_DIR, 
                                width, height, font_size, label_size, linewidth, 
                                l_brace, l_ed, d_ed, Test_name, LINE_Y, LINE_XS[Test_name],
                                colors)
        pc.plot_comp_ratchet(ratchet_mark_row[Test_name], slip,
                             f'{Test_name}_ratchet.png',
                            x_min=x_mins[i], x_max=x_maxs[i],
                            y_min=y_mins[i], y_max=y_maxs[i],
                            x_major_locator=x_major_locators[i],
                            x_minor_locator=x_minor_locators[i],
                            y_major_locator=y_major_locators[i],
                            y_minor_locator=y_minor_locators[i])
