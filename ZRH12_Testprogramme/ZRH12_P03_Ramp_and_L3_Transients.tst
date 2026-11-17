'    ZRH12 WINTERTHUR - ENERIA CAT 3516, 3.5 MVA / approx 2800 kW at 0.8 pf
'    Aggreko orders A766406 (54 x 200 kW) and A766407 (6 MVA)
'    P03 - RAMP AND L3 STEP TRANSIENTS, Rev D
'    Aggreko / Mobil in Time AG - B. Uecoez
'
'    PURPOSE
'      The full test run: specified ramp, main plateau, L3 step transients and a
'      thermal reference step. Replaces ZRH12 ASTON RAMP 30s 2700kW SK RevA.
'
'    CHANGES AGAINST RevA
'      1. Ramp section rebuilt from 30 steps to 16 steps of about 132 kW. Measured
'         execution time is 1.62 s, so 30 steps take 46.9 s whatever the delay says.
'         16 steps also stay within the documented 16 timed load step limit.
'      2. Measuring plateau added at 2298 kW. This is the specified ramp end point
'         and now carries a stable 60 s plateau instead of being passed through.
'      3. Main plateau extended from 45 s to 180 s, so the thermal drift of the
'         elements becomes visible inside the plateau instead of being mistaken for
'         a generator deviation.
'      4. Thermal reference step added in section 7. Same 2721 kW set point with the
'         bank fully warm. The difference against the section 4 reading at 0 s is the
'         measured temperature coefficient of this run, not an estimate.
'      5. Defined start state and fan run-on cool-down added.
'      6. L3 transient block: set points, sequence and hold times UNCHANGED.
'         The execution is improved, the test substance is not touched.
'
'    WHY THE THERMAL REFERENCE MATTERS
'      On 10 November on GEN-1C the generator read 2.4 to 3.4 percent above the load
'      bank set point across four ramps. On 9 November on GEN-1A the first cold
'      plateau read 2926 kW against 2804 kW on a later warm plateau of the same run,
'      a 4.2 percent difference. Resistive elements have a positive temperature
'      coefficient, so a cold bank draws more power at the same set point.
'      Cable losses account for roughly 1 percent of the offset at these lengths.
'      Section 7 turns the remainder from an argument into a recorded number.
'    Expected total run time: 16 min 59 s
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
'      Single step, 17 s. Unchanged from RevA, which ran it to 17.008 s.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:17
'
'    SECTION 2 - specified ramp 187 to 2298 kW
'      16 steps, 15 of 132 kW and one of 131 kW, to land exactly on 2298 kW.
'      Steps 2, 5, 8, 11, 14 carry a 2 s delay, five in total.
'      Expected 29.9 s against the required 30 s.
'      Cursor 1 on the LAST sample of the 187 kW plateau, cursor 2 on the FIRST
'      sample of the 2298 kW plateau. The 17 s hold in section 1 is settling time
'      and is not part of the ramp. Placing cursor 1 at the start of that plateau
'      makes the reading 17 s too long.
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
'      The 16th step carries the 60 s measuring plateau directly. No repeated
'      switching command lands on 2298 kW, which would otherwise shift the
'      plateau start by one step time and falsify the ramp reading.
'
'    SECTION 3 - continue to 2721 kW
'      4 steps of 106 kW, unchanged from RevA.
Load  2404kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2510kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2616kw 1cosÿ 00:00:00 No
Delay  00:00:01
'
'    SECTION 4 - main plateau 2721 kW, 180 s
'      Record power at 0 s and at 180 s. The fall between the two readings is
'      the element temperature coefficient, not a generator deviation.
'      RevA held only 45 s and hid this effect.
Load  2721kw 1cosÿ 00:00:00 No
Delay  00:03:00
'
'    SECTION 5 - controlled return to zero
'      Unchanged from RevA.
Load  2500kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2400kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2300kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2200kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2100kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2000kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1800kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1600kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1400kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1200kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1000kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  800kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  500kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  200kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  0kw 1cosÿ 00:00:00 No
Delay  00:00:30
'
'    SECTION 6 - L3 step transients
'      Set points, sequence and hold times unchanged from RevA.
'      687.5 / 1375 / 2062.5 / 2750 kW = 25 / 50 / 75 / 100 percent of 2750 kW.
Load  687.5kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  0kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  1375kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  2750kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  1375kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  0kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  687.5kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  2062.5kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  687.5kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  0kw 1cosÿ 00:00:00 No
Delay  00:00:30
Load  2750kw 1cosÿ 00:00:00 No
Delay  00:01:00
Load  0kw 1cosÿ 00:00:00 No
Delay  00:00:30
'
'    SECTION 7 - thermal reference step
'      Same 2721 kW as section 4, bank now fully warm after the transient block.
'      Difference against the section 4 reading at 0 s is the full temperature
'      coefficient of this run, measured on the same bank with the same cabling.
Load  1000kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2000kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2721kw 1cosÿ 00:00:00 No
Delay  00:01:00
'
'    SECTION 8 - cool-down
'      Zero load with fans running for 180 s before shutdown, so the
'      elements are not left hot with the fans stopped.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:03:00
Reject
Capture  Off
