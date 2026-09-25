// macOS helper for PocketTopo under Wine. See ../POCKETTOPO_MACOS.md.
// Lists the selected process's windows or posts a global click within its window bounds.
// The caller must visually verify that the click point is unobscured.
import AppKit
import CoreGraphics
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data(("pockettopo-ui: " + message + "\n").utf8))
    exit(1)
}

func visibleWindows(of pid: pid_t) -> [[String: Any]] {
    guard let windows = CGWindowListCopyWindowInfo(
        [.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID
    ) as? [[String: Any]] else {
        fail("cannot read the window list")
    }
    return windows.filter { ($0[kCGWindowOwnerPID as String] as? Int) == Int(pid) }
}

func requireFrontmost(_ pid: pid_t) {
    guard NSWorkspace.shared.frontmostApplication?.processIdentifier == pid else {
        fail("target PID \(pid) is not the active application; no click sent")
    }
}

let args = CommandLine.arguments
guard args.count >= 3, let pid = Int32(args[2]), pid > 0 else {
    fail("usage: pockettopo-ui windows PID | click PID X Y")
}
guard NSRunningApplication(processIdentifier: pid) != nil else {
    fail("PID \(pid) is not a running macOS application")
}

switch args[1] {
case "windows":
    guard args.count == 3 else { fail("usage: pockettopo-ui windows PID") }
    for window in visibleWindows(of: pid) {
        do {
            let data = try JSONSerialization.data(withJSONObject: window, options: [.sortedKeys])
            FileHandle.standardOutput.write(data)
            FileHandle.standardOutput.write(Data([10]))
        } catch {
            fail("cannot serialize window information: \(error)")
        }
    }
case "click":
    guard args.count == 5,
          let x = Double(args[3]), let y = Double(args[4]), x.isFinite, y.isFinite else {
        fail("usage: pockettopo-ui click PID X Y (finite screen coordinates)")
    }
    requireFrontmost(pid)
    guard CGPreflightPostEventAccess() else {
        fail("macOS has not granted access to post input events")
    }
    let point = CGPoint(x: x, y: y)
    let insideTargetWindow = visibleWindows(of: pid).contains { window in
        guard let bounds = window[kCGWindowBounds as String] as? [String: Any],
              let rect = CGRect(dictionaryRepresentation: bounds as CFDictionary) else {
            return false
        }
        return rect.contains(point)
    }
    guard insideTargetWindow else {
        fail("point is outside the target process's visible windows; no click sent")
    }
    guard let move = CGEvent(
        mouseEventSource: nil, mouseType: .mouseMoved,
        mouseCursorPosition: point, mouseButton: .left
    ), let down = CGEvent(
        mouseEventSource: nil, mouseType: .leftMouseDown,
        mouseCursorPosition: point, mouseButton: .left
    ), let up = CGEvent(
        mouseEventSource: nil, mouseType: .leftMouseUp,
        mouseCursorPosition: point, mouseButton: .left
    ) else {
        fail("cannot create mouse events")
    }
    down.setIntegerValueField(.mouseEventClickState, value: 1)
    up.setIntegerValueField(.mouseEventClickState, value: 1)
    requireFrontmost(pid)
    move.post(tap: .cghidEventTap)
    Thread.sleep(forTimeInterval: 0.05)
    requireFrontmost(pid)
    down.post(tap: .cghidEventTap)
    Thread.sleep(forTimeInterval: 0.05)
    // Always release a button we pressed, even if focus changes after mouse-down.
    up.post(tap: .cghidEventTap)
    print("Click sent to screen point \(x), \(y); inspect the result before continuing.")
default:
    fail("unknown command; use windows or click")
}
