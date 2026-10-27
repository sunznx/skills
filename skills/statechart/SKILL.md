---
name: statechart
description: "Check a TLA+ model of a system that moves between states, such as a product flow, a protocol, or a service, and draw it as a Mermaid statechart. The report gives the shortest path to each state that breaks a rule. Use for /statechart, or to show a bug as a path through states."
---

# Statechart

The chart shows how a system moves between states, in the words of the person who reads it. That person, the reader, decides whether the behavior is right.

## Plan and page

Before the first run, use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow invokes this skill, use that workflow's selected plan. Keep its absolute directory.

Give each system you chart its own run folder, `<PLAN_DIR>/statechart/<system>/`, named in kebab case, as in `checkout-payment`. Reruns of the same model stay in its folder; never reuse a folder for another system.

- The spec, its config, and the view module sit at the top of the run folder.
- Each run writes to the next numbered folder, `out-1/`, `out-2/`, and so on, because the command writes only to a new or empty folder. Pass `--out <PLAN_DIR>/statechart/<system>/out-<n>`. Render each SVG next to its `.mmd` file in that folder, as `references/render.md` says.
- `statechart-<system>.html` sits beside the `out-<n>/` folders. It is the page for the person who must decide.

Build the page from the latest `out-<n>/`, and rebuild it after each rerun. It carries everything that [Hand off](#hand-off) lists:

- Open with one line that says which rules hold and which break, with counts from that run's `report.md`.
- Show `chart.svg` with a legend of the group colors and marks that it uses. When the run wrote no `chart.mmd`, say why.
- Give each bug its own section: the rule, the reader's sentence for that rule, and the path as the report numbers it.
- Put the Mermaid text in a collapsed block under the chart.
- Link `report.md`, `tlc.out`, and each `tlc-RULE.out`. Show the command that makes the files again, with the next `out-<n>` folder.
- Reference files by relative path, as in `out-2/chart.svg`. Use inline CSS. The page works on desktop and mobile, in light and dark mode.

Record the run folder, the page path, and the one-line verdict in the selected plan's `findings.md` and `progress.md`, then open the page:

```
Bash(open "<PLAN_DIR>/statechart/<system>/statechart-<system>.html")
```

## Run

Work in the run folder that [Plan and page](#plan-and-page) names. Write a TLA+ spec and its config there. Then run:

```sh
<skill dir>/scripts/statechart SPEC.tla [--config FILE] [--view FILE] [--out DIR]
```

`scripts/statechart.ts` is TypeScript, so run it with a runtime that can execute TypeScript.

The first run installs TLC and Java with mise and needs the network.

## Write the spec

- Write each rule that the reader agrees to as an INVARIANT. A rule can be about a screen, a result, a stored value, or a message. If the model has no variable for a rule, add the variable. Never weaken a rule to make it hold.
- Write `Next` as a disjunction of the actions, such as `YouPressPlay \/ YouPressStop`. If you do not, TLC names every step `Next`.
- A state with no step out breaks `NoDeadlock`, also when it is a correct end state. When an INVARIANT or a PROPERTY already has that name, the rule is `CHECK_DEADLOCK`. Add to `Next` an action that is true only in the end states and changes nothing, such as `Done == phase \in {"paid", "failed"} /\ UNCHANGED vars`, and give it a label in `step()`.

## Pick the chart

You do the work that needs judgment: the words on each state and arrow, the phases and their colors, the title, and the report to the reader. Put your work in a view module, and give it with `--view`.

To show the reader's words, the view exports `state(vars)`. The value that `state()` returns picks the form:

- A string gives a flat chart: `export const state = (v) => (v.paid ? "Paid" : "Paying");`
- An array gives parent states: `export const state = (v) => v.main.split(".");`
- An object gives one parallel region for each key: `export const state = (v) => ({ Playback: v.playback, Volume: v.volume });`

Label each state with what the reader can see or cares about, such as "Paying" or "Lease held, write pending". Keep variable names out of labels. In `vars`, a TLA+ sequence is an object with keys from 1, so `v.pc[1]` is `pc[1]`. A set is an array.

The view can also export `step(action, from, to)`. It gets the TLC action name and the values before and after the step, and it returns the label of the arrow. Write each step label as the user sees it happen, such as "you press play" or "the connect fails". Do not name the code or the TLA+ action. Two actions that end the same in the chart get the same label, so that they share one arrow.

When a step can occur only in some conditions, end its label with the condition in brackets, in the reader's words, such as `you press play [while the file loads]`. In a regions chart, the command writes the condition on the other regions on the arrow, in the words of their labels, such as `[when Offline]`. Your brackets replace it, and two arrows from one state can then look the same. So in a regions chart, do not write brackets for a condition on another region. When a value that no label shows decides where a step goes, name the result in the label, such as "the roster read fails".

The view can also export these:

- `group(vars)` returns the name of a phase. Each chart state gets the color of its group. When the model states behind one chart state are in different groups, that state gets no color.
- `colors` gives each group name a color class.
- `title` is a string that the chart shows at the top.

The command calls `state()` and `group()` at most once for each model state, and `step()` at most once for each step. The chart and the report both use those answers. So make each function depend only on its arguments.

The chart does not draw a step that stays in one label. Split a label when the reader must see such a step.

Aim for about 20 arrows or fewer, because a busier chart is hard to read. First return coarser labels from `state()`. Give one label to values that act the same, and leave out a detail that the reader does not need, such as a call in flight whose return changes nothing. Keep each state of a bug path, and keep each mark. When a merge changes a `breaks` state to `mayBreak`, it hides where a rule breaks. Do not merge two states that break different rules, because the reader then cannot see which rule breaks where. If the chart is still too busy, return `null` from `step()` for the steps that the reader does not need, such as a reset that every state has, or a step whose arrow repeats what other arrows show. Obey these rules when you hide steps:

- Keep each chart state reachable by arrows from a start state.
- Keep at least one arrow out of each chart state that has a step out in the model.
- Hide all the steps of an arrow, or none of them. When you hide only some, its condition gets narrower.
- In the hand-off, say which steps the chart hides.

## Read the report

- In the chart, a state that breaks a rule has the class `breaks`. When only some model states behind it break the rule, it has the class `mayBreak`. The Legend names the rules of each mark. When two rules break, it names both on one mark, so say in the hand-off which state breaks which rule. In a regions chart, a state gets a mark when each combination of region states that includes it can break a rule. When a combination can break a rule and none of its states has a mark, each state in that combination gets a mark.
- TLC goes past a state that breaks a rule, so the chart shows the states after a bug.
- Because TLC goes past bugs, a model with no limit on its states can run without end. Keep the constants small, or add a CONSTRAINT.
- With a VIEW or a SYMMETRY, TLC counts states that it treats as the same as one state, and the chart draws that one state. An arrow can lead to it rather than to the state that the step reaches, and the report says so.
- TLC checks the rules in each state past a CONSTRAINT or an ACTION_CONSTRAINT, but it does not explore that state or check it for deadlock. When TLC's shortest path for a rule ends in such a state, the chart draws that state, and the report gives that path. The chart does not draw the other states past the bound. A deadlock in such a state does not show. TLC also checks the rules after each step that an ACTION_CONSTRAINT excludes, also when it reaches the next state another way. When TLC's shortest path for a rule ends with such a step, the chart draws that step.
- The command checks the rules with TLC on the config as written, with one worker. When a rule breaks, the command removes that rule and runs TLC again, until no rule breaks. After the first break, each run stops at 100,000 distinct states, so that a large model does not run without end. When a run reaches that bound or stops on an error, the report lists the rules that it did not check under "Rules not checked", and the chart does not mark them. A rule that is not checked can hold or break. To check it, remove the rules that break from the config, or make the model smaller. The bound adds a module that changes TLC's order of the variables, so for a property TLC can find a different counterexample than a run without the bound.
- `tlc.out` is what TLC printed on the config as written. When the chart does not show the bug path of a rule that breaks, `tlc-RULE.out` is what TLC printed for the run that found it. When TLC repeats its first warning, plain TLC prints it twice, but `tlc.out` shows it once, because TLC leaves the second copy out of the output that this command reads. That happens only when Java runs with `-XX:+UseParallelGC`, since otherwise TLC's first warning is its advice to pass that flag, which it prints once.

## Show the chart

Show `chart.mmd` to the user on the page from [Plan and page](#plan-and-page), not as a code block in the reply. The chart has a budget of 500 states, counted by TLC on the config as written. Above that, the chart draws only the paths to the rules that break, and when no rule breaks, the command writes no `chart.mmd`. It still checks each rule, and the report gives the state count and each bug path. To see the whole graph, make the model smaller.

Render each chart to SVG with Pele, as `references/render.md` says, so that the page can show it. Do not use a different renderer unless the user asks for it.

## Hand off

Give each chart and its Mermaid text to the person who must decide. Add one line for each bug: the rule, the reader's sentence for that rule, and the path as the report numbers it. Say what the model leaves out. Give the command that makes the files again, with a new `--out` folder.

When the model describes code, replay each bug path against the real code, as a test or a live repro, one step for each action. If a bug does not occur, think that the model is wrong until you show that it is not.

Hand all of this off as the page from [Plan and page](#plan-and-page), and give its absolute path.
