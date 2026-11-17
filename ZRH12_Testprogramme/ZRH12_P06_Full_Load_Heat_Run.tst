'    ZRH12 WINTERTHUR - ENERIA CAT 3516, 3.5 MVA / approx 2800 kW at 0.8 pf
'    Aggreko orders A766406 (54 x 200 kW) and A766407 (6 MVA)
'    P06 - FULL LOAD HEAT RUN, Rev 1
'    Aggreko / Mobil in Time AG - B. Uecoez
'
'    PURPOSE
'      Sustained graduated load run to prove cooling capacity, fuel delivery, exhaust
'      temperature and continuous output, and to prevent wet stacking.
'
'    PROFILE
'      25 percent /  687.5 kW / 30 min
'      50 percent / 1375   kW / 30 min
'      75 percent / 2062.5 kW / 30 min
'     100 percent / 2750   kW / 60 min
'      Total on load 2 h 30 min, total programme approximately 2 h 45 min.
'      The graduated sequence is not optional and the 25 and 50 percent blocks are
'      not to be skipped to save time.
'
'    HOLD TIMES
'      These are the commonly applied durations. Check them against the project
'      specification before the run and adjust if the specification differs.
'
'    WHAT TO RECORD IN EACH BLOCK
'      At block start, mid block and block end: kW, kVA, power factor, voltage and
'      current per phase, frequency, coolant and exhaust temperature, oil pressure,
'      fuel level. Ambient temperature at the start and end of the run.
'
'    FUEL
'      At 2750 kW the run consumes a significant volume. Confirm tank level before
'      starting and check it against the contractual fuel allowance. Refuelling is
'      through the tank only, never directly from the tanker into the generator.
'
'    THERMAL NOTE
'      The first minutes of each block read high because the elements are still
'      coming up to temperature. Take the block value at the END of the block, not
'      at the start. P04 quantifies this effect.
'    Expected total run time: 157 min 10 s
'
Capture  On
Section  Heatrun
Instrumentation  Full
'
'    SECTION 0 - defined start state
'      Fans running, zero load, 60 s settle before the first step.
'      Confirm bank temperature state and record it in the test sheet.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:01:00
'
'    SECTION 1 - 25 percent block, 687.5 kW, 30 min
'      Ramp in over 8 steps, then hold. Take the block reading at the END.
Load  187kw 1cosÿ 00:00:00 No
Delay  00:00:10
Load  250kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  312kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  375kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  437kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  500kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  562kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  625kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  687.5kw 1cosÿ 00:00:00 No
Delay  00:30:00
'
'    SECTION 2 - 50 percent block, 1375 kW, 30 min
'      Ramp in over 8 steps, then hold. Take the block reading at the END.
Load  773kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  859kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  945kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1031kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1117kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1203kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1289kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1375kw 1cosÿ 00:00:00 No
Delay  00:30:00
'
'    SECTION 3 - 75 percent block, 2062.5 kW, 30 min
'      Ramp in over 8 steps, then hold. Take the block reading at the END.
Load  1461kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1547kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1633kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1719kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1805kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1891kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  1977kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2062.5kw 1cosÿ 00:00:00 No
Delay  00:30:00
'
'    SECTION 4 - 100 percent block, 2750 kW, 60 min
'      Ramp in over 8 steps, then hold. Take the block reading at the END.
Load  2148kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2234kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2320kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2406kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2492kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2578kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2664kw 1cosÿ 00:00:00 No
Delay  00:00:01
Load  2750kw 1cosÿ 00:00:00 No
Delay  01:00:00
'
'    SECTION 5 - controlled return to zero
Load  2000kw 1cosÿ 00:00:00 No
Delay  00:00:02
Load  1400kw 1cosÿ 00:00:00 No
Delay  00:00:02
Load  800kw 1cosÿ 00:00:00 No
Delay  00:00:02
Load  300kw 1cosÿ 00:00:00 No
Delay  00:00:02
'
'    SECTION 6 - cool-down
'      Zero load with fans running for 300 s before shutdown, so the
'      elements are not left hot with the fans stopped.
Load  0kw 1cosÿ 00:00:00 No
Delay  00:05:00
Reject
Capture  Off
