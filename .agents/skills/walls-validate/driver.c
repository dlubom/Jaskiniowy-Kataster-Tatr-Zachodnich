/* Walls v2.3.0-beta.1 only. Native messages, scoped to our child PID.
 * IDs verified against Walls32/resource.h and prjview.cpp at that release tag.
 * Build: cl /W4 driver.c user32.lib /Fe:driver.exe
 * Or: x86_64-w64-mingw32-gcc -O2 -Wall -Wextra driver.c -o driver.exe -luser32
 */
#define _WIN32_WINNT 0x0600
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static DWORD pid;
static HWND main_window, project_list, compile_button, dialog;
static int existing;

static int owned(HWND w) {
    DWORD owner = 0;
    GetWindowThreadProcessId(w, &owner);
    return owner == pid;
}

static BOOL CALLBACK scan_top(HWND w, LPARAM unused) {
    char cls[80] = {0};
    (void)unused;
    GetClassNameA(w, cls, sizeof(cls));
    if (!strcmp(cls, "Walls32Class")) {
        if (!pid) existing = 1;
        else if (owned(w)) main_window = w;
    }
    if (pid && owned(w) && IsWindowVisible(w) && !strcmp(cls, "#32770")) dialog = w;
    return TRUE;
}

static BOOL CALLBACK scan_child(HWND w, LPARAM unused) {
    char cls[80] = {0};
    (void)unused;
    GetClassNameA(w, cls, sizeof(cls));
    if (GetDlgCtrlID(w) == 1 && !strcmp(cls, "ListBox")) project_list = w;
    if (GetDlgCtrlID(w) == 32810 && IsWindowVisible(w)) compile_button = w;
    return TRUE;
}

static BOOL CALLBACK dump_child(HWND w, LPARAM unused) {
    char text[4096] = {0}, cls[80] = {0};
    (void)unused;
    GetClassNameA(w, cls, sizeof(cls));
    GetWindowTextA(w, text, sizeof(text));
    if (text[0]) printf("CONTROL %d %s: %s\n", GetDlgCtrlID(w), cls, text);
    return TRUE;
}

static void dump(HWND w) {
    dump_child(w, 0);
    EnumChildWindows(w, dump_child, 0);
    fflush(stdout);
}

static int message(HWND w, UINT msg, WPARAM wp, LPARAM lp, DWORD_PTR *out) {
    return SendMessageTimeoutA(w, msg, wp, lp, SMTO_ABORTIFHUNG | SMTO_BLOCK, 2000, out) != 0;
}

static int fresh_outputs(const char *base) {
    const char *extensions[] = {"NTA", "NTN", "NTP", "NTS", "NTV"};
    char file[MAX_PATH];
    WIN32_FILE_ATTRIBUTE_DATA data;
    int i;
    for (i = 0; i < 5; ++i) {
        if (snprintf(file, sizeof(file), "%s.%s", base, extensions[i]) >= MAX_PATH) return 0;
        if (!GetFileAttributesExA(file, GetFileExInfoStandard, &data) ||
            !(data.nFileSizeLow || data.nFileSizeHigh)) return 0;
    }
    return 1;
}

