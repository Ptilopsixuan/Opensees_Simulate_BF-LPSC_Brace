from lib import plot_test
from pathlib import Path


if __name__ == '__main__':
    excel_file = "revise.xlsx"
    pic_path = Path(__file__).resolve().parent / "single_brace_ratchet"
    pic_path.mkdir(parents=True, exist_ok=True)

    Test_names = ["Static", "Dynamic", "Fatigue"]
    LINE_Y = 1
    LINE_XS = {"Static": 5, "Dynamic": 2, "Fatigue": 8}
    H_len = [-365, -500, -724] # "Static", "Dynamic", "Fatigue"
    D_len = [-350, -469, -715] # "Static", "Dynamic", "Fatigue"
    ratchet_mark_row = {"Static": (1, 14), "Dynamic": (49, 64), "Fatigue": (16, 46)}
    slip: float = -2

    width, 	height, font_size, 	label_size, linewidth = \
    4.5, 		4.5, 	8,			6,			0.5

    colors = ['#66ccff', '#ff66cc', '#ccff66']  # 预定义颜色列表
    colors = ['#1f77b4', '#b22222', '#1a1a1a']

    x_mins =            [-400,  -600,   -800    ]
    x_maxs =            [25,    50,     50      ]
    y_mins =            [0,     0,      0       ]
    y_maxs =            [1000,  1000,   1000    ]
    x_major_locators =  [100,   200,    200     ]
    x_minor_locators =  [25,    50,     50      ]
    y_major_locators =  [200,   200,    200     ]
    y_minor_locators =  [50,    50,     50      ]

    for i, Test_name in enumerate(Test_names):
        pt = plot_test.plot_test(excel_file, pic_path, width, height, 
                                font_size, label_size, linewidth, colors,
                                f'{Test_name}', LINE_Y, LINE_XS[Test_name])
        pt.plot_ratchet(ratchet_mark_row[Test_name], slip,
                        f'{Test_name}.png', H_len[i], D_len[i],
                        x_min=x_mins[i], x_max=x_maxs[i],
                        y_min=y_mins[i], y_max=y_maxs[i],
                        x_major_locator=x_major_locators[i],
                        x_minor_locator=x_minor_locators[i],
                        y_major_locator=y_major_locators[i],
                        y_minor_locator=y_minor_locators[i])
        