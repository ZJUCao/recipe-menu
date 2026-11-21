---
troy-doc: "ADR-0013"
lang: "en"
version: "1.0"
updated: "2026-11-21"
status: "Approved by Troy on 2026-11-21"
mirror: "ADR-0013-edit-starts-the-editor.zh-CN.md"
---

# ADR-0013: edit starts the editor that the settings name

## 1. Status

Accepted. Troy accepted the decision on 2026-11-21, as option 1 of point C of the F16 design.

## 2. Context

`recipe-menu edit ID` opens the recipe's file in the editor that the settings name, Notepad by default, waits until you close the editor, and then checks that recipe (requirements 4, F16). So the tool must start another program and wait for it. ADR-0001 already names `subprocess` for the editor in v0.2.

Architecture 4 says that only `cli` touches the outside world, and architecture 8 lists what only `cli` reads, the environment variables among them. `cli` passes them on through `Context` and the parameters of `main`, so tests give fixed values (ADR-0003). Neither section names starting another program.

Starting the editor touches the outside world in three ways that architecture 4 and 8 keep for `cli`:

- To find the editor, `shutil.which` reads `PATH`, and on Windows `PATHEXT` and `NoDefaultCurrentDirectoryInExePath`, from the environment of the process. On Windows it looks in the current folder first unless that last variable is set.
- The editor gets the environment, the current folder, and the console of `recipe-menu`, as when you type its name in PowerShell.
- So `main(environ={})`, which keeps every other command away from the environment of the process, does not keep `edit` from the `PATH` and the current folder of the process.

On Windows, Python's wait for a process does not wake for Ctrl+C, so a plain wait would hold Ctrl+C until the editor ends.

## 3. Decision

- `edit` finds the program, the first word of the setting `editor`, with `shutil.which`. It starts `[found, *options, full path of the recipe's file]` with `subprocess.Popen`, with no shell, no `env`, no `cwd`, and no streams, and waits for it with `Popen.wait(timeout=0.5)` in a loop (F16 design, choices 4 and 5).
- Only `edit` starts a program, and only the editor that the settings name. No other module starts a program or calls `shutil.which`. Architecture 4 and 8 name this one exception to the rule that only `cli` touches the outside world.
- `edit` imports `subprocess` and `shutil` only inside the function that starts the editor, and calls them as `subprocess.Popen` and `shutil.which`, so no other command loads them, and a test can replace either through `monkeypatch`.
- An editor that cannot be found, cannot start, or ends with an exit code other than 0 is not an error in the data. `edit` writes one line to the error stream and gives 1. It catches only the `OSError` of `Popen`, and the `subprocess.TimeoutExpired` of its steps of waiting, which only means that the editor still runs. Ctrl+C while it waits goes on to `cli`, which gives 130, and the editor is left running. Architecture 6 has a row for this.
- No test starts a real editor. A test that runs `edit` sets the `PATH` that `edit` searches, and lets it find only a stand-in editor, which opens no window (architecture 10).
- The tool still never uses the network. The editor is a program of your choice and not part of the tool, so it may use the network, as VS Code does.

## 4. Options considered

| Option | Pros | Cons |
| --- | --- | --- |
| Option 1: `edit` starts the editor itself with `subprocess.Popen`, after `shutil.which` finds it on the `PATH`, and the editor gets the environment, the current folder, and the console of `recipe-menu`. Chosen. | One command starts one program that the requirement names, so one narrow rule covers it. `Context` and `main` keep their fields and parameters, so F15-T03 holds and no test-fix PR comes before the mock PR. `app` gets no interface that starts a program. The editor starts as when you type its name in PowerShell, so `code` finds `code.cmd`. | Architecture 4 and 8 gain an exception, and `main(environ={})` no longer keeps `edit` from the `PATH` and the current folder of the process. Two drawbacks that the design did not list: every test that runs `edit` needs a guard of its `PATH` and current folder, because on Troy's PC a test without the key `editor` and without the guard would start the real Notepad and wait until someone closes it. And each test run of `edit` starts a real process, a stand-in in Python, so those tests take longer than tests that stay in the process. |
| Option 2: `cli` starts programs for the commands. `Context` gets a new field, a function that starts a program and waits for it, which `main` fills, and which a test replaces with a stand-in in the process. `edit` calls it. | The rule of architecture 8 stays whole: `main` would search the `PATH` of its `environ`, so `main(environ={})` would keep every command away from the environment of the process. The tests of `edit` would start no process. Only the test of the starter in `cli` would. | A field that one command uses goes into the context of every command, and an interface that starts a program goes into `app`. F15-T03, which compares the names of the fields of `Context`, changes in a test-fix PR before the mock PR, and the `Context` row of architecture 5.2 changes. Choices 4, 5, 9, and 10, section 3, and the examples of the design change before the mock PR. It still needs an ADR, for architecture 5.2 and 8, and the test of the real start still needs a stand-in. |

## 5. Consequences

- Architecture 4 and 8 name the rule in version 5.2. Architecture 6 gains the row of a program that a command starts, and architecture 10 says that no test starts a real editor. The `Context` row of architecture 5.2 and the parameters of `main` do not change.
- ADR-0003 stays as Troy accepted it. Its rule that only `cli` reads the environment holds for every other module, and for every read of `edit` other than the search for the editor. `subprocess`, `shutil`, and `time` are standard modules (ADR-0001), so R16 has nothing to review.
- The F16 design and test plan stay as Troy approved them in version 1.0. Choices 4, 5, 9, and 10 of the design, and the guard, the stand-in, and the watching and the raising `Popen` of the test plan, already follow option 1. No requirement, prototype, or scenario changes, and no test or code of an earlier feature changes.
- The start of every other command does not load `subprocess` or `shutil`, which keeps about 11 to 15 ms out of it on Troy's PC, as the design review measured. ruff flags `S603` and `PLC0415` on the start of the editor, and each of those lines carries a `noqa` comment with its reason (F16 design, choice 4).
- On Windows, a program of the editor's name in the folder where you run `edit` runs in place of the one on the `PATH`, unless `NoDefaultCurrentDirectoryInExePath` is set. Troy's terminal does not set it.
- A batch editor, such as `code.cmd`, gets its arguments through `cmd.exe`. A data folder path that holds `%`, or that holds `&`, `|`, `<`, `>`, or `^` and no space, reaches it changed, and after `&` the rest of the path can run as a command (the design review, note 6). The design names only `%NAME%`. The ID never holds these characters, the data folder is your own choice, and the default data folder on Troy's PC holds none of them. An `.exe` editor, such as Notepad, gets every argument as written.
- When `Popen` fails, the reason in the message is the system's own text, in the system's language, and on Windows it can hold a literal `%1` (the design review, note 2).
- The rule "No network" of architecture 1 and the rules of architecture 7 are about the tool. What the editor does is its own doing, such as the text of open tabs, saved or not, that Windows 11 Notepad can keep to restore them.
- A later command that wants to start a program, or another module that wants `shutil.which`, needs its own change to architecture 8 with an ADR. The rule change flow can make the rule a lint check with ruff's banned-API rule `TID251`, which would ban `subprocess`, `shutil.which`, `os.system`, `os.startfile`, `os.popen`, and the `os.exec` and `os.spawn` functions everywhere but in `edit`.

## 6. Related

- Features: F05, F15, F16
- Rules: None
