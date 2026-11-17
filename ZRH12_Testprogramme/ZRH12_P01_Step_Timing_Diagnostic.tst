'    ZRH12 WINTERTHUR - ENERIA CAT 3516, 3.5 MVA / approx 2800 kW at 0.8 pf
'    Aggreko orders A766406 (54 x 200 kW) and A766407 (6 MVA)
'    P01 - SIGMA STEP TIMING DIAGNOSTIC, Rev 1
'    Aggreko / Mobil in Time AG - B. Uecoez
'
'    PURPOSE
'      Measure the real step execution time of the load bank and separate the two
'      candidate causes of the ramp overrun recorded on 16 November 2026.
'
'    BACKGROUND
'      In that run a single load step with a 17 s delay ran in 17.008 s, while a
'      section of 30 steps with 1 s delays ran in 46.931 s against a programmed 30 s.
'      The excess is 0.56 to 0.62 s per step, constant and independent of step size.
'
'    CANDIDATE A - timed load step limit
'      Sigma automatic load control is documented as providing up to 16 timed load
'      steps. Above that the controller may fetch step by step instead of running
'      from its internal sequence buffer.
'
'    CANDIDATE B - control bus
'      The master issues each step serially to the units and waits for switching
'      acknowledgement before the delay timer starts.
'
'    HOW TO READ THE RESULT
'      All three blocks cover the identical 187 to 1500 kW span.
'      Step execution time = delay + a fixed overhead. Read the overhead as
'        overhead = (measured block time - sum of delays) / number of steps
'
'      Block A, 12 steps, 11 delays of 1 s, below the 16 step figure:
'        about 11 to 12 s -> no overhead, candidate A, the step limit
'        about 18 to 19 s -> overhead 0.6 s, candidate B, the control bus
'      Block B, 24 steps, 23 delays of 1 s, above the figure:
'        about 23 s       -> no overhead
'        about 38 s       -> overhead 0.6 s
'        An overhead per step that is LARGER in block B than in block A confirms
'        candidate A. An identical overhead in both blocks confirms candidate B.
'      Block C, 12 steps, zero delay, measures the floor directly:
'        block time divided by 12 is the bare overhead per step.
'
'      Cursor placement, both cursors on a stable plateau:
'        cursor 1 on the LAST sample of the 187 kW plateau, that is immediately
'                 before the first step of the block,
'        cursor 2 on the FIRST sample of the 1500 kW plateau.
'      Do not place a cursor on a rising edge and do not include the 10 s hold at
'      187 kW in the reading.
'      Sigma PC also shows elapsed time since the last load was applied in
'      its status line, which is a second independent reading.
'    Expected total run time: 5 min 08 s
'
Capture  On
Section  Heatrun
Instrumentation  Full
'
'    SECTION 0 - defined start state
'      Fans running, zero load, 30 s settle before the first step.
'      Confirm bank temperature state and record it in the test sheet.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:00:30
'
'    SECTION 1 - BLOCK A - 12 steps, below the 16 step figure, 1 s delay
'      Decisive block. 12 s points to the step limit, 19 s to the control bus.
'      Span 187 to 1500 kW, identical in all three blocks.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:10
Load  296kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  406kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  515kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  625kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  734kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  844kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  953kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1062kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1172kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1281kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1391kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1500kw 1cosÿ 00:00:00 No
Delay  00:00:20
Load  0kw 1cosÿ 00:00:00 No
Delay  00:00:30
'
'    SECTION 2 - BLOCK B - 24 steps, above the 16 step figure, 1 s delay
'      Twice the step count of block A over the identical load span.
'      Span 187 to 1500 kW, identical in all three blocks.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:10
Load  242kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  296kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  351kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  406kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  461kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  515kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  570kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  625kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  679kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  734kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  789kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  844kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  898kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  953kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1008kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1062kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1117kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1172kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1226kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1281kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1336kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1391kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1445kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1500kw 1cosÿ 00:00:00 No
Delay  00:00:20
Load  0kw 1cosÿ 00:00:00 No
Delay  00:00:30
'
'    SECTION 3 - BLOCK C - 12 steps, zero delay, floor measurement
'      If Delay 00:00:00 is rejected by the compiler, delete this block and run the rest.
'      Span 187 to 1500 kW, identical in all three blocks.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:10
Load  296kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  406kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  515kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  625kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  734kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  844kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  953kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  1062kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  1172kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  1281kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  1391kw 1cosÿ 00:00:00 No
Delay  00:00:00
Load  1500kw 1cosÿ 00:00:00 No
Delay  00:00:20
'
'    SECTION 4 - cool-down
'      Zero load with fans running for 60 s before shutdown, so the
'      elements are not left hot with the fans stopped.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:01:00
Reject
Capture  Off