int main(int argc, char **argv) {
    STARTUPINFOA si = {0};
    PROCESS_INFORMATION pi = {0};
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits = {0};
    HANDLE job;
    char cmd[2048], title[512] = {0};
    ULONGLONG deadline, stable = 0;
    DWORD_PTR selection;
    DWORD exit_code = 0;
    int sent = 0, result = 30;
    unsigned seconds;
    if (argc != 7 || !(seconds = (unsigned)atoi(argv[4])) || seconds > 1800) {
        fprintf(stderr, "usage: driver Walls32.exe project.wpj output_base timeout duplicates(0/1) build_title\n");
        return 30;
    }
    si.cb = sizeof(si);
    EnumWindows(scan_top, 0);
    if (existing) { puts("INFRA: Walls already open in this Windows session; refusing to touch it"); return 30; }
    if (fresh_outputs(argv[3])) { puts("INFRA: stale output set"); return 30; }
    job = CreateJobObjectA(NULL, NULL);
    limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if (!job || !SetInformationJobObject(job, JobObjectExtendedLimitInformation, &limits, sizeof(limits))) return 30;
    if (snprintf(cmd, sizeof(cmd), "\"%s\" \"%s\"", argv[1], argv[2]) >= (int)sizeof(cmd)) return 30;
    if (!CreateProcessA(argv[1], cmd, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {
        printf("INFRA: CreateProcess error %lu\n", (unsigned long)GetLastError());
        CloseHandle(job); return 30;
    }
    if (!AssignProcessToJobObject(job, pi.hProcess)) {
        puts("INFRA: cannot contain child process");
        TerminateProcess(pi.hProcess, 30);
        CloseHandle(pi.hThread); CloseHandle(pi.hProcess); CloseHandle(job); return 30;
    }
    pid = pi.dwProcessId;
    printf("CHILD_PID %lu DUPLICATES %s\n", (unsigned long)pid, argv[5]);
    ResumeThread(pi.hThread);
    CloseHandle(pi.hThread);
    deadline = GetTickCount64() + (ULONGLONG)seconds * 1000;
    while (GetTickCount64() < deadline) {
        if (WaitForSingleObject(pi.hProcess, 0) == WAIT_OBJECT_0) { puts("INFRA: child exited before completion"); break; }
        main_window = dialog = NULL;
        EnumWindows(scan_top, 0);
        if (dialog) {
            GetWindowTextA(dialog, title, sizeof(title));
            if (!sent && !strcmp(title, "Tip of the Day")) {
                PostMessageA(dialog, WM_COMMAND, IDOK, 0); Sleep(250); continue;
            }
            puts("WALLS_DIALOG"); dump(dialog); result = 20; break;
        }
        if (main_window && IsWindowEnabled(main_window)) {
            GetWindowTextA(main_window, title, sizeof(title));
            if (!strstr(title, argv[6])) { puts("INFRA: unsupported Walls build"); dump(main_window); break; }
            project_list = compile_button = NULL;
            EnumChildWindows(main_window, scan_child, 0);
            if (!sent && project_list && compile_button) {
                if (!message(project_list, LB_SETCURSEL, 0, 0, &selection) || selection != 0 ||
                    !message(GetParent(project_list), WM_COMMAND, MAKEWPARAM(1, LBN_SELCHANGE),
                             (LPARAM)project_list, &selection) ||
                    !message(project_list, LB_GETCURSEL, 0, 0, &selection) || selection != 0) break;
                /* CheckNames defaults FALSE on every new Walls process (Prjdoc.cpp). */
                if (atoi(argv[5])) PostMessageA(main_window, WM_COMMAND, 32817, 0);
                PostMessageA(main_window, WM_COMMAND, 32825, 0);
                puts("RECOMPILE_ROOT"); fflush(stdout); sent = 1;
            } else if (sent && compile_button) {
                GetWindowTextA(compile_button, title, sizeof(title));
                if (!strcmp(title, "&Review") && IsWindowEnabled(compile_button) && fresh_outputs(argv[3])) {
                    if (!stable) stable = GetTickCount64();
                    if (GetTickCount64() - stable >= 1500) { puts("COMPILE_COMPLETE"); dump(main_window); result = 0; break; }
                } else stable = 0;
            }
        }
        Sleep(250);
    }
    if (result == 30) { puts("INFRA: no confirmed compilation before deadline"); if (main_window) dump(main_window); }
    if (result == 0 && main_window) PostMessageA(main_window, WM_CLOSE, 0, 0);
    if (WaitForSingleObject(pi.hProcess, 5000) != WAIT_OBJECT_0) {
        /* Only our child, never an existing user process. Failed dialogs are preserved in stdout. */
        TerminateJobObject(job, 30);
        if (result == 0) { puts("INFRA: Walls did not close normally"); result = 30; }
        WaitForSingleObject(pi.hProcess, 5000);
    }
    if (result == 0 && (!GetExitCodeProcess(pi.hProcess, &exit_code) || exit_code != 0)) {
        printf("INFRA: abnormal Walls exit %lu\n", (unsigned long)exit_code);
        result = 30;
    }
    CloseHandle(pi.hProcess); CloseHandle(job);
    return result;
}
