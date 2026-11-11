"""原生 Windows EXE 离线冒烟；仅控制本脚本启动的 --sim 进程。

测试辅助依赖 pywinauto/psutil 不属于生产运行依赖。需交互式桌面。
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import psutil
from pywinauto import Desktop
import win32con
import win32gui


def wait_for(function, timeout=25):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = function()
        if value:
            return value
        time.sleep(.2)
    raise TimeoutError('等待原生窗口/控件超时')


def check(exe, folder, title=None, workbench=False):
    expected = title or '宇树s288舵机microduck关节运动上位机'
    process = subprocess.Popen([str(exe), '--sim'] + (['--title', title] if title else []), cwd=exe.parent)
    root = psutil.Process(process.pid)
    owned = {process.pid: root.create_time()}
    desktop = Desktop(backend='uia')
    record = dict(expected_title=expected, process_id=process.pid, sim=True)

    def windows():
        try:
            for child in root.children(recursive=True):
                owned[child.pid] = child.create_time()
        except psutil.NoSuchProcess:
            pass
        top = [window for window in desktop.windows() if window.process_id() in owned]
        nested = [child for window in top for child in window.descendants(control_type='Window')]
        return top + nested

    try:
        main = wait_for(lambda: next((w for w in windows() if w.window_text() == expected), None))
        record['actual_title'] = main.window_text()
        if workbench:
            desktop.window(handle=main.handle).child_window(title='离线工作台', control_type='Button').invoke()
            time.sleep(1)
            print('Owned windows:', [w.window_text() for w in windows()], flush=True)
            dialog = wait_for(lambda: next((w for w in windows() if w.window_text() == '构型与平顺轨迹工作台 · 离线'), None))
            spec = desktop.window(handle=dialog.handle)
            spec.child_window(title='平顺轨迹预览', control_type='TabItem').select()
            spec.child_window(title='载入离线示例', control_type='Button').invoke()
            spec.child_window(title='生成平顺轨迹', control_type='Button').invoke()
            export = spec.child_window(title='导出参考 JSON / CSV', control_type='Button')
            wait_for(lambda: export.is_enabled())
            record['trajectory_generated'] = True
            record['visible_text'] = [w.window_text() for w in dialog.descendants()
                                      if w.window_text() and w.element_info.control_type in ('Text', 'Edit')]
            screenshot = folder/'workbench_exe_v1_06.png'
            dialog.capture_as_image().save(screenshot)
            record['screenshot'] = str(screenshot)
            win32gui.PostMessage(dialog.handle, win32con.WM_CLOSE, 0, 0)
            wait_for(lambda: not win32gui.IsWindow(dialog.handle))
        win32gui.PostMessage(main.handle, win32con.WM_CLOSE, 0, 0)
        process.wait(timeout=20)
        record['exit_code'] = process.returncode
        record['normal_wm_close'] = True
    finally:
        survivors = []
        for pid, created in owned.items():
            try:
                item = psutil.Process(pid)
                if item.create_time() == created and item.is_running():
                    survivors.append(item)
            except psutil.NoSuchProcess:
                pass
        record['forced_cleanup_pids'] = [item.pid for item in survivors]
        for item in survivors:
            item.terminate()
        psutil.wait_procs(survivors, timeout=5)
        print(json.dumps(record, ensure_ascii=False), flush=True)
    if record['forced_cleanup_pids']:
        raise RuntimeError('测试进程需要强制清理，不能视为正常退出')
    return record


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, default=Path(__file__).resolve().parents[1]/'dist/unitree_s288_microduck_joint_ui_v1_06.exe')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parents[1]/'build'
    folder.mkdir(exist_ok=True)
    records = [check(args.exe.resolve(), folder, workbench=True),
               check(args.exe.resolve(), folder, title='原生离线验收_v1_06')]
    (folder/'smoke_workbench_exe_v1_06.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
