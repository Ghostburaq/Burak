'    ZRH12 WINTERTHUR - ENERIA CAT 3516, 3.5 MVA / approx 2800 kW at 0.8 pf
'    Aggreko orders A766406 (54 x 200 kW) and A766407 (6 MVA)
'    P02 - COLD START RAMP ACCEPTANCE, Rev D
'    Aggreko / Mobil in Time AG - B. Uecoez
'
'    PURPOSE
'      The contractual ramp of the cold start acceptance test, run on its own so the
'      ramp time can be read from two stable plateaus instead of estimated from a
'      rising edge.
'
'    REQUIREMENT
'      187 to 2298 kW in 30 s = 70.4 kW/s
'      Expected with 16 steps of about 132 kW: 29.9 s = 70.6 kW/s
'
'    WHY 16 STEPS AND NOT 30
'      Measured step execution time is 1.62 s, not the programmed 1.00 s. 30 steps
'      therefore take 46.9 s whatever the delay says. 16 steps deliver the
'      same 2111 kW inside the window and stay within the documented limit of 16
'      timed load steps. Five delays are set to 2 s to land on 30 s rather than 25 s.
'
'    MARGIN CHECK BEFORE THE ACCEPTANCE RUN
'      Ramp time = 16 x overhead + 15 s + n, where n is the number of 2 s delays.
'      This file is set to n = 5, which gives 29.9 s at an overhead of 0.62 s.
'      That is only 0.1 s inside the 30 s requirement, so confirm the overhead
'      with P01 first and set n from the measured value:
'        overhead up to 0.62 s   -> n = 5, ramp 29.0 to 29.9 s
'        overhead 0.63 to 0.68 s -> n = 4, ramp 29.1 to 29.9 s
'        overhead 0.69 to 0.74 s -> n = 3, ramp 29.0 to 29.8 s
'        overhead 0.75 to 0.80 s -> n = 2, ramp 29.0 to 29.8 s
'      Take the 2 s delays out from the end of the ramp first, that is step 14,
'      then 11, then 8, so the early part of the ramp stays unchanged.
'
'    LOAD STEP SIZE
'      132 kW is 4.8 percent of the 2750 kW reference. The transient block of the
'      customer programme already applies 2750 kW in a single step, so there is no
'      load acceptance concern at this step size.
'
'    MEASURING INSTRUCTION
'      Cursor 1 on the LAST sample of the 187 kW plateau in section 1, that is
'      immediately before the first ramp step. Cursor 2 on the FIRST sample of the
'      2298 kW plateau at the end of section 2.
'      Both are stable plateaus, so the reading does not depend on cursor placement
'      on a rising edge.
'      The 17 s hold at 187 kW is settling time, not part of the ramp. If cursor 1
'      is placed at the START of that plateau the reading comes out 17 s too long
'      and the ramp appears to fail when it does not.
'
'    PRECONDITION
'      Cold start refers to the generator, not to the load bank. If the bank is cold
'      the first plateau reads high by roughly 4 percent through the temperature
'      coefficient of the elements. Record the bank state in the test sheet and use
'      P04 to quantify it.
'    Expected total run time: 4 min 25 s
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
'    SECTION 1 - base step
'      Single step with a 17 s delay. This section ran to 17.008 s in RevA
'      and is unchanged, so the two revisions stay directly comparable.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:17
'
'    SECTION 2 - specified ramp 187 to 2298 kW
'      16 steps, 15 of 132 kW and one of 131 kW, to land exactly on 2298 kW.
'      Steps 2, 5, 8, 11, 14 carry a 2 s delay, five in total.
'      Expected 29.9 s against the required 30 s. The 2298 kW plateau starts
'      with the 16th step, so cursor 2 goes on the start of that plateau.
Load  319kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  451kw 1cosÿ 00:00:00 No
Delay  00:00:02
Load  583kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  715kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  847kw 1cosÿ 00:00:00 No
Delay  00:00:02
Load  979kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1111kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1242kw 1cosÿ 00:00:00 No
Delay  00:00:02
Load  1374kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1506kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1638kw 1cosÿ 00:00:00 No
Delay  00:00:02
Load  1770kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1902kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2034kw 1cosÿ 00:00:00 No
Delay  00:00:02
Load  2166kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2298kw 1cosÿ 00:00:00 No
Delay  00:01:00
'      The final step carries the 60 s hold directly, so no second switching
'      command lands on 2298 kW. A repeated command on the same value costs one
'      step time and would shift the plateau start, falsifying the ramp reading.
'
'    SECTION 3 - controlled return to zero
Load  1800kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1200kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  700kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  200kw 1cosÿ 00:00:00 No
Delay  00:00:01
'
'    SECTION 4 - cool-down
'      Zero load with fans running for 120 s before shutdown, so the
'      elements are not left hot with the fans stopped.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:02:00
Reject
Capture  Off
