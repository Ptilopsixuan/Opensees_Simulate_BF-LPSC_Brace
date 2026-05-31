# LLPSCB OpenSees Simulations

这个仓库包含基于 OpenSeesPy 的 LLPSCB 构件级测试工具（两节点支撑件）。代码以 Python 脚本组织，支持静态、疲劳和瞬态（dynamic）分步加载并输出 recorder 文件与绘图。

主要文件与目录

- `single_brace_simu.py`: 主运行脚本，构建模型、注册材料/单元、设置分析并按协议运行静态 / 疲劳 / 瞬态测试，输出结果到 `single_brace_simu/<test>.out`。
- `lib/`
  - `material.py`: 材料类（`Material`, `StainlessSteel` 等）。
  - `brace.py`: `Brace` 与 `LLPSCB` 类，包含 `build_in_opensees()` 注册单元/材料与 recorder。
  - `opensees_setter.py`: `ModelSetter`，用于初始化模型与设置分析（静态/动态分支）。构造时可传入 `dt`（默认时间增量），并通过 `set_analysis(test_type)` 配置 `Static` 或 `Transient` 分析。
  - `plot_brace.py`: 读取 recorder 输出并生成图片的类 `plot_brace_results`（替代早期独立脚本 `analyze_brace_results.py`）。
  - `pic_setter.py`: 绘图样式与公用设置函数 `pic_setting`。

快速开始

1. 安装依赖：

```bash
pip install openseespy numpy matplotlib
```

2. 运行示例：

```bash
python single_brace_simu.py
```

默认会运行 `single_brace_simu.py` 中配置的测试协议（`static`, `fatigue`, `dynamic` 可在脚本中切换），并把输出写入 `single_brace_simu/<test>.out`，同时生成 PNG 绘图文件。

重要用法提示

- 在构造 `ModelSetter` 时可以指定时间步长 `dt`（例如 `ModelSetter(dt=0.01)`），这对瞬态（dynamic）分析的稳定性很重要。脚本默认已将 `dt` 与协议步长设置为较小值以提高收敛性。
- 使用 `ModelSetter.set_disp_protocol(protocol, step_len)` 可以把高层位移协议映射为每段的步数与单步位移。返回值 `(numIter, du)`：`numIter` 为每段的分析增量数，`du` 为对应的每步位移（可能为负以表示方向）。
- 若瞬态分析在某些时间步出现收敛失败，脚本包含子步细分重试机制；也可在 `lib/opensees_setter.py` 中调整收敛判据（`ops.test`）、迭代次数或算法（`ops.algorithm`）。

输出位置

- 结果和绘图位于 `single_brace_simu/<test>.out`，常见文件包括 `BraceTest2Disp.out`, `BraceTest2Force.out` 等，以及 `Brace_Force_Displacement.png` 等图像。

故障排查

- 如果 OpenSees 报 `OpenSeesError` 指出某些 uniaxial material 未识别，请确认你所使用的 OpenSees 构建是否包含 `Ratchet`, `ReinforcingSteel`, `ElasticMultiLinear` 等扩展材料（这些材料并非所有 OpenSees 构建都支持）。
- 若瞬态频繁不收敛：尝试减小 `step_len`（protocol 的步长），减小 `dt`，或在 `opensees_setter.py` 中适当放宽收敛容差／增大最大迭代次数。

许可证: MIT
